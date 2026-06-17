/**
 * Scene Controller
 * 
 * Manages 3D scene state, layers, and visualization modes.
 * Part of the dual-view architecture (Leaflet 2D + Cesium 3D).
 */

import React, { useState, useCallback, useMemo } from 'react';
import { useCesium } from './CesiumContext';

// Layer types
export type LayerType = 
  | 'assets'
  | 'sensors'
  | 'events'
  | 'health'
  | 'workOrders'
  | 'documents'
  | 'topology'
  | 'routes'
  | 'simulation'
  | 'timeline';

interface LayerState {
  id: LayerType;
  name: string;
  visible: boolean;
  opacity: number;
  color?: string;
}

interface SceneConfig {
  mode: '3D' | '2D';
  enableLighting: boolean;
  enableAtmosphere: boolean;
  enableFog: boolean;
}

interface SceneControllerProps {
  onLayerChange?: (layers: LayerState[]) => void;
}

// Default layer configuration
const DEFAULT_LAYERS: LayerState[] = [
  { id: 'assets', name: 'Assets', visible: true, opacity: 1.0 },
  { id: 'sensors', name: 'Sensors', visible: true, opacity: 1.0 },
  { id: 'events', name: 'Events', visible: true, opacity: 1.0 },
  { id: 'health', name: 'Health', visible: true, opacity: 0.8 },
  { id: 'workOrders', name: 'Work Orders', visible: true, opacity: 1.0 },
  { id: 'documents', name: 'Documents', visible: false, opacity: 1.0 },
  { id: 'topology', name: 'Topology', visible: true, opacity: 0.7 },
  { id: 'routes', name: 'Routes', visible: true, opacity: 1.0 },
  { id: 'simulation', name: 'Simulation', visible: false, opacity: 1.0 },
  { id: 'timeline', name: 'Timeline', visible: false, opacity: 1.0 },
];

export function SceneController({
  onLayerChange,
}: SceneControllerProps): JSX.Element {
  const { viewer, setSceneMode, sceneMode } = useCesium();
  const [layers, setLayers] = useState<LayerState[]>(DEFAULT_LAYERS);
  const [config, setConfig] = useState<SceneConfig>({
    mode: '3D',
    enableLighting: false,
    enableAtmosphere: true,
    enableFog: false,
  });

  // Toggle layer visibility
  const toggleLayer = useCallback((layerId: LayerType) => {
    setLayers(prev => {
      const updated = prev.map(layer =>
        layer.id === layerId
          ? { ...layer, visible: !layer.visible }
          : layer
      );
      onLayerChange?.(updated);
      return updated;
    });
  }, [onLayerChange]);

  // Set layer opacity
  const setLayerOpacity = useCallback((layerId: LayerType, opacity: number) => {
    setLayers(prev => {
      const updated = prev.map(layer =>
        layer.id === layerId
          ? { ...layer, opacity }
          : layer
      );
      onLayerChange?.(updated);
      return updated;
    });
  }, [onLayerChange]);

  // Toggle scene mode (3D/2D)
  const toggleSceneMode = useCallback(() => {
    const newMode = config.mode === '3D' ? '2D' : '3D';
    setConfig(prev => ({ ...prev, mode: newMode }));
    setSceneMode(newMode);
  }, [config.mode, setSceneMode]);

  // Toggle lighting
  const toggleLighting = useCallback(() => {
    setConfig(prev => ({ ...prev, enableLighting: !prev.enableLighting }));
  }, []);

  // Toggle atmosphere
  const toggleAtmosphere = useCallback(() => {
    setConfig(prev => ({ ...prev, enableAtmosphere: !prev.enableAtmosphere }));
  }, []);

  // Toggle fog
  const toggleFog = useCallback(() => {
    setConfig(prev => ({ ...prev, enableFog: !prev.enableFog }));
  }, []);

  // Visible layers count
  const visibleCount = useMemo(() =>
    layers.filter(l => l.visible).length,
    [layers]
  );

  return (
    <div className="scene-controller">
      {/* Scene Mode Toggle */}
      <div className="scene-mode-section">
        <h4>View Mode</h4>
        <div className="scene-mode-buttons">
          <button
            className={config.mode === '3D' ? 'active' : ''}
            onClick={() => { if (config.mode !== '3D') toggleSceneMode(); }}
          >
            3D Globe
          </button>
          <button
            className={config.mode === '2D' ? 'active' : ''}
            onClick={() => { if (config.mode !== '2D') toggleSceneMode(); }}
          >
            2D Map
          </button>
        </div>
      </div>

      {/* Layer List */}
      <div className="layers-section">
        <h4>
          Layers
          <span className="layer-count">{visibleCount}/{layers.length}</span>
        </h4>
        <ul className="layer-list">
          {layers.map(layer => (
            <li key={layer.id} className="layer-item">
              <label className="layer-label">
                <input
                  type="checkbox"
                  checked={layer.visible}
                  onChange={() => toggleLayer(layer.id)}
                />
                <span className="layer-name">{layer.name}</span>
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={layer.opacity}
                onChange={(e) => setLayerOpacity(layer.id, parseFloat(e.target.value))}
                className="layer-opacity"
                disabled={!layer.visible}
              />
            </li>
          ))}
        </ul>
      </div>

      {/* Scene Options */}
      <div className="scene-options-section">
        <h4>Scene Options</h4>
        <label className="option-toggle">
          <input
            type="checkbox"
            checked={config.enableLighting}
            onChange={toggleLighting}
          />
          <span>Lighting</span>
        </label>
        <label className="option-toggle">
          <input
            type="checkbox"
            checked={config.enableAtmosphere}
            onChange={toggleAtmosphere}
          />
          <span>Atmosphere</span>
        </label>
        <label className="option-toggle">
          <input
            type="checkbox"
            checked={config.enableFog}
            onChange={toggleFog}
          />
          <span>Fog</span>
        </label>
      </div>
    </div>
  );
}

// Hook for managing scene layers
export function useSceneLayers() {
  const [layers, setLayers] = useState<LayerState[]>(DEFAULT_LAYERS);

  const showLayer = useCallback((layerId: LayerType) => {
    setLayers(prev =>
      prev.map(layer =>
        layer.id === layerId
          ? { ...layer, visible: true }
          : layer
      )
    );
  }, []);

  const hideLayer = useCallback((layerId: LayerType) => {
    setLayers(prev =>
      prev.map(layer =>
        layer.id === layerId
          ? { ...layer, visible: false }
          : layer
      )
    );
  }, []);

  const setLayerVisible = useCallback((layerId: LayerType, visible: boolean) => {
    setLayers(prev =>
      prev.map(layer =>
        layer.id === layerId
          ? { ...layer, visible }
          : layer
      )
    );
  }, []);

  const getVisibleLayers = useCallback(() =>
    layers.filter(l => l.visible),
    [layers]
  );

  return {
    layers,
    showLayer,
    hideLayer,
    setLayerVisible,
    getVisibleLayers,
    setLayers,
  };
}

export default SceneController;
