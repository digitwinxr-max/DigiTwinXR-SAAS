"""
Tests for GeoServer Integration

Tests workspaces, layers, styles, services, groups, validation, and timeline events.
"""

import pytest
from backend.src.integrations.geoserver import (
    GeoServerClient,
    WorkspaceManager,
    LayerManager,
    StyleManager,
    WMSAdapter,
    WFSAdapter,
    WCSAdapter,
    GeoServerValidator,
    LayerType,
    ServiceType,
    LayerGroupMode,
    Workspace,
    PublishedLayer,
    Style,
    BoundingBox,
)


class TestGeoServerTypes:
    """Tests for GeoServer types."""
    
    def test_layer_type_values(self):
        """Test layer type values."""
        assert LayerType.VECTOR.value == "vector"
        assert LayerType.RASTER.value == "raster"
        assert LayerType.LAYER_GROUP.value == "layer_group"
    
    def test_service_type_values(self):
        """Test service type values."""
        assert ServiceType.WMS.value == "wms"
        assert ServiceType.WFS.value == "wfs"
        assert ServiceType.WCS.value == "wcs"
    
    def test_layer_group_mode_values(self):
        """Test layer group mode values."""
        assert LayerGroupMode.SINGLE.value == "single"
        assert LayerGroupMode.CONTAINER.value == "container"


class TestBoundingBox:
    """Tests for bounding box."""
    
    def test_create_bounding_box(self):
        """Test creating a bounding box."""
        bbox = BoundingBox(
            minx=-180,
            miny=-90,
            maxx=180,
            maxy=90
        )
        
        assert bbox.minx == -180
        assert bbox.maxy == 90
    
    def test_bounding_box_to_dict(self):
        """Test bounding box serialization."""
        bbox = BoundingBox(minx=0, miny=0, maxx=10, maxy=10)
        data = bbox.to_dict()
        
        assert data["minx"] == 0
        assert data["maxy"] == 10


class TestWorkspace:
    """Tests for workspace."""
    
    def test_create_workspace(self):
        """Test creating a workspace."""
        workspace = Workspace(
            id="ws-1",
            name="test_workspace",
            uri="http://example.com/test"
        )
        
        assert workspace.id == "ws-1"
        assert workspace.name == "test_workspace"
        assert workspace.is_default is False
    
    def test_workspace_to_dict(self):
        """Test workspace serialization."""
        workspace = Workspace(
            id="ws-1",
            name="test",
            uri="http://example.com"
        )
        data = workspace.to_dict()
        
        assert data["name"] == "test"


class TestPublishedLayer:
    """Tests for published layer."""
    
    def test_create_layer(self):
        """Test creating a layer."""
        layer = PublishedLayer(
            id="layer-1",
            workspace_id="ws-1",
            name="test_layer"
        )
        
        assert layer.id == "layer-1"
        assert layer.is_published is True
    
    def test_layer_bounding_box(self):
        """Test getting layer bounding box."""
        layer = PublishedLayer(
            id="layer-1",
            workspace_id="ws-1",
            name="test",
            bbox_minx=-10,
            bbox_miny=-10,
            bbox_maxx=10,
            bbox_maxy=10
        )
        
        bbox = layer.get_bounding_box()
        assert bbox is not None
        assert bbox.minx == -10


class TestStyle:
    """Tests for style."""
    
    def test_create_style(self):
        """Test creating a style."""
        style = Style(
            id="style-1",
            workspace_id="ws-1",
            name="test_style"
        )
        
        assert style.id == "style-1"
        assert style.is_default is False


class TestWorkspaceManager:
    """Tests for workspace manager."""
    
    @pytest.fixture
    def manager(self):
        """Create workspace manager."""
        return WorkspaceManager()
    
    def test_create_workspace(self, manager):
        """Test creating a workspace."""
        workspace = manager.create_workspace(
            name="test",
            uri="http://example.com/test"
        )
        
        assert workspace is not None
        assert workspace.name == "test"
    
    def test_get_workspace(self, manager):
        """Test getting a workspace."""
        workspace = manager.create_workspace(
            name="test",
            uri="http://example.com/test"
        )
        
        retrieved = manager.get_workspace(workspace.id)
        
        assert retrieved is not None
        assert retrieved.id == workspace.id
    
    def test_delete_workspace(self, manager):
        """Test deleting a workspace."""
        workspace = manager.create_workspace(
            name="test",
            uri="http://example.com/test"
        )
        workspace_id = workspace.id
        
        result = manager.delete_workspace(workspace_id)
        
        assert result is True
        assert manager.get_workspace(workspace_id) is None
    
    def test_set_default_workspace(self, manager):
        """Test setting default workspace."""
        workspace = manager.create_workspace(
            name="test",
            uri="http://example.com/test"
        )
        
        default = manager.set_default_workspace(workspace.id)
        
        assert default.is_default is True
    
    def test_get_workspace_count(self, manager):
        """Test getting workspace count."""
        manager.create_workspace(name="test1", uri="http://example.com/1")
        manager.create_workspace(name="test2", uri="http://example.com/2")
        
        count = manager.get_workspace_count()
        
        assert count == 2


