/**
 * Camera Controller
 * 
 * Camera controls for 3D globe navigation.
 * Supports zoom, pan, rotate, fly-to, and route following.
 * Part of the dual-view architecture (Leaflet 2D + Cesium 3D).
 */

import React, { useState, useCallback, useEffect } from 'react';
import { useCesium } from './CesiumContext';

// Position type for camera
interface CameraPosition {
  longitude: number;
  latitude: number;
  height: number;
  heading?: number;
  pitch?: number;
  roll?: number;
}

interface RoutePoint {
  position: CameraPosition;
  duration?: number;
}

interface CameraControllerProps {
  onPositionChange?: (position: CameraPosition) => void;
  enableKeyboardControls?: boolean;
}

// Available camera presets
const CAMERA_PRESETS: Record<string, CameraPosition> = {
  'default': {
    longitude: -75.59777,
    latitude: 40.038503,
    height: 15000000,
    heading: 0,
    pitch: -90,
  },
  'north-america': {
    longitude: -100,
    latitude: 45,
    height: 20000000,
    heading: 0,
    pitch: -90,
  },
  'europe': {
    longitude: 10,
    latitude: 50,
    height: 15000000,
    heading: 0,
    pitch: -90,
  },
  'asia': {
    longitude: 100,
    latitude: 35,
    height: 20000000,
    heading: 0,
    pitch: -90,
  },
  'australia': {
    longitude: 135,
    latitude: -25,
    height: 15000000,
    heading: 0,
    pitch: -90,
  },
};

export function CameraController({
  onPositionChange,
  enableKeyboardControls = true,
}: CameraControllerProps): JSX.Element {
  const { 
    flyTo, 
    zoomIn, 
    zoomOut, 
    resetCamera, 
    focusAsset,
    viewer 
  } = useCesium();
  
  const [currentPosition, setCurrentPosition] = useState<CameraPosition>(CAMERA_PRESETS['default']);
  const [isAnimating, setIsAnimating] = useState(false);

  // Update position when camera changes
  useEffect(() => {
    if (viewer) {
      const handleMove = () => {
        // Get current camera position
        // const position = viewer.camera.position;
        const position = currentPosition; // Placeholder
        setCurrentPosition(position);
        onPositionChange?.(position);
      };

      // Attach camera move listener
      // viewer.camera.changed.addEventListener(handleMove);

      return () => {
        // viewer.camera.changed.removeEventListener(handleMove);
      };
    }
  }, [viewer, onPositionChange]);

  // Fly to position
  const handleFlyTo = useCallback((position: CameraPosition) => {
    setIsAnimating(true);
    flyTo(
      { x: position.longitude, y: position.latitude, z: position.height },
      position.heading,
      position.pitch
    );
    setTimeout(() => setIsAnimating(false), 1000);
  }, [flyTo]);

  // Zoom handlers
  const handleZoomIn = useCallback(() => {
    zoomIn();
  }, [zoomIn]);

  const handleZoomOut = useCallback(() => {
    zoomOut();
  }, [zoomOut]);

  // Reset camera
  const handleReset = useCallback(() => {
    resetCamera();
    setCurrentPosition(CAMERA_PRESETS['default']);
  }, [resetCamera]);

  // Focus on asset
  const handleFocusAsset = useCallback((assetId: string, position: CameraPosition) => {
    focusAsset(assetId, { 
      x: position.longitude, 
      y: position.latitude, 
      z: position.height 
    });
  }, [focusAsset]);

  // Go to preset
  const handleGoToPreset = useCallback((preset: string) => {
    if (CAMERA_PRESETS[preset]) {
      handleFlyTo(CAMERA_PRESETS[preset]);
    }
  }, [handleFlyTo]);

  // Follow route animation
  const followRoute = useCallback(async (route: RoutePoint[]) => {
    setIsAnimating(true);
    
    for (const point of route) {
      await new Promise<void>((resolve) => {
        handleFlyTo(point.position);
        setTimeout(resolve, (point.duration || 2) * 1000);
      });
    }
    
    setIsAnimating(false);
  }, [handleFlyTo]);

  return (
    <div className="camera-controller">
      {/* Zoom Controls */}
      <div className="camera-zoom-controls">
        <button 
          className="camera-btn zoom-in"
          onClick={handleZoomIn}
          title="Zoom In"
          disabled={isAnimating}
        >
          +
        </button>
        <button 
          className="camera-btn zoom-out"
          onClick={handleZoomOut}
          title="Zoom Out"
          disabled={isAnimating}
        >
          −
        </button>
      </div>

      {/* Reset Button */}
      <button 
        className="camera-btn reset"
        onClick={handleReset}
        title="Reset Camera"
        disabled={isAnimating}
      >
        ⟲
      </button>

      {/* Preset Positions */}
      <div className="camera-presets">
        <button 
          className="preset-btn"
          onClick={() => handleGoToPreset('north-america')}
          title="North America"
        >
          NA
        </button>
        <button 
          className="preset-btn"
          onClick={() => handleGoToPreset('europe')}
          title="Europe"
        >
          EU
        </button>
        <button 
          className="preset-btn"
          onClick={() => handleGoToPreset('asia')}
          title="Asia"
        >
          AS
        </button>
        <button 
          className="preset-btn"
          onClick={() => handleGoToPreset('australia')}
          title="Australia"
        >
          AU
        </button>
      </div>

      {/* Current Position Display */}
      <div className="camera-position">
        <span>Lon: {currentPosition.longitude.toFixed(4)}</span>
        <span>Lat: {currentPosition.latitude.toFixed(4)}</span>
        <span>Alt: {(currentPosition.height / 1000).toFixed(0)}km</span>
      </div>
    </div>
  );
}

// Hook for programmatic camera control
export function useCameraControls() {
  const { flyTo, zoomIn, zoomOut, resetCamera, focusAsset } = useCesium();

  const flyToPosition = useCallback((position: CameraPosition) => {
    flyTo(
      { x: position.longitude, y: position.latitude, z: position.height },
      position.heading,
      position.pitch
    );
  }, [flyTo]);

  const zoomInBy = useCallback((factor: number = 0.5) => {
    zoomIn();
  }, [zoomIn]);

  const zoomOutBy = useCallback((factor: number = 2) => {
    zoomOut();
  }, [zoomOut]);

  const flyToAsset = useCallback((assetId: string, position: CameraPosition) => {
    focusAsset(assetId, { 
      x: position.longitude, 
      y: position.latitude, 
      z: position.height 
    });
  }, [focusAsset]);

  const homeView = useCallback(() => {
    resetCamera();
  }, [resetCamera]);

  return {
    flyToPosition,
    zoomInBy,
    zoomOutBy,
    flyToAsset,
    homeView,
    zoomIn,
    zoomOut,
    resetCamera,
  };
}

export default CameraController;
