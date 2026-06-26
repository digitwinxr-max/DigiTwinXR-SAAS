/**
 * PMTiles Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { PMTilesInfo } from './maplibre_types';

interface PMTilesContextValue {
  archives: PMTilesInfo[];
  activeArchive: PMTilesInfo | null;
  addArchive: (archive: PMTilesInfo) => void;
  removeArchive: (id: string) => void;
  setActiveArchive: (archive: PMTilesInfo | null) => void;
  getArchive: (id: string) => PMTilesInfo | undefined;
}

const PMTilesContext = createContext<PMTilesContextValue | undefined>(undefined);

interface PMTilesProviderProps {
  children: ReactNode;
}

export function PMTilesProvider({ children }: PMTilesProviderProps) {
  const [archives, setArchives] = useState<PMTilesInfo[]>([]);
  const [activeArchive, setActiveArchive] = useState<PMTilesInfo | null>(null);

  const addArchive = (archive: PMTilesInfo) => {
    setArchives(prev => [...prev, archive]);
  };

  const removeArchive = (id: string) => {
    setArchives(prev => prev.filter(a => a.id !== id));
    if (activeArchive?.id === id) {
      setActiveArchive(null);
    }
  };

  const getArchive = (id: string) => {
    return archives.find(a => a.id === id);
  };

  const value: PMTilesContextValue = {
    archives,
    activeArchive,
    addArchive,
    removeArchive,
    setActiveArchive,
    getArchive
  };

  return (
    <PMTilesContext.Provider value={value}>
      {children}
    </PMTilesContext.Provider>
  );
}

export function usePMTiles() {
  const context = useContext(PMTilesContext);
  if (!context) {
    throw new Error('usePMTiles must be used within a PMTilesProvider');
  }
  return context;
}

// PMTiles operations
export function usePMTilesOperations() {
  const { addArchive, removeArchive, setActiveArchive } = usePMTiles();

  const openArchive = async (id: string, url: string) => {
    // Extract PMTiles metadata
    const header = await fetch(url, { headers: { Range: 'bytes=0-127' } });
    const buffer = await header.arrayBuffer();
    
    // Parse PMTiles header (simplified)
    const info: PMTilesInfo = {
      id,
      name: id,
      bounds: [-180, -85.051129, 180, 85.051129],
      center: [0, 0],
      minZoom: 0,
      maxZoom: 14,
      layers: [],
      tileType: 'pbf'
    };
    
    addArchive(info);
    setActiveArchive(info);
    return info;
  };

  const closeArchive = (id: string) => {
    removeArchive(id);
  };

  const getMetadata = (archive: PMTilesInfo) => {
    return {
      name: archive.name,
      description: archive.description,
      bounds: archive.bounds,
      center: archive.center,
      zoomRange: `${archive.minZoom} - ${archive.maxZoom}`,
      layers: archive.layers
    };
  };

  return {
    openArchive,
    closeArchive,
    getMetadata
  };
}

// PMTiles source configuration
export function getPMTilesSource(archive: PMTilesInfo) {
  return {
    type: 'vector' as const,
    url: `pmtiles://${archive.id}`
  };
}
