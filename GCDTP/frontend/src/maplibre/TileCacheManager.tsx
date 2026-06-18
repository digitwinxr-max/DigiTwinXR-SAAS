/**
 * Tile Cache Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { TileCacheStats } from './maplibre_types';

interface CacheEntry {
  key: string;
  url: string;
  size: number;
  timestamp: number;
}

interface TileCacheContextValue {
  stats: TileCacheStats;
  entries: CacheEntry[];
  addEntry: (key: string, url: string, size: number) => void;
  removeEntry: (key: string) => void;
  clearCache: () => void;
  getCacheHitRate: () => number;
}

const TileCacheContext = createContext<TileCacheContextValue | undefined>(undefined);

interface TileCacheProviderProps {
  children: ReactNode;
}

export function TileCacheProvider({ children }: TileCacheProviderProps) {
  const [entries, setEntries] = useState<CacheEntry[]>([]);
  const [hits, setHits] = useState(0);
  const [misses, setMisses] = useState(0);
  const [totalSize, setTotalSize] = useState(0);

  const addEntry = (key: string, url: string, size: number) => {
    setEntries(prev => {
      // Remove if exists
      const filtered = prev.filter(e => e.key !== key);
      setTotalSize(t => t + size);
      return [...filtered, { key, url, size, timestamp: Date.now() }];
    });
    setMisses(m => m + 1);
  };

  const removeEntry = (key: string) => {
    setEntries(prev => {
      const entry = prev.find(e => e.key === key);
      if (entry) {
        setTotalSize(t => t - entry.size);
      }
      return prev.filter(e => e.key !== key);
    });
  };

  const clearCache = () => {
    setEntries([]);
    setHits(0);
    setMisses(0);
    setTotalSize(0);
  };

  const getCacheHitRate = () => {
    const total = hits + misses;
    return total > 0 ? (hits / total) * 100 : 0;
  };

  const recordHit = () => {
    setHits(h => h + 1);
  };

  const recordMiss = () => {
    setMisses(m => m + 1);
  };

  const value: TileCacheContextValue = {
    stats: {
      hits,
      misses,
      size: totalSize,
      maxSize: 100 * 1024 * 1024, // 100MB default
      entries: entries.length
    },
    entries,
    addEntry,
    removeEntry,
    clearCache,
    getCacheHitRate
  };

  return (
    <TileCacheContext.Provider value={value}>
      {children}
    </TileCacheContext.Provider>
  );
}

export function useTileCache() {
  const context = useContext(TileCacheContext);
  if (!context) {
    throw new Error('useTileCache must be used within a TileCacheProvider');
  }
  return context;
}

// Cache operations
export function useTileCacheOperations() {
  const { addEntry, removeEntry, clearCache, stats } = useTileCache();

  const cacheTile = (url: string, data: ArrayBuffer) => {
    const key = `tile:${url}`;
    addEntry(key, url, data.byteLength);
  };

  const getCachedTile = (url: string) => {
    const key = `tile:${url}`;
    return entries.find(e => e.key === key);
  };

  const entries = useTileCache().entries;

  const pruneCache = (maxSize: number) => {
    let currentSize = stats.size;
    const sortedEntries = [...entries].sort((a, b) => a.timestamp - b.timestamp);
    
    for (const entry of sortedEntries) {
      if (currentSize <= maxSize) break;
      removeEntry(entry.key);
      currentSize -= entry.size;
    }
  };

  return {
    cacheTile,
    getCachedTile,
    pruneCache,
    clearCache,
    stats
  };
}
