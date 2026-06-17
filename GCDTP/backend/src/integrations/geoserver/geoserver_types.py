"""
GeoServer Types

Core data types for GeoServer integration.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class LayerType(str, Enum):
    """Layer type."""
    VECTOR = "vector"
    RASTER = "raster"
    LAYER_GROUP = "layer_group"
    OWS = "ows"


class ServiceType(str, Enum):
    """OGC Service type."""
    WMS = "wms"
    WFS = "wfs"
    WCS = "wcs"
    WMTS = "wmts"


class LayerGroupMode(str, Enum):
    """Layer group mode."""
    SINGLE = "single"
    CONTAINER = "container"
    NAMED = "named"
    OPACITY = "opacity"


class BoundingBox:
    """Bounding box for layers."""
    
    def __init__(
        self,
        minx: float,
        miny: float,
        maxx: float,
        maxy: float,
        crs: str = "EPSG:4326"
    ):
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
        self.crs = crs
    
    def to_dict(self) -> Dict:
        return {
            "minx": self.minx,
            "miny": self.miny,
            "maxx": self.maxx,
            "maxy": self.maxy,
            "crs": self.crs
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "BoundingBox":
        return cls(
            minx=data["minx"],
            miny=data["miny"],
            maxx=data["maxx"],
            maxy=data["maxy"],
            crs=data.get("crs", "EPSG:4326")
        )


@dataclass
class Workspace:
    """
    GeoServer workspace.
    """
    id: str
    name: str
    uri: str
    description: str = ""
    is_default: bool = False
    is_isolated: bool = False
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "uri": self.uri,
            "description": self.description,
            "is_default": self.is_default,
            "is_isolated": self.is_isolated,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class PublishedLayer:
    """
    Published map layer.
    """
    id: str
    workspace_id: str
    name: str
    layer_type: LayerType = LayerType.VECTOR
    native_name: str = ""
    title: str = ""
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    srs: str = "EPSG:4326"
    
    # Bounding box
    bbox_minx: Optional[float] = None
    bbox_miny: Optional[float] = None
    bbox_maxx: Optional[float] = None
    bbox_maxy: Optional[float] = None
    native_bbox: Optional[Dict] = None
    
    # Status
    is_published: bool = True
    is_queryable: bool = True
    caching_enabled: bool = False
    cache_max_age: Optional[int] = None
    
    # Audit
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "name": self.name,
            "native_name": self.native_name,
            "layer_type": self.layer_type.value,
            "title": self.title,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "srs": self.srs,
            "is_published": self.is_published,
            "is_queryable": self.is_queryable,
        }
    
    def get_bounding_box(self) -> Optional[BoundingBox]:
        """Get bounding box."""
        if all([self.bbox_minx, self.bbox_miny, self.bbox_maxx, self.bbox_maxy]):
            return BoundingBox(
                self.bbox_minx,
                self.bbox_miny,
                self.bbox_maxx,
                self.bbox_maxy,
                self.srs
            )
        return None


@dataclass
class Style:
    """
    Layer style (SLD).
    """
    id: str
    workspace_id: str
    name: str
    filename: str = ""
    sld_content: str = ""
    is_default: bool = False
    layer_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "name": self.name,
            "filename": self.filename,
            "is_default": self.is_default,
            "layer_id": self.layer_id,
        }


@dataclass
class ServiceEndpoint:
    """
    OGC Service endpoint.
    """
    id: str
    workspace_id: str
    service_type: ServiceType
    endpoint_url: str = ""
    is_enabled: bool = True
    version: str = "1.3.0"
    is_default: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "service_type": self.service_type.value,
            "endpoint_url": self.endpoint_url,
            "is_enabled": self.is_enabled,
            "version": self.version,
            "is_default": self.is_default,
        }


@dataclass
class LayerGroup:
    """
    Layer group for organizing layers.
    """
    id: str
    workspace_id: str
    name: str
    title: str = ""
    abstract: str = ""
    mode: LayerGroupMode = LayerGroupMode.SINGLE
    layers: List[Dict] = field(default_factory=list)  # [{layer_id, order, style_id}]
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "name": self.name,
            "title": self.title,
            "abstract": self.abstract,
            "mode": self.mode.value,
            "layer_count": len(self.layers),
        }


@dataclass
class WorkspaceSummary:
    """Summary of a workspace."""
    workspace: Workspace
    layer_count: int = 0
    group_count: int = 0
    style_count: int = 0
    enabled_services: int = 0
    
    def to_dict(self) -> Dict:
        data = self.workspace.to_dict()
        data["layer_count"] = self.layer_count
        data["group_count"] = self.group_count
        data["style_count"] = self.style_count
        data["enabled_services"] = self.enabled_services
        return data


@dataclass
class LayerDetails:
    """Detailed layer information."""
    layer: PublishedLayer
    workspace_name: str = ""
    default_style: Optional[str] = None
    
    def to_dict(self) -> Dict:
        data = self.layer.to_dict()
        data["workspace_name"] = self.workspace_name
        data["default_style"] = self.default_style
        return data
