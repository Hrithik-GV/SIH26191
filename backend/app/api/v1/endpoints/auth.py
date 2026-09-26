"""Authentication API: Secure Login, Token Generation, and User Profile."""

import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Header, status

from backend.app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    ROLE_ADMIN,
    ROLE_AUTHORITY_VIEWER,
)
from backend.app.services.audit_service import AuditService

logger = logging.getLogger("sih26191.auth")

router = APIRouter(prefix="/auth", tags=["Security & Authentication"])

# Standard Pre-Configured Official Accounts (Password for all demo accounts: GovAdmin@2026)
DEFAULT_PASSWORD = "GovAdmin@2026"
DEFAULT_HASH = hash_password(DEFAULT_PASSWORD)

OFFICIAL_USERS_DB = {
    "admin": {
        "id": "usr-admin-01",
        "username": "admin",
        "password_hash": DEFAULT_HASH,
        "name": "Shri K. Harikumar",
        "designation": "Executive Disaster Operations Administrator",
        "role": ROLE_ADMIN,
        "clearance": "LEVEL_1_ADMIN",
        "agency": "District Emergency Operations Centre, Wayanad",
        "station": "DEOC Kalpetta",
    },
    "collector": {
        "id": "usr-collector-02",
        "username": "collector",
        "password_hash": DEFAULT_HASH,
        "name": "Dr. A. K. Nambiar, IAS",
        "designation": "District Collector & Chairman, DDMA Wayanad",
        "role": ROLE_AUTHORITY_VIEWER,
        "clearance": "COMMAND_AUTHORITY",
        "agency": "Kerala State Disaster Management Authority (KSDMA) / NDMA",
        "station": "District Collectorate, Kalpetta",
    },
    "relief_commissioner": {
        "id": "usr-relief-03",
        "username": "relief_commissioner",
        "password_hash": DEFAULT_HASH,
        "name": "Smt. Meera Varma, IAS",
        "designation": "Principal Secretary & State Relief Commissioner",
        "role": ROLE_AUTHORITY_VIEWER,
        "clearance": "STATE_COMMAND",
        "agency": "Revenue & Disaster Management Dept, Govt of Kerala",
        "station": "State EOC, Thiruvananthapuram",
    },
}


class LoginRequest(BaseModel):
    username: str = Field(..., description="Government officer username (e.g., 'admin', 'collector')")
    password: str = Field(..., description="Secure password")


class UserProfileResponse(BaseModel):
    id: str
    username: str
    name: str
    designation: str
    role: str
    clearance: str
    agency: str
    station: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfileResponse


def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    FastAPI dependency validating the incoming Bearer JWT token.
    Raises 401 Unauthorized if invalid or expired.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header with Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Must be 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    user = OFFICIAL_USERS_DB.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists in authority directory.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_role(allowed_roles: list[str]):
    """Role-based authorization guard factory."""
    def dependency(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires one of the following roles: {allowed_roles}. Your role is '{user['role']}'.",
            )
        return user
    return dependency


# Reusable role guards
require_admin = require_role([ROLE_ADMIN])
require_any_authority = require_role([ROLE_ADMIN, ROLE_AUTHORITY_VIEWER])


@router.post("/login", response_model=LoginResponse, summary="Secure Crisis Command Sign-In")
def login(request: LoginRequest):
    """
    Authenticates government authority personnel and issues a cryptographic JWT token.
    Records audit entry upon success or failure.
    """
    user = OFFICIAL_USERS_DB.get(request.username.strip().lower())
    if not user or not verify_password(request.password, user["password_hash"]):
        AuditService.record_action(
            action="LOGIN_FAILED",
            user_id=request.username,
            user_name="Unknown",
            user_role="UNKNOWN",
            resource_type="AUTH",
            details={"reason": "Invalid credentials provided."},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Issue JWT token
    token = create_access_token({
        "sub": user["username"],
        "user_id": user["id"],
        "name": user["name"],
        "role": user["role"],
    })

    # Record successful login audit
    AuditService.record_action(
        action="LOGIN_SUCCESS",
        user_id=user["id"],
        user_name=user["name"],
        user_role=user["role"],
        resource_type="AUTH",
        details={"station": user["station"], "agency": user["agency"]},
    )

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=720 * 60,
        user=UserProfileResponse(
            id=user["id"],
            username=user["username"],
            name=user["name"],
            designation=user["designation"],
            role=user["role"],
            clearance=user["clearance"],
            agency=user["agency"],
            station=user["station"],
        ),
    )


@router.get("/me", response_model=UserProfileResponse, summary="Get Current Authenticated User Profile")
def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns profile and role claims of the authenticated officer."""
    return UserProfileResponse(
        id=current_user["id"],
        username=current_user["username"],
        name=current_user["name"],
        designation=current_user["designation"],
        role=current_user["role"],
        clearance=current_user["clearance"],
        agency=current_user["agency"],
        station=current_user["station"],
    )
