/**
 * TerriaJS Context Provider
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type {
  TerriaConfig,
  CatalogItem,
  CameraPosition,
  ViewMode
} from './terria_types';

interface TerriaContextValue {
  config: TerriaConfig;
  setConfig: (config: TerriaConfig) => void;
  catalogItems: CatalogItem[];
  setCatalogItems: (items: CatalogItem[]) => void;
  cameraPosition: CameraPosition | null;
  setCameraPosition: (position: CameraPosition) => void;
  viewMode: ViewMode;
  setViewMode: (mode: ViewMode) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

const defaultConfig: TerriaConfig = {
  appName: 'GCDTP',
  useCesiumIonTerrain: true
};

const TerriaContext = createContext<TerriaContextValue | undefined>(undefined);

interface TerriaProviderProps {
  children: ReactNode;
  initialConfig?: TerriaConfig;
}

export function TerriaProvider({ children, initialConfig }: TerriaProviderProps) {
  const [config, setConfig] = useState<TerriaConfig>(initialConfig || defaultConfig);
  const [catalogItems, setCatalogItems] = useState<CatalogItem[]>([]);
  const [cameraPosition, setCameraPosition] = useState<CameraPosition | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>(ViewMode.CESIUM_3D);
  const [isLoading, setIsLoading] = useState(false);

  const value: TerriaContextValue = {
    config,
    setConfig,
    catalogItems,
    setCatalogItems,
    cameraPosition,
    setCameraPosition,
    viewMode,
    setViewMode,
    isLoading,
    setIsLoading
  };

  return (
    <TerriaContext.Provider value={value}>
      {children}
    </TerriaContext.Provider>
  );
}

export function useTerria() {
  const context = useContext(TerriaContext);
  if (!context) {
    throw new Error('useTerria must be used within a TerriaProvider');
  }
  return context;
}

export function useCatalog() {
  const { catalogItems, setCatalogItems } = useTerria();
  
  return {
    items: catalogItems,
    setItems: setCatalogItems,
    addItem: (item: CatalogItem) => {
      setCatalogItems([...catalogItems, item]);
    },
    removeItem: (id: string) => {
      setCatalogItems(catalogItems.filter(item => item.id !== id));
    },
    getItem: (id: string) => {
      return catalogItems.find(item => item.id === id);
    }
  };
}

export function useCamera() {
  const { cameraPosition, setCameraPosition } = useTerria();
  
  return {
    position: cameraPosition,
    setPosition: setCameraPosition,
    flyTo: (position: CameraPosition) => {
      setCameraPosition(position);
    }
  };
}

export function useViewMode() {
  const { viewMode, setViewMode } = useTerria();
  
  return {
    mode: viewMode,
    setMode: setViewMode,
    isLeaflet: viewMode === ViewMode.LEAFLET_2D,
    isCesium: viewMode === ViewMode.CESIUM_3D,
    isTerria: viewMode === ViewMode.TERRA_FEDERATION
  };
}
