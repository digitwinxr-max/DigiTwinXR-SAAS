/**
 * Tileset Loader
 * 
 * Loads and manages 3D Tilesets (GLB, B3DM, PNTS, etc.)
 * Prepared for future BIM, IFC, photogrammetry, and point clouds.
 * Part of the dual-view architecture (Leaflet 2D + Cesium 3D).
 */

import React, { useEffect, useState, useCallback } from 'react';
import { useCesium } from './CesiumContext';

// Tileset types supported
export type TilesetType = 
  | 'glb'           // GL Transmission Format (GLB)
  | 'b3dm'          // Batched 3D Model
  | 'pnts'          // Point Cloud
  | 'i3dm'          // Instanced 3D Model
  | 'cmpt';         // Composite

interface TilesetConfig {
  id: string;
  url: string;
  type: TilesetType;
  name?: string;
  visible?: boolean;
  style?: any;
}

interface TilesetLoaderProps {
  tilesets: TilesetConfig[];
  onTilesetLoaded?: (id: string) => void;
  onTilesetError?: (id: string, error: Error) => void;
}

interface TilesetState {
  id: string;
  url: string;
  type: TilesetType;
  name: string;
  visible: boolean;
  loading: boolean;
  loaded: boolean;
  error: string | null;
}

export function TilesetLoader({
  tilesets,
  onTilesetLoaded,
  onTilesetError,
}: TilesetLoaderProps): JSX.Element {
  const { load3DTiles } = useCesium();
  const [tilesetStates, setTilesetStates] = useState<Record<string, TilesetState>>({});

  // Initialize tileset states
  useEffect(() => {
    const initialStates: Record<string, TilesetState> = {};
    
    tilesets.forEach(tileset => {
      initialStates[tileset.id] = {
        id: tileset.id,
        url: tileset.url,
        type: tileset.type,
        name: tileset.name || tileset.id,
        visible: tileset.visible ?? true,
        loading: false,
        loaded: false,
        error: null,
      };
    });
    
    setTilesetStates(initialStates);
  }, [tilesets]);

  // Load tilesets
  const loadTileset = useCallback(async (tileset: TilesetConfig) => {
    setTilesetStates(prev => ({
      ...prev,
      [tileset.id]: {
        ...prev[tileset.id],
        loading: true,
        error: null,
      },
    }));

    try {
      // In real implementation:
      // const tileset = await Cesium.create3DTileset(tileset.url);
      // viewer.scene.primitives.add(tileset);
      
      load3DTiles(tileset.url);
      
      setTilesetStates(prev => ({
        ...prev,
        [tileset.id]: {
          ...prev[tileset.id],
          loading: false,
          loaded: true,
        },
      }));
      
      onTilesetLoaded?.(tileset.id);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load tileset';
      
      setTilesetStates(prev => ({
        ...prev,
        [tileset.id]: {
          ...prev[tileset.id],
          loading: false,
          error: errorMessage,
        },
      }));
      
      onTilesetError?.(tileset.id, error instanceof Error ? error : new Error(errorMessage));
    }
  }, [load3DTiles, onTilesetLoaded, onTilesetError]);

  // Load all visible tilesets
  useEffect(() => {
    tilesets.forEach(tileset => {
      if (tilesetStates[tileset.id]?.visible && !tilesetStates[tileset.id]?.loaded) {
        loadTileset(tileset);
      }
    });
  }, [tilesets, tilesetStates, loadTileset]);

  // Toggle tileset visibility
  const toggleVisibility = useCallback((tilesetId: string) => {
    setTilesetStates(prev => ({
      ...prev,
      [tilesetId]: {
        ...prev[tilesetId],
        visible: !prev[tilesetId].visible,
      },
    }));
  }, []);

  // This component manages tilesets internally
  // It doesn't render any UI elements directly
  return <></>;
}

// Component for displaying tileset controls
export function TilesetControls({
  tilesets,
  onToggleVisibility,
  onReload,
}: {
  tilesets: TilesetState[];
  onToggleVisibility: (id: string) => void;
  onReload: (id: string) => void;
}): JSX.Element {
  return (
    <div className="tileset-controls">
      <h4>3D Layers</h4>
      <ul className="tileset-list">
        {tilesets.map(tileset => (
          <li key={tileset.id} className="tileset-item">
            <label>
              <input
                type="checkbox"
                checked={tileset.visible}
                onChange={() => onToggleVisibility(tileset.id)}
                disabled={tileset.loading}
              />
              <span className="tileset-name">{tileset.name}</span>
              <span className="tileset-type">{tileset.type}</span>
            </label>
            {tileset.loading && <span className="tileset-loading">Loading...</span>}
            {tileset.error && (
              <button 
                className="tileset-retry"
                onClick={() => onReload(tileset.id)}
              >
                Retry
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

// Hook for loading BIM/IFC models (future-ready)
export function useBIMLoader() {
  const { addEntity } = useCesium();
  
  const loadModel = useCallback(async (url: string, position: any) => {
    // Future implementation for BIM/IFC models
    // import { Model } from 'cesium';
    // const model = await Model.fromGltf({ url, ... });
    console.log('Loading BIM model from:', url);
    return { url, position };
  }, [addEntity]);

  return { loadModel };
}

// Hook for loading point clouds (future-ready)
export function usePointCloudLoader() {
  const { addEntity } = useCesium();
  
  const loadPointCloud = useCallback(async (url: string, position: any) => {
    // Future implementation for point clouds
    // import { PointCloud } from 'cesium';
    // const points = await PointCloud.fromUrl(url);
    console.log('Loading point cloud from:', url);
    return { url, position };
  }, [addEntity]);

  return { loadPointCloud };
}

// Hook for loading photogrammetry (future-ready)
export function usePhotogrammetryLoader() {
  const { load3DTiles } = useCesium();
  
  const loadPhotogrammetry = useCallback(async (url: string) => {
    // Future implementation for photogrammetry
    // Uses 3D Tiles for streaming
    load3DTiles(url);
  }, [load3DTiles]);

  return { loadPhotogrammetry };
}

export default TilesetLoader;
