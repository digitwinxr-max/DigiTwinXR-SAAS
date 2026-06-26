/**
 * Terrain Manager
 * 
 * Manages terrain providers for 3D visualization.
 * Supports WorldTerrain, STK, and custom terrain.
 * Part of the dual-view architecture (Leaflet 2D + Cesium 3D).
 */

import React, { useState, useCallback } from 'react';
import { useCesium } from './CesiumContext';

// Terrain provider types
export type TerrainProviderType = 
  | 'world'           // Cesium World Terrain
  | 'ellipsoid'        // Ellipsoid (no terrain)
  | 'stk'             // STK Terrain Server
  | 'arcgis'          // ArcGIS World Terrain
  | 'custom';         // Custom terrain provider

interface TerrainConfig {
  type: TerrainProviderType;
  url?: string;
  token?: string;
  requestVertexNormals?: boolean;
  requestWaterMask?: boolean;
}

interface TerrainManagerProps {
  defaultTerrain?: TerrainProviderType;
  onTerrainChange?: (type: TerrainProviderType) => void;
}

// Common terrain providers
const TERRAIN_PROVIDERS: Record<TerrainProviderType, string> = {
  world: 'Cesium World Terrain',
  ellipsoid: 'Ellipsoid (No Terrain)',
  stk: 'STK Terrain Server',
  arcgis: 'ArcGIS World Terrain',
  custom: 'Custom Terrain',
};

export function TerrainManager({
  defaultTerrain = 'world',
  onTerrainChange,
}: TerrainManagerProps): JSX.Element {
  const { loadTerrain, viewer } = useCesium();
  const [currentTerrain, setCurrentTerrain] = useState<TerrainProviderType>(defaultTerrain);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTerrainChange = useCallback(async (newTerrain: TerrainProviderType) => {
    setIsLoading(true);
    setError(null);

    try {
      let provider: any;

      switch (newTerrain) {
        case 'world':
          // Cesium World Terrain - open data
          provider = {
            type: 'world',
            name: 'Cesium World Terrain',
          };
          break;
          
        case 'ellipsoid':
          // Ellipsoid - flat earth
          provider = {
            type: 'ellipsoid',
            name: 'Ellipsoid',
          };
          break;
          
        case 'stk':
          // STK Terrain Server (requires token)
          provider = {
            type: 'stk',
            name: 'STK Terrain',
          };
          break;
          
        case 'arcgis':
          // ArcGIS World Terrain
          provider = {
            type: 'arcgis',
            name: 'ArcGIS World Terrain',
          };
          break;
          
        case 'custom':
          // Custom terrain URL would be provided
          provider = {
            type: 'custom',
            name: 'Custom Terrain',
          };
          break;
          
        default:
          throw new Error(`Unknown terrain type: ${newTerrain}`);
      }

      loadTerrain(provider);
      setCurrentTerrain(newTerrain);
      onTerrainChange?.(newTerrain);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load terrain');
    } finally {
      setIsLoading(false);
    }
  }, [loadTerrain, onTerrainChange]);

  return (
    <div className="terrain-manager">
      <h4>Terrain</h4>
      
      {isLoading && <div className="terrain-loading">Loading terrain...</div>}
      {error && <div className="terrain-error">{error}</div>}
      
      <select
        value={currentTerrain}
        onChange={(e) => handleTerrainChange(e.target.value as TerrainProviderType)}
        disabled={isLoading}
        className="terrain-select"
      >
        {Object.entries(TERRAIN_PROVIDERS).map(([key, label]) => (
          <option key={key} value={key}>
            {label}
          </option>
        ))}
      </select>
      
      {currentTerrain === 'stk' && (
        <div className="terrain-token-notice">
          Note: STK terrain requires authentication
        </div>
      )}
    </div>
  );
}

// Hook for managing terrain providers
export function useTerrainProvider() {
  const { loadTerrain, viewer } = useCesium();
  const [currentProvider, setCurrentProvider] = useState<string | null>(null);

  const setWorldTerrain = useCallback(() => {
    loadTerrain({ type: 'world' });
    setCurrentProvider('world');
  }, [loadTerrain]);

  const setEllipsoid = useCallback(() => {
    loadTerrain({ type: 'ellipsoid' });
    setCurrentProvider('ellipsoid');
  }, [loadTerrain]);

  const setCustomTerrain = useCallback((url: string, options?: any) => {
    loadTerrain({ type: 'custom', url, ...options });
    setCurrentProvider('custom');
  }, [loadTerrain]);

  return {
    currentProvider,
    setWorldTerrain,
    setEllipsoid,
    setCustomTerrain,
  };
}

// Component for terrain lighting effects
export function TerrainLighting({
  enabled = true,
}: {
  enabled?: boolean;
}): JSX.Element {
  const { viewer } = useCesium();

  React.useEffect(() => {
    if (viewer && enabled) {
      // Enable terrain lighting
      // viewer.scene.globe.enableLighting = true;
    }
  }, [viewer, enabled]);

  return <></>;
}

// Component for terrain exaggeration
export function TerrainExaggeration({
  factor = 1.0,
}: {
  factor?: number;
}): JSX.Element {
  const { viewer } = useCesium();

  React.useEffect(() => {
    if (viewer) {
      // Set terrain exaggeration
      // viewer.scene.globe.terrainExaggeration = factor;
    }
  }, [viewer, factor]);

  return <></>;
}

export default TerrainManager;
