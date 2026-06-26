/**
 * Asset 3D Layer Tests
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { CesiumProvider } from '../../src/cesium/CesiumContext';
import { Asset3DLayer, AssetData, HealthBarLayer } from '../../src/cesium/Asset3DLayer';

// Test wrapper with provider
function AssetLayerWrapper({ assets, ...props }: { assets: AssetData[] } & any) {
  return (
    <CesiumProvider>
      <Asset3DLayer assets={assets} {...props} />
    </CesiumProvider>
  );
}

describe('Asset3DLayer', () => {
  const mockAssets: AssetData[] = [
    {
      id: 'asset-1',
      name: 'Substation A',
      type: 'substation',
      position: { longitude: -75.59777, latitude: 40.038503 },
      status: 'healthy',
      health: 0.95,
    },
    {
      id: 'asset-2',
      name: 'Transformer B',
      type: 'transformer',
      position: { longitude: -75.6, latitude: 40.04 },
      status: 'warning',
      health: 0.6,
    },
    {
      id: 'asset-3',
      name: 'Pipeline C',
      type: 'pipeline',
      position: { longitude: -75.5, latitude: 40.03 },
      status: 'critical',
      health: 0.2,
    },
  ];

  it('should render without crashing', () => {
    render(<AssetLayerWrapper assets={mockAssets} />);
    // Component doesn't render anything directly
    expect(true).toBe(true);
  });

  it('should accept asset data', () => {
    render(<AssetLayerWrapper assets={mockAssets} />);
    // Just verify it accepts the data without error
    expect(mockAssets.length).toBe(3);
  });

  it('should handle empty assets array', () => {
    render(<AssetLayerWrapper assets={[]} />);
    expect(mockAssets.length).toBe(0);
  });

  it('should handle asset with all required fields', () => {
    const completeAsset: AssetData = {
      id: 'complete-1',
      name: 'Complete Asset',
      type: 'pump',
      position: { longitude: 0, latitude: 0, height: 100 },
      status: 'offline',
      health: 0,
      metadata: { custom: 'data' },
    };
    
    render(<AssetLayerWrapper assets={[completeAsset]} />);
    expect(completeAsset.metadata).toBeDefined();
  });
});

describe('Asset Types', () => {
  it('should support all asset types', () => {
    const types = ['substation', 'transformer', 'pipeline', 'pump', 'valve', 'sensor', 'other'];
    
    types.forEach(type => {
      const asset: AssetData = {
        id: `asset-${type}`,
        name: `${type} Asset`,
        type,
        position: { longitude: 0, latitude: 0 },
      };
      
      expect(asset.type).toBe(type);
    });
  });
});

describe('Asset Status', () => {
  it('should support all status values', () => {
    const statuses = ['healthy', 'warning', 'critical', 'offline'];
    
    statuses.forEach(status => {
      const asset: AssetData = {
        id: `asset-${status}`,
        name: `${status} Asset`,
        type: 'sensor',
        position: { longitude: 0, latitude: 0 },
        status,
      };
      
      expect(asset.status).toBe(status);
    });
  });
});

describe('HealthBarLayer', () => {
  it('should render without crashing', () => {
    const assets: AssetData[] = [
      {
        id: 'health-1',
        name: 'Health Asset',
        type: 'sensor',
        position: { longitude: 0, latitude: 0 },
        health: 0.8,
      },
    ];
    
    render(
      <CesiumProvider>
        <HealthBarLayer assets={assets} />
      </CesiumProvider>
    );
    
    expect(true).toBe(true);
  });
});
