/**
 * Analytics Layer Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { AnalyticsLayer, LayerVisibility } from './kepler_types';

interface AnalyticsLayerContextValue {
  layers: AnalyticsLayer[];
  layerVisibility: LayerVisibility[];
  addLayer: (layer: AnalyticsLayer) => void;
  removeLayer: (id: string) => void;
  updateLayer: (id: string, updates: Partial<AnalyticsLayer>) => void;
  getLayer: (id: string) => AnalyticsLayer | undefined;
  setLayerVisibility: (id: string, visible: boolean) => void;
  setLayerOpacity: (id: string, opacity: number) => void;
  reorderLayers: (layerIds: string[]) => void;
}

const AnalyticsLayerContext = createContext<AnalyticsLayerContextValue | undefined>(undefined);

interface AnalyticsLayerProviderProps {
  children: ReactNode;
}

export function AnalyticsLayerProvider({ children }: AnalyticsLayerProviderProps) {
  const [layers, setLayers] = useState<AnalyticsLayer[]>([]);
  const [layerVisibility, setLayerVisibility] = useState<LayerVisibility[]>([]);

  const addLayer = (layer: AnalyticsLayer) => {
    setLayers(prev => [...prev, layer]);
    setLayerVisibility(prev => [
      ...prev,
      { layerId: layer.id, visible: true, opacity: 1 }
    ]);
  };

  const removeLayer = (id: string) => {
    setLayers(prev => prev.filter(l => l.id !== id));
    setLayerVisibility(prev => prev.filter(v => v.layerId !== id));
  };

  const updateLayer = (id: string, updates: Partial<AnalyticsLayer>) => {
    setLayers(prev => prev.map(l => l.id === id ? { ...l, ...updates } : l));
  };

  const getLayer = (id: string) => {
    return layers.find(l => l.id === id);
  };

  const setVisibility = (id: string, visible: boolean) => {
    setLayerVisibility(prev =>
      prev.map(v => v.layerId === id ? { ...v, visible } : v)
    );
  };

  const setOpacity = (id: string, opacity: number) => {
    setLayerVisibility(prev =>
      prev.map(v => v.layerId === id ? { ...v, opacity } : v)
    );
  };

  const reorderLayers = (layerIds: string[]) => {
    setLayers(prev => {
      const layerMap = new Map(prev.map(l => [l.id, l]));
      return layerIds.map((id, index) => {
        const layer = layerMap.get(id);
        return layer ? { ...layer, order: index } as AnalyticsLayer : null;
      }).filter(Boolean) as AnalyticsLayer[];
    });
  };

  const value: AnalyticsLayerContextValue = {
    layers,
    layerVisibility,
    addLayer,
    removeLayer,
    updateLayer,
    getLayer,
    setLayerVisibility: setVisibility,
    setLayerOpacity: setOpacity,
    reorderLayers
  };

  return (
    <AnalyticsLayerContext.Provider value={value}>
      {children}
    </AnalyticsLayerContext.Provider>
  );
}

export function useAnalyticsLayer() {
  const context = useContext(AnalyticsLayerContext);
  if (!context) {
    throw new Error('useAnalyticsLayer must be used within an AnalyticsLayerProvider');
  }
  return context;
}

// Analytics layer operations
export function useAnalyticsLayerOperations() {
  const { addLayer, removeLayer, setLayerVisibility, setLayerOpacity } = useAnalyticsLayer();

  const toggleLayerVisibility = (id: string) => {
    const visibility = useAnalyticsLayer().layerVisibility.find(v => v.layerId === id);
    if (visibility) {
      setLayerVisibility(id, !visibility.visible);
    }
  };

  const getVisibleLayers = () => {
    const { layers, layerVisibility } = useAnalyticsLayer();
    return layers.filter(l => {
      const v = layerVisibility.find(vis => vis.layerId === l.id);
      return v?.visible ?? true;
    });
  };

  return {
    addLayer,
    removeLayer,
    toggleLayerVisibility,
    setLayerOpacity,
    getVisibleLayers
  };
}
