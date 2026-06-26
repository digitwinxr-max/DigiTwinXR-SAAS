/**
 * Tests for MapLibre Module
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// Test types
import type {
  MapLibreConfig,
  CameraState,
  MapStyle,
  VectorTileSource,
  RasterTileSource,
  PMTilesInfo,
  OfflineRegion,
  TileCacheStats,
  LayerVisibility,
  SyncState,
  MapViewMode,
  ThemeConfig,
  OfflineStatus
} from '../../src/maplibre/maplibre_types';

describe('MapLibre Types', () => {
  describe('CameraState', () => {
    it('should create a camera state', () => {
      const camera: CameraState = {
        center: [-122.4, 37.8],
        zoom: 10,
        bearing: 0,
        pitch: 45
      };
      
      expect(camera.center[0]).toBe(-122.4);
      expect(camera.zoom).toBe(10);
      expect(camera.pitch).toBe(45);
    });
    
    it('should create camera state with default values', () => {
      const camera: CameraState = {
        center: [0, 0],
        zoom: 2,
        bearing: 0,
        pitch: 0
      };
      
      expect(camera.center).toEqual([0, 0]);
    });
  });
  
  describe('MapViewMode', () => {
    it('should have correct enum values', () => {
      expect(MapViewMode.LEAFLET_2D).toBe('leaflet-2d');
      expect(MapViewMode.MAPLIBRE_VECTOR).toBe('maplibre-vector');
      expect(MapViewMode.CESIUM_3D).toBe('cesium-3d');
      expect(MapViewMode.TERRA_FEDERATION).toBe('terria-federation');
    });
  });
  
  describe('VectorTileSource', () => {
    it('should create a vector tile source', () => {
      const source: VectorTileSource = {
        id: 'test-source',
        type: 'vector',
        url: 'https://example.com/tiles/{z}/{x}/{y}.mvt',
        tiles: ['https://example.com/tiles/{z}/{x}/{y}.mvt'],
        bounds: [-180, -85, 180, 85],
        minzoom: 0,
        maxzoom: 14
      };
      
      expect(source.id).toBe('test-source');
      expect(source.type).toBe('vector');
    });
  });
  
  describe('RasterTileSource', () => {
    it('should create a raster tile source', () => {
      const source: RasterTileSource = {
        id: 'raster-source',
        type: 'raster',
        url: 'https://example.com/tiles/{z}/{x}/{y}.png',
        tileSize: 256
      };
      
      expect(source.id).toBe('raster-source');
      expect(source.tileSize).toBe(256);
    });
  });
  
  describe('PMTilesInfo', () => {
    it('should create PMTiles info', () => {
      const info: PMTilesInfo = {
        id: 'pmtiles-1',
        name: 'Test PMTiles',
        bounds: [-180, -85, 180, 85],
        center: [0, 0],
        minZoom: 0,
        maxZoom: 14,
        layers: ['buildings', 'roads'],
        tileType: 'pbf'
      };
      
      expect(info.layers).toHaveLength(2);
      expect(info.maxZoom).toBe(14);
    });
  });
  
  describe('OfflineRegion', () => {
    it('should create an offline region', () => {
      const region: OfflineRegion = {
        id: 'region-1',
        name: 'Test Region',
        bounds: [-122.5, 37.5, -122.0, 38.0],
        minZoom: 10,
        maxZoom: 16,
        status: OfflineStatus.PENDING,
        progress: 0,
        createdAt: '2024-01-01T00:00:00Z'
      };
      
      expect(region.status).toBe(OfflineStatus.PENDING);
    });
  });
  
  describe('TileCacheStats', () => {
    it('should create cache stats', () => {
      const stats: TileCacheStats = {
        hits: 100,
        misses: 20,
        size: 1024 * 1024,
        maxSize: 100 * 1024 * 1024,
        entries: 50
      };
      
      expect(stats.hits).toBe(100);
      expect(stats.misses).toBe(20);
    });
  });
  
  describe('ThemeConfig', () => {
    it('should create a theme config', () => {
      const theme: ThemeConfig = {
        id: 'dark-theme',
        name: 'Dark',
        primaryColor: '#90CAF9',
        secondaryColor: '#BDBDBD',
        backgroundColor: '#121212',
        textColor: '#FFFFFF',
        mapStyle: 'https://example.com/style.json'
      };
      
      expect(theme.id).toBe('dark-theme');
      expect(theme.primaryColor).toBe('#90CAF9');
    });
  });
  
  describe('SyncState', () => {
    it('should create sync state', () => {
      const state: SyncState = {
        camera: null,
        layers: [],
        selection: []
      };
      
      expect(state.camera).toBeNull();
      expect(state.layers).toHaveLength(0);
    });
  });
  
  describe('OfflineStatus', () => {
    it('should have correct enum values', () => {
      expect(OfflineStatus.PENDING).toBe('pending');
      expect(OfflineStatus.DOWNLOADING).toBe('downloading');
      expect(OfflineStatus.COMPLETED).toBe('completed');
      expect(OfflineStatus.FAILED).toBe('failed');
    });
  });
});

// Test MapModeSwitcher component
describe('MapModeSwitcher', () => {
  it('should render mode buttons', () => {
    const { getByText } = render(
      <MapModeSwitcher 
        currentMode={MapViewMode.MAPLIBRE_VECTOR} 
        onModeChange={() => {}} 
      />
    );
    
    expect(getByText('Leaflet 2D')).toBeInTheDocument();
    expect(getByText('MapLibre Vector')).toBeInTheDocument();
    expect(getByText('Cesium 3D')).toBeInTheDocument();
    expect(getByText('Terria Federation')).toBeInTheDocument();
  });
  
  it('should call onModeChange when button clicked', () => {
    const handleChange = jest.fn();
    const { getByText } = render(
      <MapModeSwitcher 
        currentMode={MapViewMode.MAPLIBRE_VECTOR} 
        onModeChange={handleChange} 
      />
    );
    
    fireEvent.click(getByText('Leaflet 2D'));
    expect(handleChange).toHaveBeenCalledWith(MapViewMode.LEAFLET_2D);
  });
  
  it('should highlight active mode', () => {
    const { getByText } = render(
      <MapModeSwitcher 
        currentMode={MapViewMode.MAPLIBRE_VECTOR} 
        onModeChange={() => {}} 
      />
    );
    
    const button = getByText('MapLibre Vector').closest('button');
    expect(button).toHaveClass('active');
  });
});

// Import for testing
import { MapModeSwitcher } from '../../src/components/MapModeSwitcher';

// Test MapModeBadge component
describe('MapModeBadge', () => {
  it('should render correct badge for Leaflet mode', () => {
    const { getByText } = render(<MapModeBadge mode={MapViewMode.LEAFLET_2D} />);
    expect(getByText('2D')).toBeInTheDocument();
  });
  
  it('should render correct badge for MapLibre mode', () => {
    const { getByText } = render(<MapModeBadge mode={MapViewMode.MAPLIBRE_VECTOR} />);
    expect(getByText('Vector')).toBeInTheDocument();
  });
  
  it('should render correct badge for Cesium mode', () => {
    const { getByText } = render(<MapModeBadge mode={MapViewMode.CESIUM_3D} />);
    expect(getByText('3D')).toBeInTheDocument();
  });
  
  it('should render correct badge for Terria mode', () => {
    const { getByText } = render(<MapModeBadge mode={MapViewMode.TERRA_FEDERATION} />);
    expect(getByText('Terria')).toBeInTheDocument();
  });
});

// Import for testing
import { MapModeBadge } from '../../src/components/MapModeSwitcher';

// Test ViewerControls component
describe('ViewerControls', () => {
  it('should render control buttons', () => {
    const { getByTitle } = render(
      <ViewerControlsWrapper />
    );
    
    expect(getByTitle('Zoom in')).toBeInTheDocument();
    expect(getByTitle('Zoom out')).toBeInTheDocument();
    expect(getByTitle('Reset rotation')).toBeInTheDocument();
    expect(getByTitle('Fullscreen')).toBeInTheDocument();
  });
  
  it('should call onZoomIn when clicked', () => {
    const onZoomIn = jest.fn();
    const { getByTitle } = render(
      <ViewerControls 
        onZoomIn={onZoomIn}
        onZoomOut={() => {}}
        onResetView={() => {}}
        onCompassClick={() => {}}
        onFullscreen={() => {}}
      />
    );
    
    fireEvent.click(getByTitle('Zoom in'));
    expect(onZoomIn).toHaveBeenCalled();
  });
});

// Import for testing
import { ViewerControls } from '../../src/maplibre/MapLibreViewer';

// Helper wrapper
function ViewerControlsWrapper() {
  return (
    <ViewerControls 
      onZoomIn={() => {}}
      onZoomOut={() => {}}
      onResetView={() => {}}
      onCompassClick={() => {}}
      onFullscreen={() => {}}
    />
  );
}

// Test ScaleBar component
describe('ScaleBar', () => {
  it('should render scale bar', () => {
    const { getByText } = render(<ScaleBar />);
    expect(getByText('0')).toBeInTheDocument();
  });
  
  it('should show metric units', () => {
    const { getByText } = render(<ScaleBar unit="metric" />);
    expect(getByText('500m')).toBeInTheDocument();
  });
  
  it('should show imperial units', () => {
    const { getByText } = render(<ScaleBar unit="imperial" />);
    expect(getByText('0.5mi')).toBeInTheDocument();
  });
});

// Import for testing
import { ScaleBar } from '../../src/maplibre/MapLibreViewer';
