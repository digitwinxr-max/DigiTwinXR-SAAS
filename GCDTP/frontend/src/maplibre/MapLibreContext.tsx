/**
 * MapLibre Context Provider
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type {
  MapLibreConfig,
  CameraState,
  MapStyle,
  SyncState
} from './maplibre_types';

interface MapLibreContextValue {
  config: MapLibreConfig;
  setConfig: (config: MapLibreConfig) => void;
  camera: CameraState | null;
  setCamera: (camera: CameraState) => void;
  style: MapStyle | null;
  setStyle: (style: MapStyle) => void;
  syncState: SyncState;
  updateSyncState: (state: Partial<SyncState>) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

const defaultConfig: MapLibreConfig = {
  style: 'https://demotiles.maplibre.org/style.json',
  center: [0, 0],
  zoom: 2
};

const MapLibreContext = createContext<MapLibreContextValue | undefined>(undefined);

interface MapLibreProviderProps {
  children: ReactNode;
  initialConfig?: MapLibreConfig;
}

export function MapLibreProvider({ children, initialConfig }: MapLibreProviderProps) {
  const [config, setConfig] = useState<MapLibreConfig>(initialConfig || defaultConfig);
  const [camera, setCamera] = useState<CameraState | null>(null);
  const [style, setStyle] = useState<MapStyle | null>(null);
  const [syncState, setSyncState] = useState<SyncState>({
    camera: null,
    layers: [],
    selection: []
  });
  const [isLoading, setIsLoading] = useState(false);

  const updateSyncState = (state: Partial<SyncState>) => {
    setSyncState(prev => ({ ...prev, ...state }));
  };

  const value: MapLibreContextValue = {
    config,
    setConfig,
    camera,
    setCamera,
    style,
    setStyle,
    syncState,
    updateSyncState,
    isLoading,
    setIsLoading
  };

  return (
    <MapLibreContext.Provider value={value}>
      {children}
    </MapLibreContext.Provider>
  );
}

export function useMapLibre() {
  const context = useContext(MapLibreContext);
  if (!context) {
    throw new Error('useMapLibre must be used within a MapLibreProvider');
  }
  return context;
}

export function useMapCamera() {
  const { camera, setCamera } = useMapLibre();
  
  return {
    camera,
    setCamera,
    flyTo: (center: [number, number], zoom?: number) => {
      setCamera({
        center,
        zoom: zoom || camera?.zoom || 10,
        bearing: 0,
        pitch: 0
      });
    },
    zoomIn: () => {
      if (camera) {
        setCamera({ ...camera, zoom: Math.min(camera.zoom + 1, 22) });
      }
    },
    zoomOut: () => {
      if (camera) {
        setCamera({ ...camera, zoom: Math.max(camera.zoom - 1, 0) });
      }
    }
  };
}

export function useMapStyle() {
  const { style, setStyle } = useMapLibre();
  
  return {
    style,
    setStyle,
    updateStyle: (updates: Partial<MapStyle>) => {
      if (style) {
        setStyle({ ...style, ...updates });
      }
    }
  };
}
