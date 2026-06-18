/**
 * MapLibre Viewer Component
 */

import React, { useRef, useEffect, useState } from 'react';
import type { MapLibreConfig, CameraState, MapStyle } from './maplibre_types';

interface MapLibreViewerProps {
  config?: MapLibreConfig;
  style?: MapStyle;
  camera?: CameraState | null;
  onCameraChange?: (camera: CameraState) => void;
  onMapReady?: (map: any) => void;
  className?: string;
}

export function MapLibreViewer({
  config,
  style,
  camera,
  onCameraChange,
  onMapReady,
  className = ''
}: MapLibreViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Initialize MapLibre map
    const initMap = async () => {
      if (!containerRef.current) return;
      
      // Placeholder - actual implementation would use maplibre-gl
      setIsReady(true);
      onMapReady?.({});
    };

    initMap();

    return () => {
      // Cleanup
      if (mapRef.current) {
        // mapRef.current.remove();
      }
    };
  }, []);

  useEffect(() => {
    // Update camera when prop changes
    if (mapRef.current && camera) {
      mapRef.current.jumpTo({
        center: camera.center,
        zoom: camera.zoom,
        bearing: camera.bearing,
        pitch: camera.pitch
      });
    }
  }, [camera]);

  const handleCameraMove = () => {
    if (mapRef.current) {
      const center = mapRef.current.getCenter();
      const newCamera: CameraState = {
        center: [center.lng, center.lat],
        zoom: mapRef.current.getZoom(),
        bearing: mapRef.current.getBearing(),
        pitch: mapRef.current.getPitch()
      };
      onCameraChange?.(newCamera);
    }
  };

  return (
    <div ref={containerRef} className={`maplibre-viewer ${className}`}>
      {!isReady && <div className="viewer-loading">Loading map...</div>}
      {isReady && (
        <div className="map-container">
          {/* MapLibre map would render here */}
          <div className="map-placeholder">MapLibre Vector Map</div>
        </div>
      )}
    </div>
  );
}

// Viewer controls
interface ViewerControlsProps {
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onResetView?: () => void;
  onCompassClick?: () => void;
  onFullscreen?: () => void;
}

export function ViewerControls({
  onZoomIn,
  onZoomOut,
  onResetView,
  onCompassClick,
  onFullscreen
}: ViewerControlsProps) {
  return (
    <div className="viewer-controls">
      <button onClick={onZoomIn} className="control-btn" title="Zoom in">+</button>
      <button onClick={onZoomOut} className="control-btn" title="Zoom out">−</button>
      <button onClick={onCompassClick} className="control-btn" title="Reset rotation">⌂</button>
      <button onClick={onFullscreen} className="control-btn" title="Fullscreen">⛶</button>
    </div>
  );
}

// Navigation controls
interface NavigationControlsProps {
  onLocate?: () => void;
  onMeasure?: () => void;
}

export function NavigationControls({ onLocate, onMeasure }: NavigationControlsProps) {
  return (
    <div className="navigation-controls">
      <button onClick={onLocate} className="nav-btn" title="My location">📍</button>
      <button onClick={onMeasure} className="nav-btn" title="Measure">📏</button>
    </div>
  );
}

// Scale bar
interface ScaleBarProps {
  maxWidth?: number;
  unit?: 'metric' | 'imperial';
}

export function ScaleBar({ maxWidth = 100, unit = 'metric' }: ScaleBarProps) {
  return (
    <div className="scale-bar" style={{ maxWidth }}>
      <div className="scale-bar-fill" style={{ width: '50%' }}></div>
      <div className="scale-bar-labels">
        <span>0</span>
        <span>{unit === 'metric' ? '500m' : '0.5mi'}</span>
      </div>
    </div>
  );
}

// Attribution
interface AttributionProps {
  compact?: boolean;
}

export function Attribution({ compact = true }: AttributionProps) {
  return (
    <div className={`attribution ${compact ? 'compact' : ''}`}>
      © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors
    </div>
  );
}

// Loading indicator
interface MapLoadingProps {
  progress?: number;
}

export function MapLoading({ progress }: MapLoadingProps) {
  return (
    <div className="map-loading">
      <div className="loading-spinner"></div>
      {progress !== undefined && (
        <div className="loading-progress">{progress}%</div>
      )}
    </div>
  );
}

// Error display
interface MapErrorProps {
  message: string;
  onRetry?: () => void;
}

export function MapError({ message, onRetry }: MapErrorProps) {
  return (
    <div className="map-error">
      <span className="error-icon">⚠️</span>
      <p>{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="retry-btn">Retry</button>
      )}
    </div>
  );
}
