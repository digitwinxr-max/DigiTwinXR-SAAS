/**
 * Map Mode Switcher Component
 * 
 * Provides switching between Leaflet 2D, MapLibre Vector, Cesium 3D, and Terria Federation modes.
 */

import React from 'react';
import { MapViewMode } from '../maplibre/maplibre_types';

interface MapModeSwitcherProps {
  currentMode: MapViewMode;
  onModeChange: (mode: MapViewMode) => void;
  className?: string;
}

export function MapModeSwitcher({ currentMode, onModeChange, className = '' }: MapModeSwitcherProps) {
  return (
    <div className={`map-mode-switcher ${className}`}>
      <button
        className={`mode-btn ${currentMode === MapViewMode.LEAFLET_2D ? 'active' : ''}`}
        onClick={() => onModeChange(MapViewMode.LEAFLET_2D)}
        title="2D Map View"
      >
        <span className="mode-icon">🗺️</span>
        <span className="mode-label">Leaflet 2D</span>
      </button>
      
      <button
        className={`mode-btn ${currentMode === MapViewMode.MAPLIBRE_VECTOR ? 'active' : ''}`}
        onClick={() => onModeChange(MapViewMode.MAPLIBRE_VECTOR)}
        title="Vector Tile View"
      >
        <span className="mode-icon">🗃️</span>
        <span className="mode-label">MapLibre Vector</span>
      </button>
      
      <button
        className={`mode-btn ${currentMode === MapViewMode.CESIUM_3D ? 'active' : ''}`}
        onClick={() => onModeChange(MapViewMode.CESIUM_3D)}
        title="3D Globe View"
      >
        <span className="mode-icon">🌍</span>
        <span className="mode-label">Cesium 3D</span>
      </button>
      
      <button
        className={`mode-btn ${currentMode === MapViewMode.TERRA_FEDERATION ? 'active' : ''}`}
        onClick={() => onModeChange(MapViewMode.TERRA_FEDERATION)}
        title="Terria Federation View"
      >
        <span className="mode-icon">🔗</span>
        <span className="mode-label">Terria Federation</span>
      </button>
    </div>
  );
}

// Hook for map mode management
export function useMapModeSwitcher() {
  return {
    modes: [
      { mode: MapViewMode.LEAFLET_2D, label: 'Leaflet 2D', icon: '🗺️' },
      { mode: MapViewMode.MAPLIBRE_VECTOR, label: 'MapLibre Vector', icon: '🗃️' },
      { mode: MapViewMode.CESIUM_3D, label: 'Cesium 3D', icon: '🌍' },
      { mode: MapViewMode.TERRA_FEDERATION, label: 'Terria Federation', icon: '🔗' }
    ]
  };
}

// Compact version for toolbar
interface CompactMapModeSwitcherProps {
  currentMode: MapViewMode;
  onModeChange: (mode: MapViewMode) => void;
}

export function CompactMapModeSwitcher({ currentMode, onModeChange }: CompactMapModeSwitcherProps) {
  const getIcon = () => {
    switch (currentMode) {
      case MapViewMode.LEAFLET_2D:
        return '🗺️';
      case MapViewMode.MAPLIBRE_VECTOR:
        return '🗃️';
      case MapViewMode.CESIUM_3D:
        return '🌍';
      case MapViewMode.TERRA_FEDERATION:
        return '🔗';
      default:
        return '🗺️';
    }
  };

  return (
    <div className="compact-map-mode-switcher">
      <select
        value={currentMode}
        onChange={(e) => onModeChange(e.target.value as MapViewMode)}
        className="mode-select"
      >
        <option value={MapViewMode.LEAFLET_2D}>🗺️ Leaflet 2D</option>
        <option value={MapViewMode.MAPLIBRE_VECTOR}>🗃️ MapLibre Vector</option>
        <option value={MapViewMode.CESIUM_3D}>🌍 Cesium 3D</option>
        <option value={MapViewMode.TERRA_FEDERATION}>🔗 Terria Federation</option>
      </select>
    </div>
  );
}

// Mode indicator badge
interface MapModeBadgeProps {
  mode: MapViewMode;
}

export function MapModeBadge({ mode }: MapModeBadgeProps) {
  const getConfig = () => {
    switch (mode) {
      case MapViewMode.LEAFLET_2D:
        return { label: '2D', color: '#4CAF50' };
      case MapViewMode.MAPLIBRE_VECTOR:
        return { label: 'Vector', color: '#9C27B0' };
      case MapViewMode.CESIUM_3D:
        return { label: '3D', color: '#2196F3' };
      case MapViewMode.TERRA_FEDERATION:
        return { label: 'Terria', color: '#FF9800' };
      default:
        return { label: 'Unknown', color: '#9E9E9E' };
    }
  };

  const config = getConfig();

  return (
    <span 
      className="map-mode-badge"
      style={{ backgroundColor: config.color }}
    >
      {config.label}
    </span>
  );
}
