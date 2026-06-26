/**
 * Globe Viewer
 * 
 * Main 3D globe component using Cesium.
 * Part of the dual-view architecture (Leaflet 2D + Cesium 3D).
 */

import React, { useEffect, useRef, useState } from 'react';
import { useCesium } from './CesiumContext';

interface GlobeViewerProps {
  containerId?: string;
  imageryProvider?: any;
  terrainProvider?: any;
  onReady?: () => void;
  onError?: (error: Error) => void;
}

interface GlobeViewerState {
  isReady: boolean;
  error: string | null;
}

export function GlobeViewer({
  containerId = 'cesium-container',
  imageryProvider,
  terrainProvider,
  onReady,
  onError,
}: GlobeViewerProps): JSX.Element {
  const containerRef = useRef<HTMLDivElement>(null);
  const [state, setState] = useState<GlobeViewerState>({
    isReady: false,
    error: null,
  });

  const {
    initializeViewer,
    destroyViewer,
    isInitialized,
    isLoading,
    error,
    viewer,
  } = useCesium();

  useEffect(() => {
    // Initialize Cesium viewer when container is ready
    if (containerRef.current && !isInitialized) {
      initializeViewer(containerId)
        .then(() => {
          setState(prev => ({ ...prev, isReady: true }));
          onReady?.();
        })
        .catch((err: Error) => {
          const errorMsg = err.message || 'Failed to initialize globe';
          setState(prev => ({ ...prev, error: errorMsg }));
          onError?.(err);
        });
    }

    return () => {
      // Cleanup handled by CesiumContext
    };
  }, [containerId, isInitialized, initializeViewer, onReady, onError]);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (isInitialized) {
        destroyViewer();
      }
    };
  }, [isInitialized, destroyViewer]);

  const handleResize = () => {
    // Handle container resize
    if (containerRef.current) {
      const container = containerRef.current;
      const width = container.clientWidth;
      const height = container.clientHeight;
      // In real implementation: viewer?.resize(width, height);
    }
  };

  useEffect(() => {
    // Listen for resize events
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (isLoading) {
    return (
      <div className="cesium-loading">
        <div className="cesium-loading-spinner" />
        <span>Loading 3D Globe...</span>
      </div>
    );
  }

  if (error || state.error) {
    return (
      <div className="cesium-error">
        <h3>Failed to Load 3D Globe</h3>
        <p>{error || state.error}</p>
      </div>
    );
  }

  return (
    <div className="cesium-viewer-container">
      <div
        ref={containerRef}
        id={containerId}
        className="cesium-viewer"
        style={{ width: '100%', height: '100%' }}
      />
      
      {/* Overlay controls */}
      <div className="cesium-controls-overlay">
        <button
          className="cesium-control-btn"
          onClick={handleResize}
          title="Reset View"
        >
          ⟲
        </button>
      </div>
    </div>
  );
}

export default GlobeViewer;
