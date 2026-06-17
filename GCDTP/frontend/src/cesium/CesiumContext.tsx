/**
 * Cesium Context
 * 
 * React context for managing Cesium viewer, scene, camera, terrain, entities, and timeline.
 * Part of the dual-view architecture (Leaflet 2D + Cesium 3D).
 */

import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';

// Cesium viewer type (simplified - actual Cesium types would be imported in real implementation)
interface CesiumViewer {
  id: string;
  scene: CesiumScene;
  camera: CesiumCamera;
  terrainProvider: any;
  entities: CesiumEntityCollection;
}

interface CesiumScene {
  id: string;
  mode: '3D' | '2D';
  globe: any;
 太阳穴: any;
}

interface CesiumCamera {
  position: CesiumCartesian3;
  heading: number;
  pitch: number;
  roll: number;
}

interface CesiumCartesian3 {
  x: number;
  y: number;
  z: number;
}

interface CesiumEntityCollection {
  add(entity: any): any;
  remove(entity: any): void;
  removeAll(): void;
  getById(id: string): any;
}

interface CesiumEntity {
  id: string;
  position?: CesiumCartesian3;
  properties?: Record<string, any>;
}

// Timeline state for ADR-0025 integration
interface TimelineState {
  isPlaying: boolean;
  currentTime: Date | null;
  speed: number;
  events: CesiumEntity[];
}

// Cesium context state
interface CesiumState {
  viewer: CesiumViewer | null;
  isInitialized: boolean;
  isLoading: boolean;
  error: string | null;
  sceneMode: '3D' | '2D';
  timeline: TimelineState;
  selectedEntity: CesiumEntity | null;
}

// Cesium context actions
interface CesiumActions {
  initializeViewer: (containerId: string) => Promise<void>;
  destroyViewer: () => void;
  setSceneMode: (mode: '3D' | '2D') => void;
  flyTo: (position: CesiumCartesian3, heading?: number, pitch?: number) => void;
  zoomIn: () => void;
  zoomOut: () => void;
  resetCamera: () => void;
  focusAsset: (assetId: string, position: CesiumCartesian3) => void;
  addEntity: (entity: CesiumEntity) => void;
  removeEntity: (entityId: string) => void;
  clearEntities: () => void;
  selectEntity: (entity: CesiumEntity | null) => void;
  loadTerrain: (provider: any) => void;
  load3DTiles: (url: string, options?: any) => void;
  // Timeline actions (ADR-0025 integration)
  playTimeline: () => void;
  pauseTimeline: () => void;
  seekTimeline: (time: Date) => void;
  setTimelineSpeed: (speed: number) => void;
}

type CesiumContextType = CesiumState & CesiumActions;

const CesiumContext = createContext<CesiumContextType | null>(null);

interface CesiumProviderProps {
  children: ReactNode;
}

