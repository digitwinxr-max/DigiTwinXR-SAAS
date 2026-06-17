/**
 * View Switcher
 * 
 * Toggle between 2D (Leaflet) and 3D (Cesium) views.
 * Part of the dual-view architecture.
 */

import React, { useState, useCallback } from 'react';

export type ViewMode = '2D' | '3D';

interface ViewSwitcherProps {
  currentMode: ViewMode;
  onModeChange: (mode: ViewMode) => void;
  disabled?: boolean;
}

export function ViewSwitcher({
  currentMode,
  onModeChange,
  disabled = false,
}: ViewSwitcherProps): JSX.Element {
  const handleModeChange = useCallback((mode: ViewMode) => {
    if (!disabled && mode !== currentMode) {
      onModeChange(mode);
    }
  }, [currentMode, disabled, onModeChange]);

  return (
    <div className="view-switcher">
      <div className="view-switcher-container">
        {/* 2D Button */}
        <button
          className={`view-btn ${currentMode === '2D' ? 'active' : ''}`}
          onClick={() => handleModeChange('2D')}
          disabled={disabled}
          title="2D Map View (Leaflet)"
        >
          <span className="view-icon">🗺️</span>
          <span className="view-label">2D</span>
        </button>

        {/* Divider */}
        <div className="view-divider" />

        {/* 3D Button */}
        <button
          className={`view-btn ${currentMode === '3D' ? 'active' : ''}`}
          onClick={() => handleModeChange('3D')}
          disabled={disabled}
          title="3D Globe View (Cesium)"
        >
          <span className="view-icon">🌍</span>
          <span className="view-label">3D</span>
        </button>
      </div>

      {/* Current Mode Indicator */}
      <div className="mode-indicator">
        {currentMode === '2D' ? (
          <span className="mode-label">
            2D Map View
          </span>
        ) : (
          <span className="mode-label">
            3D Globe View
          </span>
        )}
      </div>
    </div>
  );
}

// Hook for managing view mode
export function useViewSwitcher(initialMode: ViewMode = '2D') {
  const [mode, setMode] = useState<ViewMode>(initialMode);

  const switchTo2D = useCallback(() => {
    setMode('2D');
  }, []);

  const switchTo3D = useCallback(() => {
    setMode('3D');
  }, []);

  const toggleMode = useCallback(() => {
    setMode(prev => prev === '2D' ? '3D' : '2D');
  }, []);

  return {
    mode,
    setMode,
    switchTo2D,
    switchTo3D,
    toggleMode,
    is2D: mode === '2D',
    is3D: mode === '3D',
  };
}

export default ViewSwitcher;
