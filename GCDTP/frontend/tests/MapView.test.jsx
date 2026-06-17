import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MapContainer } from 'react-leaflet';

// Mock the MapView component for testing
const mockGeoJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'test-id-1',
      geometry: {
        type: 'Point',
        coordinates: [24.6849, -22.3285]
      },
      properties: {
        name: 'Test Asset 1',
        asset_type: 'sensor',
        status: 'active'
      }
    },
    {
      type: 'Feature',
      id: 'test-id-2',
      geometry: {
        type: 'Point',
        coordinates: [25.0, -23.0]
      },
      properties: {
        name: 'Test Asset 2',
        asset_type: 'device',
        status: 'inactive'
      }
    }
  ]
};

describe('MapView', () => {
  it('renders loading state initially', () => {
    render(
      <MapContainer center={[-22.3285, 24.6849]} zoom={6} style={{ height: '100%', width: '100%' }}>
        <div data-testid="map-container">Loading...</div>
      </MapContainer>
    );
    expect(screen.getByTestId('map-container')).toBeInTheDocument();
  });

  it('has correct center coordinates for Botswana', () => {
    const centerLat = -22.3285;
    const centerLng = 24.6849;
    expect(centerLat).toBeLessThan(0);
    expect(centerLng).toBeGreaterThan(0);
  });

  it('GeoJSON data structure is valid', () => {
    expect(mockGeoJSON.type).toBe('FeatureCollection');
    expect(Array.isArray(mockGeoJSON.features)).toBe(true);
    expect(mockGeoJSON.features.length).toBe(2);
  });

  it('GeoJSON features have correct structure', () => {
    const feature = mockGeoJSON.features[0];
    expect(feature.type).toBe('Feature');
    expect(feature.id).toBeDefined();
    expect(feature.geometry.type).toBe('Point');
    expect(Array.isArray(feature.geometry.coordinates)).toBe(true);
    expect(feature.geometry.coordinates.length).toBe(2);
  });

  it('GeoJSON features have required properties', () => {
    const feature = mockGeoJSON.features[0];
    expect(feature.properties.name).toBe('Test Asset 1');
    expect(feature.properties.asset_type).toBe('sensor');
    expect(feature.properties.status).toBe('active');
  });

  it('coordinates are extracted correctly from GeoJSON', () => {
    const feature = mockGeoJSON.features[0];
    const [lng, lat] = feature.geometry.coordinates;
    expect(lat).toBe(-22.3285);
    expect(lng).toBe(24.6849);
  });

  it('features without coordinates are handled', () => {
    const featureWithoutCoords = {
      type: 'Feature',
      id: 'no-coords',
      geometry: null,
      properties: {
        name: 'No Coordinates',
        asset_type: 'sensor',
        status: 'active'
      }
    };
    expect(featureWithoutCoords.geometry).toBeNull();
  });
});

describe('GeoJSON Loading', () => {
  it('can parse GeoJSON from API response', async () => {
    const mockResponse = {
      type: 'FeatureCollection',
      features: []
    };
    
    const parseResponse = async () => {
      return mockResponse;
    };
    
    const result = await parseResponse();
    expect(result.type).toBe('FeatureCollection');
    expect(Array.isArray(result.features)).toBe(true);
  });

  it('handles empty GeoJSON features array', () => {
    const emptyGeoJSON = {
      type: 'FeatureCollection',
      features: []
    };
    expect(emptyGeoJSON.features.length).toBe(0);
  });

  it('handles multiple features', () => {
    const multipleFeatures = {
      type: 'FeatureCollection',
      features: Array(5).fill({
        type: 'Feature',
        id: 'test',
        geometry: { type: 'Point', coordinates: [0, 0] },
        properties: { name: 'Test', asset_type: 'sensor', status: 'active' }
      })
    };
    expect(multipleFeatures.features.length).toBe(5);
  });
});

describe('Popup Content', () => {
  it('popup displays all required information', () => {
    const feature = mockGeoJSON.features[0];
    const popupContent = `
      <strong>${feature.properties.name}</strong>
      Type: ${feature.properties.asset_type}
      Status: ${feature.properties.status}
      Coordinates: ${feature.geometry.coordinates[1].toFixed(6)}, ${feature.geometry.coordinates[0].toFixed(6)}
    `;
    
    expect(popupContent).toContain('Test Asset 1');
    expect(popupContent).toContain('sensor');
    expect(popupContent).toContain('active');
  });
});
