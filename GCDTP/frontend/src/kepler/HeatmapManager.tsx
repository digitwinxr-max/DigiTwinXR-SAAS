/**
 * Heatmap Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { HeatmapLayer, HeatmapConfig } from './kepler_types';

interface HeatmapContextValue {
  heatmaps: HeatmapLayer[];
  addHeatmap: (heatmap: HeatmapLayer) => void;
  removeHeatmap: (id: string) => void;
  updateHeatmap: (id: string, updates: Partial<HeatmapLayer>) => void;
  getHeatmap: (id: string) => HeatmapLayer | undefined;
}

const HeatmapContext = createContext<HeatmapContextValue | undefined>(undefined);

interface HeatmapProviderProps {
  children: ReactNode;
}

export function HeatmapProvider({ children }: HeatmapProviderProps) {
  const [heatmaps, setHeatmaps] = useState<HeatmapLayer[]>([]);

  const addHeatmap = (heatmap: HeatmapLayer) => {
    setHeatmaps(prev => [...prev, heatmap]);
  };

  const removeHeatmap = (id: string) => {
    setHeatmaps(prev => prev.filter(h => h.id !== id));
  };

  const updateHeatmap = (id: string, updates: Partial<HeatmapLayer>) => {
    setHeatmaps(prev => prev.map(h => h.id === id ? { ...h, ...updates } : h));
  };

  const getHeatmap = (id: string) => {
    return heatmaps.find(h => h.id === id);
  };

  const value: HeatmapContextValue = {
    heatmaps,
    addHeatmap,
    removeHeatmap,
    updateHeatmap,
    getHeatmap
  };

  return (
    <HeatmapContext.Provider value={value}>
      {children}
    </HeatmapContext.Provider>
  );
}

export function useHeatmap() {
  const context = useContext(HeatmapContext);
  if (!context) {
    throw new Error('useHeatmap must be used within a HeatmapProvider');
  }
  return context;
}

// Heatmap operations
export function useHeatmapOperations() {
  const { addHeatmap, removeHeatmap, updateHeatmap } = useHeatmap();

  const createHeatmap = (datasetId: string, config?: Partial<HeatmapConfig>) => {
    const heatmap: HeatmapLayer = {
      id: `heatmap-${Date.now()}`,
      datasetId,
      type: 'heatmap',
      config: {
        radiusPixels: config?.radiusPixels || 30,
        intensity: config?.intensity || 1,
        threshold: config?.threshold || 0.05,
        weightField: config?.weightField,
        colorRange: config?.colorRange || [
          '#000000', '#FF0000', '#FFFF00', '#00FF00', '#00FFFF', '#FFFFFF'
        ]
      }
    };
    addHeatmap(heatmap);
    return heatmap;
  };

  const setRadius = (id: string, radiusPixels: number) => {
    const heatmap = useHeatmap().getHeatmap(id);
    if (heatmap) {
      updateHeatmap(id, {
        config: { ...heatmap.config, radiusPixels }
      });
    }
  };

  const setIntensity = (id: string, intensity: number) => {
    const heatmap = useHeatmap().getHeatmap(id);
    if (heatmap) {
      updateHeatmap(id, {
        config: { ...heatmap.config, intensity }
      });
    }
  };

  const setWeightField = (id: string, field: string) => {
    const heatmap = useHeatmap().getHeatmap(id);
    if (heatmap) {
      updateHeatmap(id, {
        config: { ...heatmap.config, weightField: field }
      });
    }
  };

  const deleteHeatmap = (id: string) => {
    removeHeatmap(id);
  };

  return {
    createHeatmap,
    setRadius,
    setIntensity,
    setWeightField,
    deleteHeatmap
  };
}

// Default color ranges
export const HEATMAP_COLOR_RANGES = {
  THERMAL: ['#000000', '#FF0000', '#FFFF00', '#00FF00', '#00FFFF', '#FFFFFF'],
  VIRIDIS: ['#440154', '#3B528B', '#21918C', '#5EC962', '#FDE725'],
  MAGMA: ['#000004', '#3B0F70', '#8C2981', '#DE4968', '#FE9F6D', '#FBFBB2'],
  INFERNO: ['#000004', '#420A68', '#932667', '#DD513A', '#FCA50A', '#FCFFA4']
};
