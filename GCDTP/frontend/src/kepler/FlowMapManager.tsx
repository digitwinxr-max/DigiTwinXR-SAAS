/**
 * Flow Map Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { FlowMapLayer, FlowMapConfig } from './kepler_types';

interface FlowMapContextValue {
  flowMaps: FlowMapLayer[];
  addFlowMap: (flowMap: FlowMapLayer) => void;
  removeFlowMap: (id: string) => void;
  updateFlowMap: (id: string, updates: Partial<FlowMapLayer>) => void;
  getFlowMap: (id: string) => FlowMapLayer | undefined;
}

const FlowMapContext = createContext<FlowMapContextValue | undefined>(undefined);

interface FlowMapProviderProps {
  children: ReactNode;
}

export function FlowMapProvider({ children }: FlowMapProviderProps) {
  const [flowMaps, setFlowMaps] = useState<FlowMapLayer[]>([]);

  const addFlowMap = (flowMap: FlowMapLayer) => {
    setFlowMaps(prev => [...prev, flowMap]);
  };

  const removeFlowMap = (id: string) => {
    setFlowMaps(prev => prev.filter(f => f.id !== id));
  };

  const updateFlowMap = (id: string, updates: Partial<FlowMapLayer>) => {
    setFlowMaps(prev => prev.map(f => f.id === id ? { ...f, ...updates } : f));
  };

  const getFlowMap = (id: string) => {
    return flowMaps.find(f => f.id === id);
  };

  const value: FlowMapContextValue = {
    flowMaps,
    addFlowMap,
    removeFlowMap,
    updateFlowMap,
    getFlowMap
  };

  return (
    <FlowMapContext.Provider value={value}>
      {children}
    </FlowMapContext.Provider>
  );
}

export function useFlowMap() {
  const context = useContext(FlowMapContext);
  if (!context) {
    throw new Error('useFlowMap must be used within a FlowMapProvider');
  }
  return context;
}

// Flow map operations
export function useFlowMapOperations() {
  const { addFlowMap, removeFlowMap, updateFlowMap } = useFlowMap();

  const createFlowMap = (datasetId: string, config: FlowMapConfig) => {
    const flowMap: FlowMapLayer = {
      id: `flowmap-${Date.now()}`,
      datasetId,
      type: 'flow',
      config: {
        sourceLatField: config.sourceLatField,
        sourceLngField: config.sourceLngField,
        targetLatField: config.targetLatField,
        targetLngField: config.targetLngField,
        weightField: config.weightField,
        colorRange: config.colorRange || ['#EFF3FF', '#BDC9E2', '#6BAED6', '#2171B5', '#084594'],
        opacity: config.opacity || 0.6
      }
    };
    addFlowMap(flowMap);
    return flowMap;
  };

  const createOriginDestination = (
    datasetId: string,
    originField: string,
    destinationField: string
  ) => {
    const flowMap: FlowMapLayer = {
      id: `flowmap-${Date.now()}`,
      datasetId,
      type: 'flow',
      config: {
        sourceLatField: `${originField}_lat`,
        sourceLngField: `${originField}_lng`,
        targetLatField: `${destinationField}_lat`,
        targetLngField: `${destinationField}_lng`,
        opacity: 0.6
      }
    };
    addFlowMap(flowMap);
    return flowMap;
  };

  const setOpacity = (id: string, opacity: number) => {
    const flowMap = useFlowMap().getFlowMap(id);
    if (flowMap) {
      updateFlowMap(id, {
        config: { ...flowMap.config, opacity }
      });
    }
  };

  const setColorRange = (id: string, colorRange: string[]) => {
    const flowMap = useFlowMap().getFlowMap(id);
    if (flowMap) {
      updateFlowMap(id, {
        config: { ...flowMap.config, colorRange }
      });
    }
  };

  const deleteFlowMap = (id: string) => {
    removeFlowMap(id);
  };

  return {
    createFlowMap,
    createOriginDestination,
    setOpacity,
    setColorRange,
    deleteFlowMap
  };
}

// Flow map color schemes
export const FLOWMAP_COLOR_SCHEMES = {
  BLUES: ['#EFF3FF', '#BDC9E2', '#6BAED6', '#2171B5', '#084594'],
  GREENS: ['#EDF8E9', '#BAE4B3', '#74C476', '#31A354', '#006D2C'],
  PURPLES: ['#F2F0F7', '#CBC9E2', '#9E9AC8', '#756BB1', '#54278F'],
  ORANGES: ['#FEEDDE', '#FDBE85', '#FD8D3C', '#E31A1C', '#800026']
};
