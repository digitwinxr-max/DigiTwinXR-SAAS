/**
 * Layer Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { VectorLayer, RasterLayer, LayerVisibility } from './maplibre_types';

interface LayerItem {
  id: string;
  name: string;
  type: 'vector' | 'raster' | 'terrain' | 'overlay';
  sourceId?: string;
  visible: boolean;
  opacity: number;
  order: number;
}

interface LayerContextValue {
  layers: LayerItem[];
  addLayer: (layer: LayerItem) => void;
  removeLayer: (id: string) => void;
  updateLayer: (id: string, updates: Partial<LayerItem>) => void;
  getLayer: (id: string) => LayerItem | undefined;
  reorderLayers: (layerIds: string[]) => void;
  setLayerVisibility: (id: string, visible: boolean) => void;
  setLayerOpacity: (id: string, opacity: number) => void;
  getVisibleLayers: () => LayerItem[];
}

const LayerContext = createContext<LayerContextValue | undefined>(undefined);

interface LayerProviderProps {
  children: ReactNode;
}

export function LayerProvider({ children }: LayerProviderProps) {
  const [layers, setLayers] = useState<LayerItem[]>([]);

  const addLayer = (layer: LayerItem) => {
    setLayers(prev => [...prev, layer]);
  };

  const removeLayer = (id: string) => {
    setLayers(prev => prev.filter(l => l.id !== id));
  };

  const updateLayer = (id: string, updates: Partial<LayerItem>) => {
    setLayers(prev => prev.map(l => l.id === id ? { ...l, ...updates } : l));
  };

  const getLayer = (id: string) => {
    return layers.find(l => l.id === id);
  };

  const reorderLayers = (layerIds: string[]) => {
    setLayers(prev => {
      const layerMap = new Map(prev.map(l => [l.id, l]));
      return layerIds.map((id, index) => {
        const layer = layerMap.get(id);
        return layer ? { ...layer, order: index } : null;
      }).filter(Boolean) as LayerItem[];
    });
  };

  const setLayerVisibility = (id: string, visible: boolean) => {
    updateLayer(id, { visible });
  };

  const setLayerOpacity = (id: string, opacity: number) => {
    updateLayer(id, { opacity: Math.max(0, Math.min(1, opacity)) });
  };

  const getVisibleLayers = () => {
    return layers.filter(l => l.visible).sort((a, b) => a.order - b.order);
  };

  const value: LayerContextValue = {
    layers,
    addLayer,
    removeLayer,
    updateLayer,
    getLayer,
    reorderLayers,
    setLayerVisibility,
    setLayerOpacity,
    getVisibleLayers
  };

  return (
    <LayerContext.Provider value={value}>
      {children}
    </LayerContext.Provider>
  );
}

export function useLayer() {
  const context = useContext(LayerContext);
  if (!context) {
    throw new Error('useLayer must be used within a LayerProvider');
  }
  return context;
}

// Layer type hooks
export function useVectorLayers() {
  const { layers } = useLayer();
  return layers.filter(l => l.type === 'vector');
}

export function useRasterLayers() {
  const { layers } = useLayer();
  return layers.filter(l => l.type === 'raster');
}

export function useTerrainLayers() {
  const { layers } = useLayer();
  return layers.filter(l => l.type === 'terrain');
}

export function useOverlayLayers() {
  const { layers } = useLayer();
  return layers.filter(l => l.type === 'overlay');
}

// Layer operations
export function useLayerOperations() {
  const { addLayer, removeLayer, setLayerVisibility, setLayerOpacity } = useLayer();

  const addVectorLayer = (id: string, name: string, sourceId: string) => {
    addLayer({
      id,
      name,
      type: 'vector',
      sourceId,
      visible: true,
      opacity: 1,
      order: Date.now()
    });
  };

  const addRasterLayer = (id: string, name: string, sourceId: string) => {
    addLayer({
      id,
      name,
      type: 'raster',
      sourceId,
      visible: true,
      opacity: 1,
      order: Date.now()
    });
  };

  const addTerrainLayer = (id: string, name: string) => {
    addLayer({
      id,
      name,
      type: 'terrain',
      visible: true,
      opacity: 1,
      order: Date.now()
    });
  };

  const addOverlayLayer = (id: string, name: string) => {
    addLayer({
      id,
      name,
      type: 'overlay',
      visible: true,
      opacity: 1,
      order: Date.now()
    });
  };

  return {
    addVectorLayer,
    addRasterLayer,
    addTerrainLayer,
    addOverlayLayer,
    removeLayer,
    toggleVisibility: (id: string) => {
      const layer = useLayer().getLayer(id);
      if (layer) setLayerVisibility(id, !layer.visible);
    },
    setOpacity: setLayerOpacity
  };
}
