/**
 * View Mode Switcher Component
 * 
 * Provides switching between Leaflet 2D, Cesium 3D, and Terria Federation modes.
 */

import React from 'react';
import { ViewMode } from '../terria/terria_types';

interface ViewModeSwitcherProps {
  currentMode: ViewMode;
  onModeChange: (mode: ViewMode) => void;
  className?: string;
}

export function ViewModeSwitcher({ currentMode, onModeChange, className = '' }: ViewModeSwitcherProps) {
  return (
    <div className={`view-mode-switcher ${className}`}>
      <button
        className={`mode-btn ${currentMode === ViewMode.LEAFLET_2D ? 'active' : ''}`}
        onClick={() => onModeChange(ViewMode.LEAFLET_2D)}
        title="2D Map View"
      >
        <span className="mode-icon">🗺️</span>
        <span className="mode-label">Leaflet 2D</span>
      </button>
      
      <button
        className={`mode-btn ${currentMode === ViewMode.CESIUM_3D ? 'active' : ''}`}
        onClick={() => onModeChange(ViewMode.CESIUM_3D)}
        title="3D Globe View"
      >
        <span className="mode-icon">🌍</span>
        <span className="mode-label">Cesium 3D</span>
      </button>
      
      <button
        className={`mode-btn ${currentMode === ViewMode.TERRA_FEDERATION ? 'active' : ''}`}
        onClick={() => onModeChange(ViewMode.TERRA_FEDERATION)}
        title="Terria Federation View"
      >
        <span className="mode-icon">🔗</span>
        <span className="mode-label">Terria Federation</span>
      </button>
    </div>
  );
}

// Hook for view mode management
export function useViewModeSwitcher() {
  return {
    modes: [
      { mode: ViewMode.LEAFLET_2D, label: 'Leaflet 2D', icon: '🗺️' },
      { mode: ViewMode.CESIUM_3D, label: 'Cesium 3D', icon: '🌍' },
      { mode: ViewMode.TERRA_FEDERATION, label: 'Terria Federation', icon: '🔗' }
    ]
  };
}

// Compact version for toolbar
interface CompactModeSwitcherProps {
  currentMode: ViewMode;
  onModeChange: (mode: ViewMode) => void;
}

export function CompactModeSwitcher({ currentMode, onModeChange }: CompactModeSwitcherProps) {
  const getIcon = () => {
    switch (currentMode) {
      case ViewMode.LEAFLET_2D:
        return '🗺️';
      case ViewMode.CESIUM_3D:
        return '🌍';
      case ViewMode.TERRA_FEDERATION:
        return '🔗';
      default:
        return '🗺️';
    }
  };

  return (
    <div className="compact-mode-switcher">
      <select
        value={currentMode}
        onChange={(e) => onModeChange(e.target.value as ViewMode)}
        className="mode-select"
      >
        <option value={ViewMode.LEAFLET_2D}>🗺️ Leaflet 2D</option>
        <option value={ViewMode.CESIUM_3D}>🌍 Cesium 3D</option>
        <option value={ViewMode.TERRA_FEDERATION}>🔗 Terria Federation</option>
      </select>
    </div>
  );
}

// Mode indicator badge
interface ModeBadgeProps {
  mode: ViewMode;
}

export function ModeBadge({ mode }: ModeBadgeProps) {
  const getConfig = () => {
    switch (mode) {
      case ViewMode.LEAFLET_2D:
        return { label: '2D', color: '#4CAF50' };
      case ViewMode.CESIUM_3D:
        return { label: '3D', color: '#2196F3' };
      case ViewMode.TERRA_FEDERATION:
        return { label: 'Terria', color: '#FF9800' };
      default:
        return { label: 'Unknown', color: '#9E9E9E' };
    }
  };

  const config = getConfig();

  return (
    <span 
      className="mode-badge"
      style={{ backgroundColor: config.color }}
    >
      {config.label}
    </span>
  );
}