class TestLayerManager:
    """Tests for layer manager."""
    
    @pytest.fixture
    def manager(self):
        """Create layer manager."""
        return LayerManager()
    
    @pytest.fixture
    def workspace_manager(self):
        """Create workspace manager."""
        return WorkspaceManager()
    
    def test_publish_layer(self, manager, workspace_manager):
        """Test publishing a layer."""
        workspace = workspace_manager.create_workspace(
            name="test",
            uri="http://example.com/test"
        )
        
        layer = manager.publish_layer(
            workspace_id=workspace.id,
            name="test_layer",
            title="Test Layer"
        )
        
        assert layer is not None
        assert layer.name == "test_layer"
    
    def test_get_layer(self, manager, workspace_manager):
        """Test getting a layer."""
        workspace = workspace_manager.create_workspace(
            name="test",
            uri="http://example.com/test"
        )
        layer = manager.publish_layer(
            workspace_id=workspace.id,
            name="test_layer"
        )
        
        retrieved = manager.get_layer(layer.id)
        
        assert retrieved is not None
        assert retrieved.id == layer.id
    
    def test_unpublish_layer(self, manager, workspace_manager):
        """Test unpublishing a layer."""
        workspace = workspace_manager.create_workspace(
            name="test",
            uri="http://example.com/test"
        )
        layer = manager.publish_layer(
            workspace_id=workspace.id,
            name="test_layer"
        )
        
        result = manager.unpublish_layer(layer.id)
        
        assert result is True
        assert manager.get_layer(layer.id).is_published is False
    
    def test_get_layers_for_workspace(self, manager, workspace_manager):
        """Test getting layers for workspace."""
        workspace = workspace_manager.create_workspace(
            name="test",
            uri="http://example.com/test"
        )
        manager.publish_layer(workspace_id=workspace.id, name="layer1")
        manager.publish_layer(workspace_id=workspace.id, name="layer2")
        
        layers = manager.get_layers_for_workspace(workspace.id)
        
        assert len(layers) == 2
    
    def test_set_layer_queryable(self, manager, workspace_manager):
        """Test setting layer queryable."""
        workspace = workspace_manager.create_workspace(
            name="test",
            uri="http://example.com/test"
        )
        layer = manager.publish_layer(
            workspace_id=workspace.id,
            name="test_layer"
        )
        
        manager.set_layer_queryable(layer.id, False)
        
        assert manager.get_layer(layer.id).is_queryable is False


class TestStyleManager:
    """Tests for style manager."""
    
    @pytest.fixture
    def manager(self):
        """Create style manager."""
        return StyleManager()
    
    @pytest.fixture
    def workspace_manager(self):
        """Create workspace manager."""
        return WorkspaceManager()
    
    def test_register_style(self, manager, workspace_manager):
        """Test registering a style."""
        workspace = workspace_manager.create_workspace(
            name="test",
            uri="http://example.com/test"
        )
        
        style = manager.register_style(
            workspace_id=workspace.id,
            name="test_style"
        )
        
        assert style is not None
        assert style.name == "test_style"
    
    def test_assign_style_to_layer(self, manager, workspace_manager):
        """Test assigning style to layer."""
        workspace = workspace_manager.create_workspace(
            name="test",
            uri="http://example.com/test"
        )
        
        layer_mgr = LayerManager()
        layer = layer_mgr.publish_layer(
            workspace_id=workspace.id,
            name="test_layer"
        )
        
        style = manager.register_style(
            workspace_id=workspace.id,
            name="test_style"
        )
        
        result = manager.assign_style_to_layer(
            style.id,
            layer.id,
            as_default=True
        )
        
        assert result is True
    
    def test_create_default_styles(self, manager, workspace_manager):
        """Test creating default styles."""
        workspace = workspace_manager.create_workspace(
            name="test",
            uri="http://example.com/test"
        )
        
        styles = manager.create_default_styles(workspace.id)
        
        assert len(styles) == 4  # point, line, polygon, raster


