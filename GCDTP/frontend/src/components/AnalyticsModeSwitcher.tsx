/**
 * Analytics Mode Switcher Component
 * 
 * Provides switching between Leaflet 2D, MapLibre Vector, Cesium 3D, Terria Federation, and Kepler Analytics modes.
 */

import React from 'react';
import { AnalyticsViewMode } from '../kepler/kepler_types';

interface AnalyticsModeSwitcherProps {
  currentMode: AnalyticsViewMode;
  onModeChange: (mode: AnalyticsViewMode) => void;
  className?: string;
}

export function AnalyticsModeSwitcher({ currentMode, onModeChange, className = '' }: AnalyticsModeSwitcherProps) {
  return (
    <div className={`analytics-mode-switcher ${className}`}>
      <button
        className={`mode-btn ${currentMode === AnalyticsViewMode.LEAFLET_2D ? 'active' : ''}`}
        onClick={() => onModeChange(AnalyticsViewMode.LEAFLET_2D)}
        title="2D Map View"
      >
        <span className="mode-icon">🗺️</span>
        <span className="mode-label">Leaflet 2D</span>
      </button>
      
      <button
        className={`mode-btn ${currentMode === AnalyticsViewMode.MAPLIBRE_VECTOR ? 'active' : ''}`}
        onClick={() => onModeChange(AnalyticsViewMode.MAPLIBRE_VECTOR)}
        title="Vector Tile View"
      >
        <span className="mode-icon">🗃️</span>
        <span className="mode-label">MapLibre Vector</span>
      </button>
      
      <button
        className={`mode-btn ${currentMode === AnalyticsViewMode.CESIUM_3D ? 'active' : ''}`}
        onClick={() => onModeChange(AnalyticsViewMode.CESIUM_3D)}
        title="3D Globe View"
      >
        <span className="mode-icon">🌍</span>
        <span className="mode-label">Cesium 3D</span>
      </button>
      
      <button
        className={`mode-btn ${currentMode === AnalyticsViewMode.TERRA_FEDERATION ? 'active' : ''}`}
        onClick={() => onModeChange(AnalyticsViewMode.TERRA_FEDERATION)}
        title="Terria Federation View"
      >
        <span className="mode-icon">🔗</span>
        <span className="mode-label">Terria Federation</span>
      </button>
      
      <button
        className={`mode-btn ${currentMode === AnalyticsViewMode.KEPLER_ANALYTICS ? 'active' : ''}`}
        onClick={() => onModeChange(AnalyticsViewMode.KEPLER_ANALYTICS)}
        title="Kepler Analytics View"
      >
        <span className="mode-icon">📊</span>
        <span className="mode-label">Kepler Analytics</span>
      </button>
    </div>
  );
}

// Hook for analytics mode management
export function useAnalyticsModeSwitcher() {
  return {
    modes: [
      { mode: AnalyticsViewMode.LEAFLET_2D, label: 'Leaflet 2D', icon: '🗺️' },
      { mode: AnalyticsViewMode.MAPLIBRE_VECTOR, label: 'MapLibre Vector', icon: '🗃️' },
      { mode: AnalyticsViewMode.CESIUM_3D, label: 'Cesium 3D', icon: '🌍' },
      { mode: AnalyticsViewMode.TERRA_FEDERATION, label: 'Terria Federation', icon: '🔗' },
      { mode: AnalyticsViewMode.KEPLER_ANALYTICS, label: 'Kepler Analytics', icon: '📊' }
    ]
  };
}

// Compact version for toolbar
interface CompactAnalyticsModeSwitcherProps {
  currentMode: AnalyticsViewMode;
  onModeChange: (mode: AnalyticsViewMode) => void;
}

export function CompactAnalyticsModeSwitcher({ currentMode, onModeChange }: CompactAnalyticsModeSwitcherProps) {
  const getIcon = () => {
    switch (currentMode) {
      case AnalyticsViewMode.LEAFLET_2D:
        return '🗺️';
      case AnalyticsViewMode.MAPLIBRE_VECTOR:
        return '🗃️';
      case AnalyticsViewMode.CESIUM_3D:
        return '🌍';
      case AnalyticsViewMode.TERRA_FEDERATION:
        return '🔗';
      case AnalyticsViewMode.KEPLER_ANALYTICS:
        return '📊';
      default:
        return '🗺️';
    }
  };

  return (
    <div className="compact-analytics-mode-switcher">
      <select
        value={currentMode}
        onChange={(e) => onModeChange(e.target.value as AnalyticsViewMode)}
        className="mode-select"
      >
        <option value={AnalyticsViewMode.LEAFLET_2D}>🗺️ Leaflet 2D</option>
        <option value={AnalyticsViewMode.MAPLIBRE_VECTOR}>🗃️ MapLibre Vector</option>
        <option value={AnalyticsViewMode.CESIUM_3D}>🌍 Cesium 3D</option>
        <option value={AnalyticsViewMode.TERRA_FEDERATION}>🔗 Terria Federation</option>
        <option value={AnalyticsViewMode.KEPLER_ANALYTICS}>📊 Kepler Analytics</option>
      </select>
    </div>
  );
}

// Mode indicator badge
interface AnalyticsModeBadgeProps {
  mode: AnalyticsViewMode;
}

export function AnalyticsModeBadge({ mode }: AnalyticsModeBadgeProps) {
  const getConfig = () => {
    switch (mode) {
      case AnalyticsViewMode.LEAFLET_2D:
        return { label: '2D', color: '#4CAF50' };
      case AnalyticsViewMode.MAPLIBRE_VECTOR:
        return { label: 'Vector', color: '#9C27B0' };
      case AnalyticsViewMode.CESIUM_3D:
        return { label: '3D', color: '#2196F3' };
      case AnalyticsViewMode.TERRA_FEDERATION:
        return { label: 'Terria', color: '#FF9800' };
      case AnalyticsViewMode.KEPLER_ANALYTICS:
        return { label: 'Analytics', color: '#E91E63' };
      default:
        return { label: 'Unknown', color: '#9E9E9E' };
    }
  };

  const config = getConfig();

  return (
    <span 
      className="analytics-mode-badge"
      style={{ backgroundColor: config.color }}
    >
      {config.label}
    </span>
  );
}
