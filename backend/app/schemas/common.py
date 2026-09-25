"""Common Pydantic models for GeoJSON representations, pagination, and sorting."""

import json
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
import shapely.geometry
import shapely.wkt
from geoalchemy2.elements import WKBElement, WKTElement
from geoalchemy2.shape import to_shape

T = TypeVar("T")


class GeoJSONGeometry(BaseModel):
    """GeoJSON geometry object compliant with RFC 7946."""
    type: str = Field(..., description="Geometry type (Point, Polygon, MultiPolygon, etc.)")
    coordinates: Any = Field(..., description="GeoJSON coordinates array")


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature object."""
    type: str = Field(default="Feature")
    id: Optional[str] = Field(None, description="Feature identifier")
    geometry: Optional[Dict[str, Any]] = Field(None, description="GeoJSON geometry")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Feature attributes and metadata")


class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection object compliant with RFC 7946."""
    type: str = Field(default="FeatureCollection")
    features: List[GeoJSONFeature] = Field(default_factory=list, description="List of GeoJSON features")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated envelope."""
    total: int = Field(..., description="Total matching items count")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total pages available")
    items: List[T] = Field(default_factory=list, description="Page items")


def geometry_to_geojson(geom: Any) -> Optional[Dict[str, Any]]:
    """
    Safely translates GeoAlchemy2, WKT, WKB, Shapely, or GeoJSON strings
    into a native GeoJSON Python dictionary.
    """
    if geom is None:
        return None
    if isinstance(geom, dict):
        return geom
    if isinstance(geom, str):
        try:
            return json.loads(geom)
        except Exception:
            try:
                shp = shapely.wkt.loads(geom)
                return shapely.geometry.mapping(shp)
            except Exception:
                return None
    if isinstance(geom, (WKBElement, WKTElement)):
        try:
            shp = to_shape(geom)
            return shapely.geometry.mapping(shp)
        except Exception:
            pass
    try:
        shp = to_shape(geom)
        return shapely.geometry.mapping(shp)
    except Exception:
        return None
