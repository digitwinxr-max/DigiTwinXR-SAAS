/**
 * Cluster Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { ClusterLayer, ClusterConfig } from './kepler_types';

interface ClusterContextValue {
  clusters: ClusterLayer[];
  addCluster: (cluster: ClusterLayer) => void;
  removeCluster: (id: string) => void;
  updateCluster: (id: string, updates: Partial<ClusterLayer>) => void;
  getCluster: (id: string) => ClusterLayer | undefined;
}

const ClusterContext = createContext<ClusterContextValue | undefined>(undefined);

interface ClusterProviderProps {
  children: ReactNode;
}

export function ClusterProvider({ children }: ClusterProviderProps) {
  const [clusters, setClusters] = useState<ClusterLayer[]>([]);

  const addCluster = (cluster: ClusterLayer) => {
    setClusters(prev => [...prev, cluster]);
  };

  const removeCluster = (id: string) => {
    setClusters(prev => prev.filter(c => c.id !== id));
  };

  const updateCluster = (id: string, updates: Partial<ClusterLayer>) => {
    setClusters(prev => prev.map(c => c.id === id ? { ...c, ...updates } : c));
  };

  const getCluster = (id: string) => {
    return clusters.find(c => c.id === id);
  };

  const value: ClusterContextValue = {
    clusters,
    addCluster,
    removeCluster,
    updateCluster,
    getCluster
  };

  return (
    <ClusterContext.Provider value={value}>
      {children}
    </ClusterContext.Provider>
  );
}

export function useCluster() {
  const context = useContext(ClusterContext);
  if (!context) {
    throw new Error('useCluster must be used within a ClusterProvider');
  }
  return context;
}

// Cluster operations
export function useClusterOperations() {
  const { addCluster, removeCluster, updateCluster } = useCluster();

  const createCluster = (datasetId: string, config?: Partial<ClusterConfig>) => {
    const cluster: ClusterLayer = {
      id: `cluster-${Date.now()}`,
      datasetId,
      type: 'cluster',
      config: {
        radiusPixels: config?.radiusPixels || 50,
        minZoom: config?.minZoom || 0,
        maxZoom: config?.maxZoom || 16,
        colorRange: config?.colorRange || [
          '#48C9B0', '#5DADE2', '#AF7AC5', '#F5B041', '#EC7063'
        ]
      }
    };
    addCluster(cluster);
    return cluster;
  };

  const setClusterRadius = (id: string, radiusPixels: number) => {
    const cluster = useCluster().getCluster(id);
    if (cluster) {
      updateCluster(id, {
        config: { ...cluster.config, radiusPixels }
      });
    }
  };

  const setZoomRange = (id: string, minZoom: number, maxZoom: number) => {
    const cluster = useCluster().getCluster(id);
    if (cluster) {
      updateCluster(id, {
        config: { ...cluster.config, minZoom, maxZoom }
      });
    }
  };

  const deleteCluster = (id: string) => {
    removeCluster(id);
  };

  return {
    createCluster,
    setClusterRadius,
    setZoomRange,
    deleteCluster
  };
}

// Cluster color schemes
export const CLUSTER_COLOR_SCHEMES = {
  RAINBOW: ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#8B00FF'],
  VIRIDIS: ['#440154', '#3B528B', '#21918C', '#5EC962', '#FDE725'],
  PLASMA: ['#0D0887', '#7E03A8', '#CC4778', '#F89540', '#F0F921']
};
