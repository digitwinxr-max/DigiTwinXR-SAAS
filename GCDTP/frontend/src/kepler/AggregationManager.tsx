/**
 * Aggregation Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { HexBinLayer, HexBinConfig, AggregationConfig, AggregationType, AggregationMethod } from './kepler_types';

interface AggregationContextValue {
  hexLayers: HexBinLayer[];
  addHexLayer: (layer: HexBinLayer) => void;
  removeHexLayer: (id: string) => void;
  updateHexLayer: (id: string, updates: Partial<HexBinLayer>) => void;
  getHexLayer: (id: string) => HexBinLayer | undefined;
}

const AggregationContext = createContext<AggregationContextValue | undefined>(undefined);

interface AggregationProviderProps {
  children: ReactNode;
}

export function AggregationProvider({ children }: AggregationProviderProps) {
  const [hexLayers, setHexLayers] = useState<HexBinLayer[]>([]);

  const addHexLayer = (layer: HexBinLayer) => {
    setHexLayers(prev => [...prev, layer]);
  };

  const removeHexLayer = (id: string) => {
    setHexLayers(prev => prev.filter(h => h.id !== id));
  };

  const updateHexLayer = (id: string, updates: Partial<HexBinLayer>) => {
    setHexLayers(prev => prev.map(h => h.id === id ? { ...h, ...updates } : h));
  };

  const getHexLayer = (id: string) => {
    return hexLayers.find(h => h.id === id);
  };

  const value: AggregationContextValue = {
    hexLayers,
    addHexLayer,
    removeHexLayer,
    updateHexLayer,
    getHexLayer
  };

  return (
    <AggregationContext.Provider value={value}>
      {children}
    </AggregationContext.Provider>
  );
}

export function useAggregation() {
  const context = useContext(AggregationContext);
  if (!context) {
    throw new Error('useAggregation must be used within an AggregationProvider');
  }
  return context;
}

// Aggregation operations
export function useAggregationOperations() {
  const { addHexLayer, removeHexLayer, updateHexLayer } = useAggregation();

  const createHexBin = (datasetId: string, config?: Partial<HexBinConfig>) => {
    const layer: HexBinLayer = {
      id: `hexbin-${Date.now()}`,
      datasetId,
      type: 'hexbin',
      config: {
        coverage: config?.coverage || 0.9,
        elevationScale: config?.elevationScale || 4,
        extruded: config?.extruded ?? true,
        radius: config?.radius || 100,
        colorRange: config?.colorRange || [
          '#48C9B0', '#5DADE2', '#AF7AC5', '#F5B041', '#EC7063'
        ],
        colorField: config?.colorField,
        elevationField: config?.elevationField
      }
    };
    addHexLayer(layer);
    return layer;
  };

  const createGridAggregation = (datasetId: string, config?: Partial<HexBinConfig>) => {
    // Grid is similar to hex but with square cells
    return createHexBin(datasetId, config);
  };

  const setCoverage = (id: string, coverage: number) => {
    const layer = useAggregation().getHexLayer(id);
    if (layer) {
      updateHexLayer(id, {
        config: { ...layer.config, coverage }
      });
    }
  };

  const setElevationScale = (id: string, scale: number) => {
    const layer = useAggregation().getHexLayer(id);
    if (layer) {
      updateHexLayer(id, {
        config: { ...layer.config, elevationScale: scale }
      });
    }
  };

  const toggleExtrusion = (id: string) => {
    const layer = useAggregation().getHexLayer(id);
    if (layer) {
      updateHexLayer(id, {
        config: { ...layer.config, extruded: !layer.config.extruded }
      });
    }
  };

  const deleteHexBin = (id: string) => {
    removeHexLayer(id);
  };

  return {
    createHexBin,
    createGridAggregation,
    setCoverage,
    setElevationScale,
    toggleExtrusion,
    deleteHexBin
  };
}

// Hex bin color schemes
export const HEX_COLOR_SCHEMES = {
  LIGHT: ['#EFF3FF', '#CBD7E9', '#8DA0CB', '#5B9BD5', '#2E75B6', '#1F4E79'],
  DARK: ['#F768A1', '#FA9FB5', '#FCC5C0', '#FDCBC4', '#FDD49E', '#FDBB84'],
  NATURE: ['#EDF8E9', '#CCEBC5', '#A8D5BA', '#7BC8A4', '#4DBB8C', '#22AAAA']
};
