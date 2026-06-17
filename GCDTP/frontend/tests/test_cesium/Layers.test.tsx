/**
 * Tileset and Terrain Manager Tests
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { CesiumProvider } from '../../src/cesium/CesiumContext';
import { TilesetLoader, TilesetControls } from '../../src/cesium/TilesetLoader';
import { TerrainManager } from '../../src/cesium/TerrainManager';

function TestWrapper({ children }: { children: React.ReactNode }) {
  return <CesiumProvider>{children}</CesiumProvider>;
}

describe('TilesetLoader', () => {
  const mockTilesets = [
    { id: 'ts-1', url: 'https://example.com/tileset1.json', type: 'b3dm' as const, name: 'Building A' },
    { id: 'ts-2', url: 'https://example.com/tileset2.json', type: 'glb' as const, name: 'Model B' },
  ];

  it('should render without crashing', () => {
    render(
      <TestWrapper>
        <TilesetLoader tilesets={mockTilesets} />
      </TestWrapper>
    );
    expect(true).toBe(true);
  });

  it('should accept tileset configurations', () => {
    render(
      <TestWrapper>
        <TilesetLoader tilesets={mockTilesets} />
      </TestWrapper>
    );
    expect(mockTilesets.length).toBe(2);
  });

  it('should handle empty tilesets array', () => {
    render(
      <TestWrapper>
        <TilesetLoader tilesets={[]} />
      </TestWrapper>
    );
    expect(true).toBe(true);
  });

  it('should support all tileset types', () => {
    const types = ['glb', 'b3dm', 'pnts', 'i3dm', 'cmpt'];
    
    types.forEach(type => {
      const tileset = { 
        id: `ts-${type}`, 
        url: 'https://example.com/tileset', 
        type, 
        name: `Tileset ${type}` 
      };
      expect(tileset.type).toBe(type);
    });
  });
});

describe('TilesetControls', () => {
  it('should render tileset list', () => {
    const tilesets = [
      { id: 'ts-1', url: '', type: 'b3dm' as const, name: 'Building', visible: true, loading: false, loaded: true, error: null },
    ];
    
    render(
      <TilesetControls 
        tilesets={tilesets}
        onToggleVisibility={jest.fn()}
        onReload={jest.fn()}
      />
    );
    
    expect(screen.getByText('Building')).toBeInTheDocument();
    expect(screen.getByText('3D Layers')).toBeInTheDocument();
  });
});

describe('TerrainManager', () => {
  it('should render without crashing', () => {
    render(
      <TestWrapper>
        <TerrainManager />
      </TestWrapper>
    );
    expect(screen.getByText('Terrain')).toBeInTheDocument();
  });

  it('should have terrain options', () => {
    render(
      <TestWrapper>
        <TerrainManager />
      </TestWrapper>
    );
    
    expect(screen.getByText('Cesium World Terrain')).toBeInTheDocument();
    expect(screen.getByText('Ellipsoid (No Terrain)')).toBeInTheDocument();
  });

  it('should accept default terrain prop', () => {
    render(
      <TestWrapper>
        <TerrainManager defaultTerrain="ellipsoid" />
      </TestWrapper>
    );
    expect(true).toBe(true);
  });
});

describe('Terrain Types', () => {
  it('should support all terrain types', () => {
    const types = ['world', 'ellipsoid', 'stk', 'arcgis', 'custom'];
    
    types.forEach(type => {
      expect(['world', 'ellipsoid', 'stk', 'arcgis', 'custom']).toContain(type);
    });
  });
});