class TestWMSAdapter:
    """Tests for WMS adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create WMS adapter."""
        return WMSAdapter()
    
    def test_get_capabilities_url(self, adapter):
        """Test getting capabilities URL."""
        url = adapter.get_capabilities_url(workspace="test")
        
        assert "wms" in url
        assert "GetCapabilities" in url
    
    def test_get_map_url(self, adapter):
        """Test getting map URL."""
        url = adapter.get_map_url(
            workspace="test",
            layers=["layer1"],
            bbox={"minx": 0, "miny": 0, "maxx": 10, "maxy": 10}
        )
        
        assert "GetMap" in url
        assert "layer1" in url
    
    def test_get_feature_info_url(self, adapter):
        """Test getting feature info URL."""
        url = adapter.get_feature_info_url(
            workspace="test",
            layers=["layer1"],
            bbox={"minx": 0, "miny": 0, "maxx": 10, "maxy": 10},
            width=800,
            height=600,
            x=400,
            y=300
        )
        
        assert "GetFeatureInfo" in url
    
    def test_get_legend_url(self, adapter):
        """Test getting legend URL."""
        url = adapter.get_legend_url(
            workspace="test",
            layer="layer1"
        )
        
        assert "GetLegendGraphic" in url


class TestWFSAdapter:
    """Tests for WFS adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create WFS adapter."""
        return WFSAdapter()
    
    def test_get_capabilities_url(self, adapter):
        """Test getting capabilities URL."""
        url = adapter.get_capabilities_url(workspace="test")
        
        assert "wfs" in url
        assert "GetCapabilities" in url
    
    def test_get_feature_url(self, adapter):
        """Test getting feature URL."""
        url = adapter.get_feature_url(
            workspace="test",
            type_names=["test:type1"]
        )
        
        assert "GetFeature" in url
        assert "test:type1" in url
    
    def test_describe_feature_type_url(self, adapter):
        """Test getting describe feature type URL."""
        url = adapter.describe_feature_type_url(
            workspace="test",
            type_name="test:type1"
        )
        
        assert "DescribeFeatureType" in url


class TestWCSAdapter:
    """Tests for WCS adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create WCS adapter."""
        return WCSAdapter()
    
    def test_get_capabilities_url(self, adapter):
        """Test getting capabilities URL."""
        url = adapter.get_capabilities_url(workspace="test")
        
        assert "wcs" in url
        assert "GetCapabilities" in url
    
    def test_get_output_formats(self, adapter):
        """Test getting output formats."""
        formats = adapter.get_output_formats()
        
        assert "image/geotiff" in formats
        assert "image/png" in formats


class TestGeoServerValidator:
    """Tests for GeoServer validator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator."""
        return GeoServerValidator()
    
    def test_validate_workspace(self, validator):
        """Test validating a workspace."""
        workspace = Workspace(
            id="ws-1",
            name="test",
            uri="http://example.com"
        )
        
        issues = validator.validate_workspace(workspace)
        
        assert len(issues) == 0
    
    def test_validate_workspace_missing_name(self, validator):
        """Test validation with missing name."""
        workspace = Workspace(
            id="ws-1",
            name="",
            uri="http://example.com"
        )
        
        issues = validator.validate_workspace(workspace)
        
        assert len(issues) > 0
    
    def test_validate_layer(self, validator):
        """Test validating a layer."""
        layer = PublishedLayer(
            id="layer-1",
            workspace_id="ws-1",
            name="test"
        )
        
        issues = validator.validate_layer(layer)
        
        assert len(issues) == 0
    
    def test_validate_style(self, validator):
        """Test validating a style."""
        style = Style(
            id="style-1",
            workspace_id="ws-1",
            name="test"
        )
        
        issues = validator.validate_style(style)
        
        assert len(issues) == 0
    
    def test_validate_bounding_box(self, validator):
        """Test validating bounding box."""
        issues = validator.validate_bounding_box(0, 0, 10, 10)
        
        assert len(issues) == 0
    
    def test_validate_bounding_box_invalid(self, validator):
        """Test validating invalid bounding box."""
        issues = validator.validate_bounding_box(10, 0, 0, 10)
        
        assert len(issues) > 0
    
    def test_validate_sld_content(self, validator):
        """Test validating SLD content."""
        sld = '''<?xml version="1.0"?>
<StyledLayerDescriptor>
</StyledLayerDescriptor>'''
        
        issues = validator.validate_sld_content(sld)
        
        assert len(issues) == 0
    
    def test_validate_sld_content_invalid(self, validator):
        """Test validating invalid SLD content."""
        issues = validator.validate_sld_content("not xml")
        
        assert len(issues) > 0
    
    def test_check_workspace_conflict(self, validator):
        """Test checking workspace conflicts."""
        existing = {
            "ws-1": Workspace(id="ws-1", name="test", uri="http://example.com")
        }
        
        conflicts = validator.check_workspace_conflict(
            name="test",
            uri="http://different.com",
            existing_workspaces=existing
        )
        
        assert len(conflicts) > 0


class TestGeoServerClient:
    """Tests for GeoServer client."""
    
    @pytest.fixture
    def client(self):
        """Create GeoServer client."""
        return GeoServerClient(base_url="http://localhost:8080/geoserver")
    
    def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.base_url == "http://localhost:8080/geoserver"
    
    def test_health_check_returns_false(self, client):
        """Test health check when server not available."""
        result = client.health_check()
        
        assert result is False
