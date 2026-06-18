/**
 * Offline Map Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { OfflineRegion, OfflineStatus } from './maplibre_types';

interface OfflineContextValue {
  regions: OfflineRegion[];
  activeDownloads: Map<string, number>;
  addRegion: (region: OfflineRegion) => void;
  removeRegion: (id: string) => void;
  updateRegion: (id: string, updates: Partial<OfflineRegion>) => void;
  getRegion: (id: string) => OfflineRegion | undefined;
  startDownload: (id: string) => void;
  cancelDownload: (id: string) => void;
}

const OfflineContext = createContext<OfflineContextValue | undefined>(undefined);

interface OfflineProviderProps {
  children: ReactNode;
}

export function OfflineProvider({ children }: OfflineProviderProps) {
  const [regions, setRegions] = useState<OfflineRegion[]>([]);
  const [activeDownloads, setActiveDownloads] = useState<Map<string, number>>(new Map());

  const addRegion = (region: OfflineRegion) => {
    setRegions(prev => [...prev, region]);
  };

  const removeRegion = (id: string) => {
    setRegions(prev => prev.filter(r => r.id !== id));
    setActiveDownloads(prev => {
      const next = new Map(prev);
      next.delete(id);
      return next;
    });
  };

  const updateRegion = (id: string, updates: Partial<OfflineRegion>) => {
    setRegions(prev => prev.map(r => r.id === id ? { ...r, ...updates } : r));
  };

  const getRegion = (id: string) => {
    return regions.find(r => r.id === id);
  };

  const startDownload = (id: string) => {
    setActiveDownloads(prev => new Map(prev).set(id, 0));
    updateRegion(id, { status: OfflineStatus.DOWNLOADING });
    
    // Simulate download progress
    simulateDownload(id);
  };

  const cancelDownload = (id: string) => {
    setActiveDownloads(prev => {
      const next = new Map(prev);
      next.delete(id);
      return next;
    });
    updateRegion(id, { status: OfflineStatus.PENDING, progress: 0 });
  };

  const simulateDownload = (id: string) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      updateRegion(id, { progress });
      
      if (progress >= 100) {
        clearInterval(interval);
        setActiveDownloads(prev => {
          const next = new Map(prev);
          next.delete(id);
          return next;
        });
        updateRegion(id, { status: OfflineStatus.COMPLETED, progress: 100 });
      }
    }, 1000);
  };

  const value: OfflineContextValue = {
    regions,
    activeDownloads,
    addRegion,
    removeRegion,
    updateRegion,
    getRegion,
    startDownload,
    cancelDownload
  };

  return (
    <OfflineContext.Provider value={value}>
      {children}
    </OfflineContext.Provider>
  );
}

export function useOffline() {
  const context = useContext(OfflineContext);
  if (!context) {
    throw new Error('useOffline must be used within an OfflineProvider');
  }
  return context;
}

// Offline operations
export function useOfflineOperations() {
  const { addRegion, removeRegion, startDownload } = useOffline();

  const createRegion = async (
    name: string,
    bounds: [number, number, number, number],
    minZoom: number,
    maxZoom: number
  ) => {
    const region: OfflineRegion = {
      id: `region-${Date.now()}`,
      name,
      bounds,
      minZoom,
      maxZoom,
      status: OfflineStatus.PENDING,
      progress: 0,
      createdAt: new Date().toISOString()
    };
    
    addRegion(region);
    startDownload(region.id);
    return region;
  };

  const deleteRegion = (id: string) => {
    removeRegion(id);
  };

  const getStorageEstimate = async () => {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      return await navigator.storage.estimate();
    }
    return { usage: 0, quota: 0 };
  };

  return {
    createRegion,
    deleteRegion,
    getStorageEstimate
  };
}
