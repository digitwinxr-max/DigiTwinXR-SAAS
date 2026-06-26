/**
 * Asset 3D Layer
 * 
 * 3D visualization layer for assets.
 * Supports point, billboard, and model representations.
 * Part of the dual-view architecture (Leaflet 2D + Cesium 3D).
 */

import React, { useEffect, useMemo } from 'react';
import { useCesium } from './CesiumContext';

// Asset data types
export interface AssetData {
  id: string;
  name: string;
  type: 'substation' | 'transformer' | 'pipeline' | 'pump' | 'valve' | 'sensor' | 'other';
  position: {
    longitude: number;
    latitude: number;
    height?: number;
  };
  status?: 'healthy' | 'warning' | 'critical' | 'offline';
  health?: number;
  metadata?: Record<string, any>;
}

interface Asset3DLayerProps {
  assets: AssetData[];
  showLabels?: boolean;
  showHealth?: boolean;
  selectedAssetId?: string | null;
  onAssetClick?: (asset: AssetData) => void;
  onAssetHover?: (asset: AssetData | null) => void;
}

// Color mappings for asset types and status
const ASSET_TYPE_COLORS: Record<string, string> = {
  substation: '#FFD700',    // Gold
  transformer: '#FFA500',  // Orange
  pipeline: '#4169E1',      // Royal Blue
  pump: '#00CED1',          // Dark Turquoise
  valve: '#9370DB',         // Medium Purple
  sensor: '#32CD32',        // Lime Green
  other: '#808080',         // Gray
};

const STATUS_COLORS: Record<string, string> = {
  healthy: '#00FF00',      // Green
  warning: '#FFFF00',        // Yellow
  critical: '#FF0000',       // Red
  offline: '#808080',       // Gray
};

export function Asset3DLayer({
  assets,
  showLabels = true,
  showHealth = true,
  selectedAssetId,
  onAssetClick,
  onAssetHover,
}: Asset3DLayerProps): JSX.Element {
  const { addEntity, removeEntity, clearEntities, selectEntity } = useCesium();

  // Create entities for assets
  const entities = useMemo(() => {
    return assets.map(asset => {
      const baseColor = ASSET_TYPE_COLORS[asset.type] || ASSET_TYPE_COLORS.other;
      const statusColor = asset.status ? STATUS_COLORS[asset.status] : baseColor;
      
      return {
        id: asset.id,
        position: {
          longitude: asset.position.longitude,
          latitude: asset.position.latitude,
          height: asset.position.height || 0,
        },
        point: {
          pixelSize: selectedAssetId === asset.id ? 15 : 10,
          color: statusColor,
          outlineColor: selectedAssetId === asset.id ? '#FFFFFF' : baseColor,
          outlineWidth: selectedAssetId === asset.id ? 2 : 1,
        },
        label: showLabels ? {
          text: asset.name,
          font: '12px sans-serif',
          fillColor: '#FFFFFF',
          outlineColor: '#000000',
          outlineWidth: 2,
          style: 'FILL_AND_OUTLINE',
          verticalOrigin: 'BOTTOM',
          pixelOffset: { x: 0, y: -15 },
        } : undefined,
        description: `
          <div class="asset-info">
            <h4>${asset.name}</h4>
            <p><strong>Type:</strong> ${asset.type}</p>
            <p><strong>Status:</strong> ${asset.status || 'Unknown'}</p>
            ${asset.health !== undefined ? `<p><strong>Health:</strong> ${(asset.health * 100).toFixed(1)}%</p>` : ''}
          </div>
        `,
        properties: {
          assetType: asset.type,
          status: asset.status,
          health: asset.health,
          ...asset.metadata,
        },
      };
    });
  }, [assets, showLabels, selectedAssetId]);

  // Add entities to Cesium viewer
  useEffect(() => {
    if (entities.length > 0) {
      entities.forEach(entity => {
        addEntity(entity);
      });
    }

    return () => {
      // Cleanup entities on unmount
      entities.forEach(entity => {
        removeEntity(entity.id);
      });
    };
  }, [entities, addEntity, removeEntity]);

  // Handle entity selection
  useEffect(() => {
    if (selectedAssetId) {
      const selectedEntity = entities.find(e => e.id === selectedAssetId);
      if (selectedEntity) {
        selectEntity(selectedEntity as any);
      }
    }
  }, [selectedAssetId, entities, selectEntity]);

  // This component doesn't render anything directly
  // It manages entities in the Cesium viewer
  return <></>;
}

// Component for rendering health visualization as 3D bars
export function HealthBarLayer({
  assets,
}: {
  assets: AssetData[];
}): JSX.Element {
  const { addEntity, removeEntity } = useCesium();

  const healthBars = useMemo(() => {
    return assets
      .filter(asset => asset.health !== undefined)
      .map(asset => {
        const barHeight = (1 - (asset.health || 0)) * 1000; // Scale height based on health
        
        return {
          id: `health-bar-${asset.id}`,
          position: {
            longitude: asset.position.longitude,
            latitude: asset.position.latitude,
            height: asset.position.height || 0,
          },
          box: {
            dimensions: { x: 50, y: 50, z: barHeight },
            material: asset.health && asset.health < 0.5 
              ? STATUS_COLORS.critical 
              : asset.health && asset.health < 0.8 
                ? STATUS_COLORS.warning 
                : STATUS_COLORS.healthy,
          },
        };
      });
  }, [assets]);

  useEffect(() => {
    healthBars.forEach(bar => {
      addEntity(bar);
    });

    return () => {
      healthBars.forEach(bar => {
        removeEntity(bar.id);
      });
    };
  }, [healthBars, addEntity, removeEntity]);

  return <></>;
}

export default Asset3DLayer;
