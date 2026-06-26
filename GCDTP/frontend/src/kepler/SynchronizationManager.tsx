/**
 * Kepler Synchronization Manager
 */

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import type { CameraState, LayerVisibility, FilterConfig, TimeWindow, AnalyticsViewMode } from './kepler_types';

interface KeplerSyncContextValue {
  currentMode: AnalyticsViewMode;
  syncEnabled: boolean;
  camera: CameraState | null;
  layers: LayerVisibility[];
  filters: FilterConfig[];
  timeWindow: TimeWindow | null;
  setCurrentMode: (mode: AnalyticsViewMode) => void;
  setSyncEnabled: (enabled: boolean) => void;
  syncCamera: (camera: CameraState) => void;
  syncLayers: (layers: LayerVisibility[]) => void;
  syncFilters: (filters: FilterConfig[]) => void;
  syncTimeWindow: (window: TimeWindow) => void;
  registerViewer: (mode: AnalyticsViewMode, viewer: any) => void;
  unregisterViewer: (mode: AnalyticsViewMode) => void;
}

const KeplerSyncContext = createContext<KeplerSyncContextValue | undefined>(undefined);

interface ViewerRef {
  mode: AnalyticsViewMode;
  instance: any;
}

interface KeplerSyncProviderProps {
  children: ReactNode;
}

export function KeplerSyncProvider({ children }: KeplerSyncProviderProps) {
  const [currentMode, setCurrentMode] = useState<AnalyticsViewMode>(AnalyticsViewMode.KEPLER_ANALYTICS);
  const [syncEnabled, setSyncEnabled] = useState(true);
  const [camera, setCamera] = useState<CameraState | null>(null);
  const [layers, setLayers] = useState<LayerVisibility[]>([]);
  const [filters, setFilters] = useState<FilterConfig[]>([]);
  const [timeWindow, setTimeWindow] = useState<TimeWindow | null>(null);
  const [viewers, setViewers] = useState<Map<AnalyticsViewMode, any>>(new Map());

  const registerViewer = useCallback((mode: AnalyticsViewMode, viewer: any) => {
    setViewers(prev => {
      const next = new Map(prev);
      next.set(mode, viewer);
      return next;
    });
  }, []);

  const unregisterViewer = useCallback((mode: AnalyticsViewMode) => {
    setViewers(prev => {
      const next = new Map(prev);
      next.delete(mode);
      return next;
    });
  }, []);

  const syncCamera = useCallback((newCamera: CameraState) => {
    if (!syncEnabled) return;
    
    setCamera(newCamera);
    
    viewers.forEach((viewer, mode) => {
      if (mode !== currentMode && viewer) {
        viewer.setCamera?.(newCamera);
      }
    });
  }, [syncEnabled, viewers, currentMode]);

  const syncLayers = useCallback((newLayers: LayerVisibility[]) => {
    if (!syncEnabled) return;
    
    setLayers(newLayers);
    
    viewers.forEach((viewer, mode) => {
      if (mode !== currentMode && viewer) {
        viewer.setLayers?.(newLayers);
      }
    });
  }, [syncEnabled, viewers, currentMode]);

  const syncFilters = useCallback((newFilters: FilterConfig[]) => {
    if (!syncEnabled) return;
    
    setFilters(newFilters);
  }, [syncEnabled]);

  const syncTimeWindow = useCallback((newWindow: TimeWindow) => {
    if (!syncEnabled) return;
    
    setTimeWindow(newWindow);
    
    viewers.forEach((viewer, mode) => {
      if (mode !== currentMode && viewer) {
        viewer.setTimeWindow?.(newWindow);
      }
    });
  }, [syncEnabled, viewers, currentMode]);

  const value: KeplerSyncContextValue = {
    currentMode,
    syncEnabled,
    camera,
    layers,
    filters,
    timeWindow,
    setCurrentMode,
    setSyncEnabled,
    syncCamera,
    syncLayers,
    syncFilters,
    syncTimeWindow,
    registerViewer,
    unregisterViewer
  };

  return (
    <KeplerSyncContext.Provider value={value}>
      {children}
    </KeplerSyncContext.Provider>
  );
}

export function useKeplerSync() {
  const context = useContext(KeplerSyncContext);
  if (!context) {
    throw new Error('useKeplerSync must be used within a KeplerSyncProvider');
  }
  return context;
}

// Viewer sync hooks
export function useLeafletSync() {
  const { registerViewer, unregisterViewer, syncCamera } = useKeplerSync();
  const [leafletViewer, setLeafletViewer] = useState<any>(null);

  const register = useCallback((viewer: any) => {
    setLeafletViewer(viewer);
    registerViewer(AnalyticsViewMode.LEAFLET_2D, viewer);
  }, [registerViewer]);

  const unregister = useCallback(() => {
    unregisterViewer(AnalyticsViewMode.LEAFLET_2D);
    setLeafletViewer(null);
  }, [unregisterViewer]);

  return { register, unregister };
}

export function useMapLibreSync() {
  const { registerViewer, unregisterViewer, syncCamera } = useKeplerSync();
  const [maplibreViewer, setMaplibreViewer] = useState<any>(null);

  const register = useCallback((viewer: any) => {
    setMaplibreViewer(viewer);
    registerViewer(AnalyticsViewMode.MAPLIBRE_VECTOR, viewer);
  }, [registerViewer]);

  const unregister = useCallback(() => {
    unregisterViewer(AnalyticsViewMode.MAPLIBRE_VECTOR);
    setMaplibreViewer(null);
  }, [unregisterViewer]);

  return { register, unregister };
}

export function useCesiumSync() {
  const { registerViewer, unregisterViewer, syncCamera } = useKeplerSync();
  const [cesiumViewer, setCesiumViewer] = useState<any>(null);

  const register = useCallback((viewer: any) => {
    setCesiumViewer(viewer);
    registerViewer(AnalyticsViewMode.CESIUM_3D, viewer);
  }, [registerViewer]);

  const unregister = useCallback(() => {
    unregisterViewer(AnalyticsViewMode.CESIUM_3D);
    setCesiumViewer(null);
  }, [unregisterViewer]);

  return { register, unregister };
}

export function useTerriaSync() {
  const { registerViewer, unregisterViewer, syncCamera, syncLayers } = useKeplerSync();
  const [terriaViewer, setTerriaViewer] = useState<any>(null);

  const register = useCallback((viewer: any) => {
    setTerriaViewer(viewer);
    registerViewer(AnalyticsViewMode.TERRA_FEDERATION, viewer);
  }, [registerViewer]);

  const unregister = useCallback(() => {
    unregisterViewer(AnalyticsViewMode.TERRA_FEDERATION);
    setTerriaViewer(null);
  }, [unregisterViewer]);

  return { register, unregister };
}
