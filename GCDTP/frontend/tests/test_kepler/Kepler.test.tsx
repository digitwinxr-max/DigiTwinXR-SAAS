/**
 * Tests for Kepler.gl Module
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// Test types
import type {
  KeplerDataset,
  DatasetType,
  HeatmapLayer,
  HeatmapConfig,
  ClusterLayer,
  FlowMapLayer,
  TrajectoryLayer,
  HexBinLayer,
  FilterConfig,
  FilterType,
  TimeWindow,
  AggregationType,
  AggregationMethod,
  CameraState,
  LayerVisibility,
  AnalyticsViewMode,
  FieldType
} from '../../src/kepler/kepler_types';

describe('Kepler Types', () => {
  describe('KeplerDataset', () => {
    it('should create a dataset', () => {
      const dataset: KeplerDataset = {
        id: 'dataset-1',
        label: 'Test Dataset',
        type: DatasetType.GEOJSON,
        data: { fields: [], rows: [] }
      };
      
      expect(dataset.id).toBe('dataset-1');
      expect(dataset.label).toBe('Test Dataset');
    });
  });
  
  describe('DatasetType', () => {
    it('should have correct enum values', () => {
      expect(DatasetType.GEOJSON).toBe('geojson');
      expect(DatasetType.CSV).toBe('csv');
      expect(DatasetType.TIMESERIES).toBe('timeseries');
      expect(DatasetType.TELEMETRY).toBe('telemetry');
    });
  });
  
  describe('FieldType', () => {
    it('should have correct enum values', () => {
      expect(FieldType.STRING).toBe('string');
      expect(FieldType.FLOAT).toBe('float');
      expect(FieldType.INT).toBe('int');
      expect(FieldType.TIMESTAMP).toBe('timestamp');
    });
  });
  
  describe('HeatmapLayer', () => {
    it('should create a heatmap layer', () => {
      const heatmap: HeatmapLayer = {
        id: 'heatmap-1',
        datasetId: 'dataset-1',
        type: 'heatmap',
        config: {
          radiusPixels: 30,
          intensity: 1,
          threshold: 0.05
        }
      };
      
      expect(heatmap.id).toBe('heatmap-1');
      expect(heatmap.type).toBe('heatmap');
    });
  });
  
  describe('ClusterLayer', () => {
    it('should create a cluster layer', () => {
      const cluster: ClusterLayer = {
        id: 'cluster-1',
        datasetId: 'dataset-1',
        type: 'cluster',
        config: {
          radiusPixels: 50,
          minZoom: 0,
          maxZoom: 16
        }
      };
      
      expect(cluster.type).toBe('cluster');
    });
  });
  
  describe('FlowMapLayer', () => {
    it('should create a flow map layer', () => {
      const flow: FlowMapLayer = {
        id: 'flow-1',
        datasetId: 'dataset-1',
        type: 'flow',
        config: {
          sourceLatField: 'src_lat',
          sourceLngField: 'src_lng',
          targetLatField: 'tgt_lat',
          targetLngField: 'tgt_lng'
        }
      };
      
      expect(flow.type).toBe('flow');
    });
  });
  
  describe('TrajectoryLayer', () => {
    it('should create a trajectory layer', () => {
      const trajectory: TrajectoryLayer = {
        id: 'trajectory-1',
        datasetId: 'dataset-1',
        type: 'trajectory',
        config: {
          latField: 'lat',
          lngField: 'lng',
          timestampField: 'timestamp'
        }
      };
      
      expect(trajectory.type).toBe('trajectory');
    });
  });
  
  describe('HexBinLayer', () => {
    it('should create a hex bin layer', () => {
      const hex: HexBinLayer = {
        id: 'hex-1',
        datasetId: 'dataset-1',
        type: 'hexbin',
        config: {
          coverage: 0.9,
          elevationScale: 4,
          extruded: true
        }
      };
      
      expect(hex.type).toBe('hexbin');
    });
  });
  
  describe('FilterConfig', () => {
    it('should create a filter', () => {
      const filter: FilterConfig = {
        id: 'filter-1',
        name: 'Test Filter',
        type: FilterType.ATTRIBUTE,
        field: 'value',
        value: 100
      };
      
      expect(filter.type).toBe(FilterType.ATTRIBUTE);
    });
  });
  
  describe('FilterType', () => {
    it('should have correct enum values', () => {
      expect(FilterType.SPATIAL).toBe('spatial');
      expect(FilterType.ATTRIBUTE).toBe('attribute');
      expect(FilterType.TIME).toBe('time');
      expect(FilterType.RANGE).toBe('range');
    });
  });
  
  describe('TimeWindow', () => {
    it('should create a time window', () => {
      const window: TimeWindow = {
        start: '2024-01-01T00:00:00Z',
        end: '2024-12-31T23:59:59Z'
      };
      
      expect(window.start).toBe('2024-01-01T00:00:00Z');
    });
  });
  
  describe('CameraState', () => {
    it('should create a camera state', () => {
      const camera: CameraState = {
        center: [-122.4, 37.8],
        zoom: 10,
        bearing: 0,
        pitch: 45
      };
      
      expect(camera.center[0]).toBe(-122.4);
    });
  });
  
  describe('AnalyticsViewMode', () => {
    it('should have correct enum values', () => {
      expect(AnalyticsViewMode.LEAFLET_2D).toBe('leaflet-2d');
      expect(AnalyticsViewMode.MAPLIBRE_VECTOR).toBe('maplibre-vector');
      expect(AnalyticsViewMode.CESIUM_3D).toBe('cesium-3d');
      expect(AnalyticsViewMode.TERRA_FEDERATION).toBe('terria-federation');
      expect(AnalyticsViewMode.KEPLER_ANALYTICS).toBe('kepler-analytics');
    });
  });
  
  describe('AggregationType', () => {
    it('should have correct enum values', () => {
      expect(AggregationType.HEX_BIN).toBe('hexbin');
      expect(AggregationType.GRID).toBe('grid');
      expect(AggregationType.CLUSTER).toBe('cluster');
    });
  });
  
  describe('AggregationMethod', () => {
    it('should have correct enum values', () => {
      expect(AggregationMethod.COUNT).toBe('count');
      expect(AggregationMethod.SUM).toBe('sum');
      expect(AggregationMethod.AVG).toBe('avg');
    });
  });
});

// Test AnalyticsModeSwitcher component
describe('AnalyticsModeSwitcher', () => {
  it('should Render mode buttons', () => {
    const { getByText } = render(
      <AnalyticsModeSwitcher 
        currentMode={AnalyticsViewMode.KEPLER_ANALYTICS} 
        onModeChange={() => {}} 
      />
    );
    
    expect(getByText('Leaflet 2D')).toBeInTheDocument();
    expect(getByText('MapLibre Vector')).toBeInTheDocument();
    expect(getByText('Cesium 3D')).toBeInTheDocument();
    expect(getByText('Terria Federation')).toBeInTheDocument();
    expect(getByText('Kepler Analytics')).toBeInTheDocument();
  });
  
  it('should call onModeChange when button clicked', () => {
    const handleChange = jest.fn();
    const { getByText } = render(
      <AnalyticsModeSwitcher 
        currentMode={AnalyticsViewMode.KEPLER_ANALYTICS} 
        onModeChange={handleChange} 
      />
    );
    
    fireEvent.click(getByText('Leaflet 2D'));
    expect(handleChange).toHaveBeenCalledWith(AnalyticsViewMode.LEAFLET_2D);
  });
});

// Import for testing
import { AnalyticsModeSwitcher } from '../../src/components/AnalyticsModeSwitcher';

// Test AnalyticsModeBadge component
describe('AnalyticsModeBadge', () => {
  it('should render correct badge for 2D mode', () => {
    const { getByText } = render(<AnalyticsModeBadge mode={AnalyticsViewMode.LEAFLET_2D} />);
    expect(getByText('2D')).toBeInTheDocument();
  });
  
  it('should render correct badge for Vector mode', () => {
    const { getByText } = render(<AnalyticsModeBadge mode={AnalyticsViewMode.MAPLIBRE_VECTOR} />);
    expect(getByText('Vector')).toBeInTheDocument();
  });
  
  it('should render correct badge for 3D mode', () => {
    const { getByText } = render(<AnalyticsModeBadge mode={AnalyticsViewMode.CESIUM_3D} />);
    expect(getByText('3D')).toBeInTheDocument();
  });
  
  it('should render correct badge for Terria mode', () => {
    const { getByText } = render(<AnalyticsModeBadge mode={AnalyticsViewMode.TERRA_FEDERATION} />);
    expect(getByText('Terria')).toBeInTheDocument();
  });
  
  it('should render correct badge for Analytics mode', () => {
    const { getByText } = render(<AnalyticsModeBadge mode={AnalyticsViewMode.KEPLER_ANALYTICS} />);
    expect(getByText('Analytics')).toBeInTheDocument();
  });
});

// Import for testing
import { AnalyticsModeBadge } from '../../src/components/AnalyticsModeSwitcher';
