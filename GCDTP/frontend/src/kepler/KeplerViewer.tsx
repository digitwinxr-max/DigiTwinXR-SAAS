/**
 * Kepler.gl Viewer Component
 */

import React, { useRef, useEffect, useState } from 'react';
import type { CameraState, AnalyticsLayer } from './kepler_types';

interface KeplerViewerProps {
  datasets?: any[];
  layers?: AnalyticsLayer[];
  camera?: CameraState | null;
  onCameraChange?: (camera: CameraState) => void;
  onMapReady?: (map: any) => void;
  onLayerAdd?: (layer: AnalyticsLayer) => void;
  onLayerRemove?: (layerId: string) => void;
  className?: string;
}

export function KeplerViewer({
  datasets = [],
  layers = [],
  camera,
  onCameraChange,
  onMapReady,
  onLayerAdd,
  onLayerRemove,
  className = ''
}: KeplerViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Initialize Kepler map
    const initMap = async () => {
      if (!containerRef.current) return;
      
      // Placeholder - actual implementation would use kepler.gl
      setIsReady(true);
      onMapReady?.({});
    };

    initMap();

    return () => {
      // Cleanup
    };
  }, []);

  useEffect(() => {
    // Update camera when prop changes
    if (mapRef.current && camera) {
      mapRef.current.setView({
        center: camera.center,
        zoom: camera.zoom,
        bearing: camera.bearing,
        pitch: camera.pitch
      });
    }
  }, [camera]);

  const handleLayerAdded = (layer: AnalyticsLayer) => {
    onLayerAdd?.(layer);
  };

  const handleLayerRemoved = (layerId: string) => {
    onLayerRemove?.(layerId);
  };

  return (
    <div ref={containerRef} className={`kepler-viewer ${className}`}>
      {!isReady && <div className="viewer-loading">Loading Kepler.gl...</div>}
      {isReady && (
        <div className="kepler-container">
          <div className="kepler-placeholder">Kepler.gl Analytics View</div>
          <div className="layer-count">{layers.length} layers</div>
          <div className="dataset-count">{datasets.length} datasets</div>
        </div>
      )}
    </div>
  );
}

// Viewer controls
interface KeplerViewerControlsProps {
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onResetView?: () => void;
  onFullscreen?: () => void;
  onExportScreenshot?: () => void;
}

export function KeplerViewerControls({
  onZoomIn,
  onZoomOut,
  onResetView,
  onFullscreen,
  onExportScreenshot
}: KeplerViewerControlsProps) {
  return (
    <div className="kepler-controls">
      <button onClick={onZoomIn} className="control-btn" title="Zoom in">+</button>
      <button onClick={onZoomOut} className="control-btn" title="Zoom out">−</button>
      <button onClick={onResetView} className="control-btn" title="Reset view">⌂</button>
      <button onClick={onExportScreenshot} className="control-btn" title="Export screenshot">📷</button>
      <button onClick={onFullscreen} className="control-btn" title="Fullscreen">⛶</button>
    </div>
  );
}

// Layer panel
interface KeplerLayerPanelProps {
  layers: AnalyticsLayer[];
  onToggleVisibility?: (layerId: string) => void;
  onRemove?: (layerId: string) => void;
  onOpacityChange?: (layerId: string, opacity: number) => void;
}

export function KeplerLayerPanel({
  layers,
  onToggleVisibility,
  onRemove,
  onOpacityChange
}: KeplerLayerPanelProps) {
  return (
    <div className="kepler-layer-panel">
      <h3>Analytics Layers</h3>
      {layers.length === 0 ? (
        <p className="empty-message">No layers added</p>
      ) : (
        <ul className="layer-list">
          {layers.map(layer => (
            <li key={layer.id} className="layer-item">
              <label>
                <input
                  type="checkbox"
                  onChange={() => onToggleVisibility?.(layer.id)}
                />
                {layer.type}
              </label>
              <button onClick={() => onRemove?.(layer.id)}>×</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// Dataset panel
interface KeplerDatasetPanelProps {
  datasets: any[];
  onRemove?: (datasetId: string) => void;
}

export function KeplerDatasetPanel({ datasets, onRemove }: KeplerDatasetPanelProps) {
  return (
    <div className="kepler-dataset-panel">
      <h3>Datasets</h3>
      {datasets.length === 0 ? (
        <p className="empty-message">No datasets loaded</p>
      ) : (
        <ul className="dataset-list">
          {datasets.map(dataset => (
            <li key={dataset.id} className="dataset-item">
              <span className="dataset-label">{dataset.label}</span>
              <span className="dataset-type">{dataset.type}</span>
              <button onClick={() => onRemove?.(dataset.id)}>×</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// Filter panel
interface KeplerFilterPanelProps {
  filters: any[];
  onRemove?: (filterId: string) => void;
}

export function KeplerFilterPanel({ filters, onRemove }: KeplerFilterPanelProps) {
  return (
    <div className="kepler-filter-panel">
      <h3>Filters</h3>
      {filters.length === 0 ? (
        <p className="empty-message">No filters applied</p>
      ) : (
        <ul className="filter-list">
          {filters.map(filter => (
            <li key={filter.id} className="filter-item">
              <span className="filter-name">{filter.name}</span>
              <span className="filter-type">{filter.type}</span>
              <button onClick={() => onRemove?.(filter.id)}>×</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
