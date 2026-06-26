/**
 * Kepler.gl Context Provider
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { KeplerConfig, CameraState, KeplerDataset, SyncState } from './kepler_types';

interface KeplerContextValue {
  config: KeplerConfig;
  setConfig: (config: KeplerConfig) => void;
  datasets: KeplerDataset[];
  addDataset: (dataset: KeplerDataset) => void;
  removeDataset: (id: string) => void;
  camera: CameraState | null;
  setCamera: (camera: CameraState) => void;
  syncState: SyncState;
  updateSyncState: (state: Partial<SyncState>) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

const defaultConfig: KeplerConfig = {
  appName: 'GCDTP Analytics'
};

const KeplerContext = createContext<KeplerContextValue | undefined>(undefined);

interface KeplerProviderProps {
  children: ReactNode;
  initialConfig?: KeplerConfig;
}

export function KeplerProvider({ children, initialConfig }: KeplerProviderProps) {
  const [config, setConfig] = useState<KeplerConfig>(initialConfig || defaultConfig);
  const [datasets, setDatasets] = useState<KeplerDataset[]>([]);
  const [camera, setCamera] = useState<CameraState | null>(null);
  const [syncState, setSyncState] = useState<SyncState>({
    camera: null,
    layers: [],
    filters: [],
    timeWindow: null
  });
  const [isLoading, setIsLoading] = useState(false);

  const updateSyncState = (state: Partial<SyncState>) => {
    setSyncState(prev => ({ ...prev, ...state }));
  };

  const addDataset = (dataset: KeplerDataset) => {
    setDatasets(prev => [...prev, dataset]);
  };

  const removeDataset = (id: string) => {
    setDatasets(prev => prev.filter(d => d.id !== id));
  };

  const value: KeplerContextValue = {
    config,
    setConfig,
    datasets,
    addDataset,
    removeDataset,
    camera,
    setCamera,
    syncState,
    updateSyncState,
    isLoading,
    setIsLoading
  };

  return (
    <KeplerContext.Provider value={value}>
      {children}
    </KeplerContext.Provider>
  );
}

export function useKepler() {
  const context = useContext(KeplerContext);
  if (!context) {
    throw new Error('useKepler must be used within a KeplerProvider');
  }
  return context;
}

export function useDatasets() {
  const { datasets, addDataset, removeDataset } = useKepler();
  
  return {
    datasets,
    addDataset,
    removeDataset,
    getDataset: (id: string) => datasets.find(d => d.id === id)
  };
}

export function useKeplerCamera() {
  const { camera, setCamera } = useKepler();
  
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
    }
  };
}
