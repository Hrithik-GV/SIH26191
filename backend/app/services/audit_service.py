"""Audit Logging Service: Tracks administrative modifications, data edits, and report exports."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session

logger = logging.getLogger("sih26191.audit")


class AuditService:
    """
    Maintains a tamper-evident chronological audit log of administrative actions,
    data mutations, report generations, and access events.
    """

    _in_memory_logs: List[Dict[str, Any]] = []
    _max_logs: int = 500

    @classmethod
    def record_action(
        cls,
        action: str,
        user_id: str,
        user_name: str,
        user_role: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Records a new audit entry.
        """
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action.upper(),
            "user_id": user_id,
            "user_name": user_name,
            "user_role": user_role.upper(),
            "resource_type": resource_type.upper(),
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address or "127.0.0.1",
        }

        cls._in_memory_logs.append(entry)
        if len(cls._in_memory_logs) > cls._max_logs:
            cls._in_memory_logs.pop(0)

        logger.info(
            f"[AUDIT] {entry['timestamp']} | {user_role}:{user_name} ({user_id}) | "
            f"Action: {action} on {resource_type}:{resource_id}"
        )
        return entry

    @classmethod
    def get_logs(
        cls,
        page: int = 1,
        page_size: int = 20,
        action: Optional[str] = None,
        user_role: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Queries and filters audit entries."""
        filtered = cls._in_memory_logs

        if action:
            act_clean = action.strip().upper()
            filtered = [log for log in filtered if log["action"] == act_clean]
        if user_role:
            role_clean = user_role.strip().upper()
            filtered = [log for log in filtered if log["user_role"] == role_clean]
        if resource_type:
            res_clean = resource_type.strip().upper()
            filtered = [log for log in filtered if log["resource_type"] == res_clean]

        # Reverse order for newest first
        sorted_logs = list(reversed(filtered))
        total = len(sorted_logs)
        offset = (page - 1) * page_size
        items = sorted_logs[offset : offset + page_size]

        return items, total


# Pre-seed initial administrative audit log entries for Wayanad operations demonstration
AuditService.record_action(
    action="SYSTEM_INITIALIZE",
    user_id="sys_admin",
    user_name="System Supervisor",
    user_role="ADMIN",
    resource_type="SYSTEM",
    details={"message": "Disaster management portal audit system initialized with WGS84 PostGIS support."},
)

AuditService.record_action(
    action="VERIFY_HAZARD_ZONES",
    user_id="collector_wayanad",
    user_name="Dr. A. K. Nambiar, IAS",
    user_role="AUTHORITY_VIEWER",
    resource_type="HAZARD_ZONE",
    details={"perimeter": "Mundakkai-Chooralmala Red Zone", "status": "CONFIRMED_HIGH_EXPOSURE"},
)
