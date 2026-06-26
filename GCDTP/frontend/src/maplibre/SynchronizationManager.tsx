/**
 * Synchronization Manager
 * Synchronizes state between Leaflet, Cesium, TerriaJS, and MapLibre
 */

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import type { SyncState, CameraState, LayerVisibility } from './maplibre_types';
import { MapViewMode } from './maplibre_types';

interface SyncContextValue {
  currentMode: MapViewMode;
  syncState: SyncState;
  syncEnabled: boolean;
  setCurrentMode: (mode: MapViewMode) => void;
  setSyncEnabled: (enabled: boolean) => void;
  syncCamera: (camera: CameraState) => void;
  syncLayers: (layers: LayerVisibility[]) => void;
  syncSelection: (selection: string[]) => void;
  registerViewer: (mode: MapViewMode, viewer: any) => void;
  unregisterViewer: (mode: MapViewMode) => void;
}

const SyncContext = createContext<SyncContextValue | undefined>(undefined);

interface ViewerRef {
  mode: MapViewMode;
  instance: any;
}

interface SyncProviderProps {
  children: ReactNode;
}

export function SyncProvider({ children }: SyncProviderProps) {
  const [currentMode, setCurrentMode] = useState<MapViewMode>(MapViewMode.MAPLIBRE_VECTOR);
  const [syncState, setSyncState] = useState<SyncState>({
    camera: null,
    layers: [],
    selection: []
  });
  const [syncEnabled, setSyncEnabled] = useState(true);
  const [viewers, setViewers] = useState<Map<MapViewMode, any>>(new Map());

  const registerViewer = useCallback((mode: MapViewMode, viewer: any) => {
    setViewers(prev => {
      const next = new Map(prev);
      next.set(mode, viewer);
      return next;
    });
  }, []);

  const unregisterViewer = useCallback((mode: MapViewMode) => {
    setViewers(prev => {
      const next = new Map(prev);
      next.delete(mode);
      return next;
    });
  }, []);

  const syncCamera = useCallback((camera: CameraState) => {
    if (!syncEnabled) return;
    
    setSyncState(prev => ({ ...prev, camera }));
    
    // Sync to all other viewers
    viewers.forEach((viewer, mode) => {
      if (mode !== currentMode && viewer) {
        viewer.setCamera?.(camera);
      }
    });
  }, [syncEnabled, viewers, currentMode]);

  const syncLayers = useCallback((layers: LayerVisibility[]) => {
    if (!syncEnabled) return;
    
    setSyncState(prev => ({ ...prev, layers }));
    
    // Sync to all other viewers
    viewers.forEach((viewer, mode) => {
      if (mode !== currentMode && viewer) {
        viewer.setLayers?.(layers);
      }
    });
  }, [syncEnabled, viewers, currentMode]);

  const syncSelection = useCallback((selection: string[]) => {
    if (!syncEnabled) return;
    
    setSyncState(prev => ({ ...prev, selection }));
    
    // Sync to all other viewers
    viewers.forEach((viewer, mode) => {
      if (mode !== currentMode && viewer) {
        viewer.setSelection?.(selection);
      }
    });
  }, [syncEnabled, viewers, currentMode]);

  const value: SyncContextValue = {
    currentMode,
    syncState,
    syncEnabled,
    setCurrentMode,
    setSyncEnabled,
    syncCamera,
    syncLayers,
    syncSelection,
    registerViewer,
    unregisterViewer
  };

  return (
    <SyncContext.Provider value={value}>
      {children}
    </SyncContext.Provider>
  );
}

export function useSync() {
  const context = useContext(SyncContext);
  if (!context) {
    throw new Error('useSync must be used within a SyncProvider');
  }
  return context;
}

// Sync with Leaflet
export function useLeafletSync() {
  const { registerViewer, unregisterViewer, syncCamera } = useSync();
  const [leafletViewer, setLeafletViewer] = useState<any>(null);

  const register = useCallback((viewer: any) => {
    setLeafletViewer(viewer);
    registerViewer(MapViewMode.LEAFLET_2D, viewer);
  }, [registerViewer]);

  const unregister = useCallback(() => {
    unregisterViewer(MapViewMode.LEAFLET_2D);
    setLeafletViewer(null);
  }, [unregisterViewer]);

  const onCameraChange = useCallback((camera: CameraState) => {
    syncCamera(camera);
  }, [syncCamera]);

  return { register, unregister, onCameraChange };
}

// Sync with Cesium
export function useCesiumSync() {
  const { registerViewer, unregisterViewer, syncCamera } = useSync();
  const [cesiumViewer, setCesiumViewer] = useState<any>(null);

  const register = useCallback((viewer: any) => {
    setCesiumViewer(viewer);
    registerViewer(MapViewMode.CESIUM_3D, viewer);
  }, [registerViewer]);

  const unregister = useCallback(() => {
    unregisterViewer(MapViewMode.CESIUM_3D);
    setCesiumViewer(null);
  }, [unregisterViewer]);

  const onCameraChange = useCallback((camera: CameraState) => {
    syncCamera(camera);
  }, [syncCamera]);

  return { register, unregister, onCameraChange };
}

// Sync with TerriaJS
export function useTerriaSync() {
  const { registerViewer, unregisterViewer, syncCamera, syncLayers } = useSync();
  const [terriaViewer, setTerriaViewer] = useState<any>(null);

  const register = useCallback((viewer: any) => {
    setTerriaViewer(viewer);
    registerViewer(MapViewMode.TERRA_FEDERATION, viewer);
  }, [registerViewer]);

  const unregister = useCallback(() => {
    unregisterViewer(MapViewMode.TERRA_FEDERATION);
    setTerriaViewer(null);
  }, [unregisterViewer]);

  const onCameraChange = useCallback((camera: CameraState) => {
    syncCamera(camera);
  }, [syncCamera]);

  const onLayersChange = useCallback((layers: LayerVisibility[]) => {
    syncLayers(layers);
  }, [syncLayers]);

  return { register, unregister, onCameraChange, onLayersChange };
}
