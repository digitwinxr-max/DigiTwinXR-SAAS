/**
 * Vector Map Page
 */

import React, { useState } from 'react';
import {
  MapLibreProvider,
  VectorTileProvider,
  PMTilesProvider,
  StyleProvider,
  LayerProvider,
  OfflineProvider,
  TileCacheProvider,
  CameraProvider,
  SyncProvider,
  useMapLibre,
  useVectorTile,
  usePMTiles,
  useStyle,
  useLayer,
  useOffline,
  useTileCache,
  useCamera,
  useSync,
  MapLibreViewer,
  ViewerControls,
  ScaleBar,
  Attribution
} from '../maplibre';
import type { MapViewMode } from '../maplibre/maplibre_types';

interface VectorMapPageProps {
  initialConfig?: any;
}

export function VectorMapPage({ initialConfig }: VectorMapPageProps) {
  return (
    <MapLibreProvider initialConfig={initialConfig}>
      <SyncProvider>
        <VectorTileProvider>
          <PMTilesProvider>
            <StyleProvider>
              <LayerProvider>
                <OfflineProvider>
                  <TileCacheProvider>
                    <CameraProvider>
                      <VectorMapContent />
                    </CameraProvider>
                  </TileCacheProvider>
                </OfflineProvider>
              </LayerProvider>
            </StyleProvider>
          </PMTilesProvider>
        </VectorTileProvider>
      </SyncProvider>
    </MapLibreProvider>
  );
}

function VectorMapContent() {
  const { camera, setCamera } = useCamera();
  const { currentMode, setCurrentMode } = useSync();
  const { layers } = useLayer();
  const { stats } = useTileCache();
  
  const [showControls, setShowControls] = useState(true);

  return (
    <div className="vector-map-page">
      {/* Header */}
      <header className="map-header">
        <h1>GCDTP Vector Map</h1>
        <div className="header-actions">
          <button onClick={() => setShowControls(!showControls)}>
            {showControls ? 'Hide' : 'Show'} Controls
          </button>
        </div>
      </header>

      {/* Map Mode Switcher */}
      <MapModeSwitcher />

      <div className="map-layout">
        {/* Sidebar */}
        <aside className="map-sidebar">
          <LayerPanel />
          <TileCachePanel stats={stats} />
        </aside>

        {/* Main Content */}
        <main className="map-main">
          <MapLibreViewer
            camera={camera}
            onCameraChange={setCamera}
          />
          
          {showControls && (
            <div className="map-overlay">
              <ViewerControls
                onZoomIn={() => {}}
                onZoomOut={() => {}}
                onResetView={() => {}}
                onFullscreen={() => {}}
              />
            </div>
          )}
          
          <div className="map-footer">
            <ScaleBar />
            <Attribution />
          </div>
        </main>
      </div>
    </div>
  );
}

// Layer Panel
function LayerPanel() {
  const { layers, setLayerVisibility, setLayerOpacity } = useLayer();
  
  return (
    <div className="layer-panel">
      <h3>Layers</h3>
      {layers.length === 0 ? (
        <p className="empty-message">No layers added</p>
      ) : (
        <ul className="layer-list">
          {layers.map(layer => (
            <li key={layer.id} className="layer-item">
              <label>
                <input
                  type="checkbox"
                  checked={layer.visible}
                  onChange={() => setLayerVisibility(layer.id, !layer.visible)}
                />
                {layer.name}
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={layer.opacity * 100}
                onChange={(e) => setLayerOpacity(layer.id, Number(e.target.value) / 100)}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// Tile Cache Panel
function TileCachePanel({ stats }: { stats: any }) {
  return (
    <div className="cache-panel">
      <h3>Tile Cache</h3>
      <div className="cache-stats">
        <div>Hits: {stats.hits}</div>
        <div>Misses: {stats.misses}</div>
        <div>Size: {(stats.size / 1024).toFixed(1)} KB</div>
      </div>
    </div>
  );
}

// Import MapModeSwitcher
import { MapModeSwitcher } from '../components/MapModeSwitcher';
