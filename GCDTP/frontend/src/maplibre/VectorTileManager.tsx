/**
 * Vector Tile Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { VectorTileSource, GeoJSONSource } from './maplibre_types';

interface VectorTileContextValue {
  sources: VectorTileSource[];
  addVectorSource: (source: VectorTileSource) => void;
  removeVectorSource: (id: string) => void;
  getVectorSource: (id: string) => VectorTileSource | undefined;
  updateVectorSource: (id: string, updates: Partial<VectorTileSource>) => void;
}

const VectorTileContext = createContext<VectorTileContextValue | undefined>(undefined);

interface VectorTileProviderProps {
  children: ReactNode;
}

export function VectorTileProvider({ children }: VectorTileProviderProps) {
  const [sources, setSources] = useState<VectorTileSource[]>([]);

  const addVectorSource = (source: VectorTileSource) => {
    setSources(prev => [...prev, source]);
  };

  const removeVectorSource = (id: string) => {
    setSources(prev => prev.filter(s => s.id !== id));
  };

  const getVectorSource = (id: string) => {
    return sources.find(s => s.id === id);
  };

  const updateVectorSource = (id: string, updates: Partial<VectorTileSource>) => {
    setSources(prev => prev.map(s => s.id === id ? { ...s, ...updates } : s));
  };

  const value: VectorTileContextValue = {
    sources,
    addVectorSource,
    removeVectorSource,
    getVectorSource,
    updateVectorSource
  };

  return (
    <VectorTileContext.Provider value={value}>
      {children}
    </VectorTileContext.Provider>
  );
}

export function useVectorTile() {
  const context = useContext(VectorTileContext);
  if (!context) {
    throw new Error('useVectorTile must be used within a VectorTileProvider');
  }
  return context;
}

// Vector tile operations
export function useVectorTileOperations() {
  const { sources, addVectorSource, removeVectorSource } = useVectorTile();

  const loadMVT = async (id: string, url: string) => {
    const source: VectorTileSource = {
      id,
      type: 'vector',
      url,
      tiles: [url]
    };
    addVectorSource(source);
    return source;
  };

  const loadGeoJSON = async (id: string, data: GeoJSON.FeatureCollection) => {
    const source: GeoJSONSource = {
      id,
      type: 'geojson',
      data
    };
    addVectorSource(source as unknown as VectorTileSource);
    return source;
  };

  const loadMBTiles = async (id: string, url: string) => {
    // MBTiles would need a server-side conversion
    const source: VectorTileSource = {
      id,
      type: 'vector',
      url
    };
    addVectorSource(source);
    return source;
  };

  return {
    sources,
    loadMVT,
    loadGeoJSON,
    loadMBTiles,
    unloadSource: removeVectorSource
  };
}

// Supported tile formats
export const SUPPORTED_FORMATS = {
  MVT: 'application/vnd.mapbox-vector-tile',
  GEOJSON: 'application/geo+json',
  MBTILES: 'application/x-mbtiles'
};
