"""
GeoServer Integration Module

Spatial publishing layer for FastAPI.
FastAPI remains authoritative for business logic.

Components:
- GeoServer Client
- Workspace Manager
- Layer Manager
- Style Manager
- WMS Adapter
- WFS Adapter
- WCS Adapter
"""

from .geoserver_types import (
    LayerType,
    ServiceType,
    LayerGroupMode,
    BoundingBox,
    Workspace,
    PublishedLayer,
    Style,
    ServiceEndpoint,
    LayerGroup,
    WorkspaceSummary,
    LayerDetails,
)

from .geoserver_client import GeoServerClient, GeoServerClientError
from .workspace_manager import WorkspaceManager
from .layer_manager import LayerManager
from .style_manager import StyleManager
from .wms_adapter import WMSAdapter
from .wfs_adapter import WFSAdapter
from .wcs_adapter import WCSAdapter
from .geoserver_validator import GeoServerValidator


__all__ = [
    # Enums
    "LayerType",
    "ServiceType",
    "LayerGroupMode",
    # Types
    "BoundingBox",
    "Workspace",
    "PublishedLayer",
    "Style",
    "ServiceEndpoint",
    "LayerGroup",
    "WorkspaceSummary",
    "LayerDetails",
    # Client
    "GeoServerClient",
    "GeoServerClientError",
    # Managers
    "WorkspaceManager",
    "LayerManager",
    "StyleManager",
    # Adapters
    "WMSAdapter",
    "WFSAdapter",
    "WCSAdapter",
    # Validators
    "GeoServerValidator",
]
