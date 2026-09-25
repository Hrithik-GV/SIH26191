"""Custom exception hierarchy for the SIH 2026 GIS Processing Engine.

These exceptions ensure strict geospatial validation, preventing silent failures
such as mixing geographic and projected CRS or processing corrupted geometries.
"""

from typing import Optional, Any


class GISEngineError(Exception):
    """Base exception class for all GIS processing errors."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class CRSCompatibilityError(GISEngineError):
    """
    Raised when two spatial layers have mismatched, missing, or incompatible
    Coordinate Reference Systems (CRS), or when metric operations (e.g. buffering in meters)
    are attempted on unprojected geographic coordinates without reprojection.
    """
    pass


class InvalidGeometryError(GISEngineError):
    """
    Raised when a geometry is topologically invalid, self-intersecting, corrupt,
    or unrepairable by shapely.make_valid.
    """
    pass


class EmptyLayerError(GISEngineError):
    """Raised when an operation requires spatial features but an empty layer was provided."""
    pass


class RasterProcessingError(GISEngineError):
    """Raised when DEM reading, raster transformation, or slope calculation fails."""
    pass


class MissingHazardDataError(GISEngineError):
    """Raised when required hazard layer attributes (e.g., severity, hazard_type) are missing."""
    pass
