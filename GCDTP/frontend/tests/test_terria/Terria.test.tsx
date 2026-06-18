/**
 * Tests for TerriaJS Module
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// Test types
import type {
  TerriaConfig,
  CatalogItem,
  CatalogItemType,
  LayerCatalog,
  StoryChapter,
  CameraPosition,
  ViewMode,
  TimeInterval
} from '../../src/terria/terria_types';

describe('Terria Types', () => {
  describe('CatalogItem', () => {
    it('should create a catalog item with required fields', () => {
      const item: CatalogItem = {
        id: 'test-1',
        name: 'Test Layer',
        type: CatalogItemType.WMS,
        isEnabled: false,
        showOnTimeline: false
      };
      
      expect(item.id).toBe('test-1');
      expect(item.name).toBe('Test Layer');
      expect(item.type).toBe(CatalogItemType.WMS);
    });
    
    it('should create a catalog item with optional fields', () => {
      const item: CatalogItem = {
        id: 'test-2',
        name: 'Test Layer',
        type: CatalogItemType.WFS,
        description: 'A test layer',
        url: 'http://example.com/wfs',
        isEnabled: true,
        showOnTimeline: true,
        metadataUrl: 'http://example.com/metadata',
        legendUrl: 'http://example.com/legend'
      };
      
      expect(item.description).toBe('A test layer');
      expect(item.url).toBe('http://example.com/wfs');
      expect(item.isEnabled).toBe(true);
    });
  });
  
  describe('ViewMode', () => {
    it('should have correct enum values', () => {
      expect(ViewMode.LEAFLET_2D).toBe('leaflet-2d');
      expect(ViewMode.CESIUM_3D).toBe('cesium-3d');
      expect(ViewMode.TERRA_FEDERATION).toBe('terria-federation');
    });
  });
  
  describe('CatalogItemType', () => {
    it('should have correct type values', () => {
      expect(CatalogItemType.WMS).toBe('wms');
      expect(CatalogItemType.WFS).toBe('wfs');
      expect(CatalogItemType.GeoJSON).toBe('geojson');
    });
  });
  
  describe('CameraPosition', () => {
    it('should create a camera position', () => {
      const position: CameraPosition = {
        longitude: -122.4,
        latitude: 37.8,
        height: 1000,
        heading: 0,
        pitch: -90,
        roll: 0
      };
      
      expect(position.longitude).toBe(-122.4);
      expect(position.latitude).toBe(37.8);
      expect(position.height).toBe(1000);
    });
  });
  
  describe('StoryChapter', () => {
    it('should create a story chapter', () => {
      const chapter: StoryChapter = {
        id: 'chapter-1',
        title: 'Introduction',
        narrative: 'This is the first chapter',
        cameraPosition: { longitude: 0, latitude: 0 },
        layerStates: []
      };
      
      expect(chapter.id).toBe('chapter-1');
      expect(chapter.title).toBe('Introduction');
    });
  });
  
  describe('TimeInterval', () => {
    it('should create a time interval', () => {
      const interval: TimeInterval = {
        start: '2024-01-01T00:00:00Z',
        end: '2024-12-31T23:59:59Z',
        isContinuous: true
      };
      
      expect(interval.start).toBe('2024-01-01T00:00:00Z');
      expect(interval.end).toBe('2024-12-31T23:59:59Z');
    });
  });
});

// Test ViewModeSwitcher
describe('ViewModeSwitcher', () => {
  it('should render mode buttons', () => {
    const { getByText } = render(
      <ViewModeSwitcher 
        currentMode={ViewMode.CESIUM_3D} 
        onModeChange={() => {}} 
      />
    );
    
    expect(getByText('Leaflet 2D')).toBeInTheDocument();
    expect(getByText('Cesium 3D')).toBeInTheDocument();
    expect(getByText('Terria Federation')).toBeInTheDocument();
  });
  
  it('should call onModeChange when button clicked', () => {
    const handleChange = jest.fn();
    const { getByText } = render(
      <ViewModeSwitcher 
        currentMode={ViewMode.CESIUM_3D} 
        onModeChange={handleChange} 
      />
    );
    
    fireEvent.click(getByText('Leaflet 2D'));
    expect(handleChange).toHaveBeenCalledWith(ViewMode.LEAFLET_2D);
  });
});

// Import for testing
import { ViewModeSwitcher } from '../../src/components/ViewModeSwitcher';

// Test LayerCatalog component
describe('LayerCatalog', () => {
  it('should render catalog items', () => {
    const catalogs = [
      {
        id: 'cat-1',
        name: 'Test Catalog',
        items: [
          {
            id: 'item-1',
            name: 'Layer 1',
            type: CatalogItemType.WMS,
            isEnabled: false,
            showOnTimeline: false
          }
        ],
        isOpen: true
      }
    ];
    
    const { getByText } = render(
      <LayerCatalog 
        catalogs={catalogs} 
        onItemSelect={() => {}}
        onItemToggle={() => {}}
      />
    );
    
    expect(getByText('Test Catalog')).toBeInTheDocument();
    expect(getByText('Layer 1')).toBeInTheDocument();
  });
});

// Import for testing
import { LayerCatalog } from '../../src/terria/LayerCatalog';

// Test MetadataExplorer component
describe('MetadataExplorer', () => {
  it('should show empty state when no item', () => {
    const { getByText } = render(
      <MetadataExplorer item={null} onClose={() => {}} />
    );
    
    expect(getByText('No item selected')).toBeInTheDocument();
  });
  
  it('should display item info', () => {
    const item: CatalogItem = {
      id: 'test-1',
      name: 'Test Layer',
      type: CatalogItemType.WMS,
      isEnabled: true,
      showOnTimeline: false,
      description: 'A test layer'
    };
    
    const { getByText } = render(
      <MetadataExplorer item={item} onClose={() => {}} />
    );
    
    expect(getByText('Test Layer')).toBeInTheDocument();
  });
});

// Import for testing
import { MetadataExplorer } from '../../src/terria/MetadataExplorer';

// Test ShareButton component
describe('ShareButton', () => {
  it('should render share button', () => {
    const { getByText } = render(
      <ShareButtonWrapper />
    );
    
    expect(getByText('Share')).toBeInTheDocument();
  });
});

// Test ModeBadge component
describe('ModeBadge', () => {
  it('should render correct badge for 2D mode', () => {
    const { getByText } = render(<ModeBadge mode={ViewMode.LEAFLET_2D} />);
    expect(getByText('2D')).toBeInTheDocument();
  });
  
  it('should render correct badge for 3D mode', () => {
    const { getByText } = render(<ModeBadge mode={ViewMode.CESIUM_3D} />);
    expect(getByText('3D')).toBeInTheDocument();
  });
  
  it('should render correct badge for Terria mode', () => {
    const { getByText } = render(<ModeBadge mode={ViewMode.TERRA_FEDERATION} />);
    expect(getByText('Terria')).toBeInTheDocument();
  });
});

// Import for testing
import { ModeBadge } from '../../src/components/ViewModeSwitcher';

// Helper wrapper for ShareButton (requires context)
function ShareButtonWrapper() {
  const TestShareProvider = ({ children }: { children: React.ReactNode }) => {
    return (
      <ShareProviderMock>
        {children}
      </ShareProviderMock>
    );
  };
  
  return (
    <TestShareProvider>
      <ShareButton />
    </TestShareProvider>
  );
}

// Mock ShareProvider
const ShareProviderMock = ({ children }: { children: React.ReactNode }) => {
  return <div>{children}</div>;
};
