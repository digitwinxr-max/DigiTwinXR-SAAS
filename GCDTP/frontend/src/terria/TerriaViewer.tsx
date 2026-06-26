/**
 * Terria Viewer Component
 */

import React, { useRef, useEffect, useState } from 'react';
import type { CameraPosition, ViewMode, CatalogItem } from './terria_types';

interface TerriaViewerProps {
  viewMode: ViewMode;
  cameraPosition?: CameraPosition | null;
  layers: CatalogItem[];
  onCameraChange?: (position: CameraPosition) => void;
  onLayerClick?: (layer: CatalogItem) => void;
  className?: string;
}

export function TerriaViewer({
  viewMode,
  cameraPosition,
  layers,
  onCameraChange,
  onLayerClick,
  className = ''
}: TerriaViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Initialize viewer based on view mode
    const initViewer = async () => {
      setIsReady(true);
    };
    
    initViewer();
  }, [viewMode]);

  const renderLeafletView = () => (
    <div className="leaflet-viewer">
      <div className="leaflet-placeholder">
        Leaflet 2D View
      </div>
    </div>
  );

  const renderCesiumView = () => (
    <div className="cesium-viewer">
      <div className="cesium-placeholder">
        Cesium 3D View
      </div>
    </div>
  );

  const renderTerriaView = () => (
    <div className="terria-view">
      <div className="terria-placeholder">
        TerriaJS Federation View
      </div>
    </div>
  );

  return (
    <div ref={containerRef} className={`terria-viewer ${className}`}>
      {!isReady && <div className="viewer-loading">Loading viewer...</div>}
      
      {isReady && viewMode === ViewMode.LEAFLET_2D && renderLeafletView()}
      {isReady && viewMode === ViewMode.CESIUM_3D && renderCesiumView()}
      {isReady && viewMode === ViewMode.TERRA_FEDERATION && renderTerriaView()}
    </div>
  );
}

// Viewer controls
interface ViewerControlsProps {
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onResetView?: () => void;
  onFullscreen?: () => void;
  viewMode: ViewMode;
}

export function ViewerControls({
  onZoomIn,
  onZoomOut,
  onResetView,
  onFullscreen,
  viewMode
}: ViewerControlsProps) {
  return (
    <div className="viewer-controls">
      <button onClick={onZoomIn} className="control-btn" title="Zoom in">
        +
      </button>
      <button onClick={onZoomOut} className="control-btn" title="Zoom out">
        −
      </button>
      <button onClick={onResetView} className="control-btn" title="Reset view">
        ⌂
      </button>
      <button onClick={onFullscreen} className="control-btn" title="Fullscreen">
        ⛶
      </button>
    </div>
  );
}

// Compass/Navigation controls
interface CompassProps {
  heading: number;
  onHeadingChange?: (heading: number) => void;
}

export function Compass({ heading, onHeadingChange }: CompassProps) {
  return (
    <div 
      className="compass"
      style={{ transform: `rotate(${-heading}deg)` }}
      onClick={() => onHeadingChange?.(0)}
    >
      <div className="compass-needle">N</div>
    </div>
  );
}

// Zoom controls
interface ZoomControlsProps {
  onZoomIn?: () => void;
  onZoomOut?: () => void;
}

export function ZoomControls({ onZoomIn, onZoomOut }: ZoomControlsProps) {
  return (
    <div className="zoom-controls">
      <button onClick={onZoomIn} className="zoom-btn">+</button>
      <button onClick={onZoomOut} className="zoom-btn">−</button>
    </div>
  );
}

// Location marker
interface LocationMarkerProps {
  longitude: number;
  latitude: number;
  label?: string;
  onClick?: () => void;
}

export function LocationMarker({ longitude, latitude, label, onClick }: LocationMarkerProps) {
  return (
    <div 
      className="location-marker"
      onClick={onClick}
      title={`${longitude}, ${latitude}`}
    >
      <span className="marker-icon">📍</span>
      {label && <span className="marker-label">{label}</span>}
    </div>
  );
}

// Drawing tools
interface DrawingToolsProps {
  onDrawPoint?: () => void;
  onDrawLine?: () => void;
  onDrawPolygon?: () => void;
  onClear?: () => void;
  activeTool?: string | null;
}

export function DrawingTools({
  onDrawPoint,
  onDrawLine,
  onDrawPolygon,
  onClear,
  activeTool
}: DrawingToolsProps) {
  return (
    <div className="drawing-tools">
      <button 
        className={`tool-btn ${activeTool === 'point' ? 'active' : ''}`}
        onClick={onDrawPoint}
        title="Draw point"
      >
        ●
      </button>
      <button 
        className={`tool-btn ${activeTool === 'line' ? 'active' : ''}`}
        onClick={onDrawLine}
        title="Draw line"
      >
        /
      </button>
      <button 
        className={`tool-btn ${activeTool === 'polygon' ? 'active' : ''}`}
        onClick={onDrawPolygon}
        title="Draw polygon"
      >
        ⬡
      </button>
      <button 
        className="tool-btn"
        onClick={onClear}
        title="Clear drawings"
      >
        ✕
      </button>
    </div>
  );
}