export function CesiumProvider({ children }: CesiumProviderProps): JSX.Element {
  const [viewer, setViewer] = useState<CesiumViewer | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sceneMode, setSceneMode] = useState<'3D' | '2D'>('3D');
  const [selectedEntity, setSelectedEntity] = useState<CesiumEntity | null>(null);
  
  const [timeline, setTimeline] = useState<TimelineState>({
    isPlaying: false,
    currentTime: null,
    speed: 1.0,
    events: [],
  });

  const initializeViewer = useCallback(async (containerId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // In a real implementation, this would initialize Cesium
      // import Cesium from 'cesium';
      // const cesiumViewer = new Cesium.Viewer(containerId, {...});
      
      const mockViewer: CesiumViewer = {
        id: `cesium-${Date.now()}`,
        scene: {
          id: 'main-scene',
          mode: '3D',
          globe: {},
        },
        camera: {
          position: { x: 0, y: 0, z: 20000000 },
          heading: 0,
          pitch: -90,
          roll: 0,
        },
        terrainProvider: null,
        entities: {
          add: (entity: any) => entity,
          remove: (entity: any) => {},
          removeAll: () => {},
          getById: (id: string) => null,
        },
      };
      
      setViewer(mockViewer);
      setIsInitialized(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initialize Cesium viewer');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const destroyViewer = useCallback(() => {
    if (viewer) {
      // Cleanup Cesium resources
      setViewer(null);
      setIsInitialized(false);
      setSelectedEntity(null);
    }
  }, [viewer]);

  const setSceneModeHandler = useCallback((mode: '3D' | '2D') => {
    setSceneMode(mode);
    if (viewer) {
      viewer.scene.mode = mode;
    }
  }, [viewer]);

  const flyTo = useCallback((position: CesiumCartesian3, heading?: number, pitch?: number) => {
    if (viewer) {
      viewer.camera.position = position;
      if (heading !== undefined) viewer.camera.heading = heading;
      if (pitch !== undefined) viewer.camera.pitch = pitch;
    }
  }, [viewer]);

  const zoomIn = useCallback(() => {
    if (viewer) {
      const currentZ = viewer.camera.position.z;
      viewer.camera.position = {
        ...viewer.camera.position,
        z: currentZ * 0.5,
      };
    }
  }, [viewer]);

  const zoomOut = useCallback(() => {
    if (viewer) {
      const currentZ = viewer.camera.position.z;
      viewer.camera.position = {
        ...viewer.camera.position,
        z: currentZ * 2,
      };
    }
  }, [viewer]);

  const resetCamera = useCallback(() => {
    if (viewer) {
      viewer.camera.position = { x: 0, y: 0, z: 20000000 };
      viewer.camera.heading = 0;
      viewer.camera.pitch = -90;
      viewer.camera.roll = 0;
    }
  }, [viewer]);

  const focusAsset = useCallback((assetId: string, position: CesiumCartesian3) => {
    flyTo(position, 0, -45);
    const entity = viewer?.entities.getById(assetId);
    if (entity) {
      setSelectedEntity(entity);
    }
  }, [viewer, flyTo]);

  const addEntity = useCallback((entity: CesiumEntity) => {
    if (viewer) {
      viewer.entities.add(entity);
    }
  }, [viewer]);

  const removeEntity = useCallback((entityId: string) => {
    if (viewer) {
      const entity = viewer.entities.getById(entityId);
      if (entity) {
        viewer.entities.remove(entity);
      }
    }
  }, [viewer]);

  const clearEntities = useCallback(() => {
    if (viewer) {
      viewer.entities.removeAll();
    }
  }, [viewer]);

  const selectEntityHandler = useCallback((entity: CesiumEntity | null) => {
    setSelectedEntity(entity);
  }, []);

  const loadTerrain = useCallback((provider: any) => {
    if (viewer) {
      viewer.terrainProvider = provider;
    }
  }, [viewer]);

  const load3DTiles = useCallback((url: string, options?: any) => {
    // In real implementation:
    // const tileset = viewer.scene.primitives.add(Cesium.create3DTileset(url));
    console.log('Loading 3D Tiles from:', url);
  }, []);

  // Timeline actions (ADR-0025 integration)
  const playTimeline = useCallback(() => {
    setTimeline(prev => ({ ...prev, isPlaying: true }));
  }, []);

  const pauseTimeline = useCallback(() => {
    setTimeline(prev => ({ ...prev, isPlaying: false }));
  }, []);

  const seekTimeline = useCallback((time: Date) => {
    setTimeline(prev => ({ ...prev, currentTime: time }));
  }, []);

  const setTimelineSpeed = useCallback((speed: number) => {
    setTimeline(prev => ({ ...prev, speed }));
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      destroyViewer();
    };
  }, [destroyViewer]);

  const value: CesiumContextType = {
    viewer,
    isInitialized,
    isLoading,
    error,
    sceneMode,
    timeline,
    selectedEntity,
    initializeViewer,
    destroyViewer,
    setSceneMode: setSceneModeHandler,
    flyTo,
    zoomIn,
    zoomOut,
    resetCamera,
    focusAsset,
    addEntity,
    removeEntity,
    clearEntities,
    selectEntity: selectEntityHandler,
    loadTerrain,
    load3DTiles,
    playTimeline,
    pauseTimeline,
    seekTimeline,
    setTimelineSpeed,
  };

  return (
    <CesiumContext.Provider value={value}>
      {children}
    </CesiumContext.Provider>
  );
}

export function useCesium(): CesiumContextType {
  const context = useContext(CesiumContext);
  if (!context) {
    throw new Error('useCesium must be used within a CesiumProvider');
  }
  return context;
}

export default CesiumContext;
