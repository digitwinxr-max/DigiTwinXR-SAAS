/**
 * Digital Twin 3D Page
 * 
 * Main page for 3D digital twin visualization.
 * Integrates with Cesium for globe visualization.
 * Part of the dual-view architecture (Leaflet 2D + Cesium 3D).
 */

import React, { useState, useEffect, useCallback } from 'react';
import { CesiumProvider, useCesium } from '../cesium/CesiumContext';
import { GlobeViewer } from '../cesium/GlobeViewer';
import { Asset3DLayer } from '../cesium/Asset3DLayer';
import { TilesetLoader } from '../cesium/TilesetLoader';
import { TerrainManager } from '../cesium/TerrainManager';
import { SceneController } from '../cesium/SceneController';
import { CameraController } from '../cesium/CameraController';
import { TimelineController, TimelineEvent } from '../cesium/TimelineController';

// Asset data types
interface Asset {
  id: string;
  name: string;
  type: string;
  position: {
    longitude: number;
    latitude: number;
    height?: number;
  };
  status?: 'healthy' | 'warning' | 'critical' | 'offline';
  health?: number;
}

// Tileset configuration
interface TilesetConfig {
  id: string;
  url: string;
  type: string;
  name: string;
}

interface DigitalTwin3DPageProps {
  assets?: Asset[];
  tilesets?: TilesetConfig[];
  initialPosition?: {
    longitude: number;
    latitude: number;
    height: number;
  };
}

// Inner component that uses Cesium context
function DigitalTwin3DPageContent({
  assets = [],
  tilesets = [],
}: DigitalTwin3DPageProps) {
  const { 
    initializeViewer, 
    isInitialized, 
    error,
    timeline 
  } = useCesium();

  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);
  const [showControls, setShowControls] = useState(true);
  const [showTimeline, setShowTimeline] = useState(false);

  // Initialize viewer on mount
  useEffect(() => {
    if (!isInitialized) {
      initializeViewer('cesium-container');
    }
  }, [initializeViewer, isInitialized]);

  // Handle asset selection
  const handleAssetClick = useCallback((asset: Asset) => {
    setSelectedAssetId(asset.id);
    console.log('Selected asset:', asset);
  }, []);

  // Handle asset hover
  const handleAssetHover = useCallback((asset: Asset | null) => {
    // Could show tooltip or highlight
  }, []);

  // Sample events for timeline (in real app, would come from Timeline Engine)
  const timelineEvents: TimelineEvent[] = [
    {
      id: 'evt-1',
      timestamp: new Date('2024-01-15T10:30:00'),
      type: 'node_failed',
      entityId: 'asset-1',
    },
    {
      id: 'evt-2',
      timestamp: new Date('2024-01-15T10:35:00'),
      type: 'route_changed',
      entityId: 'route-1',
    },
    {
      id: 'evt-3',
      timestamp: new Date('2024-01-15T10:40:00'),
      type: 'node_recovered',
      entityId: 'asset-1',
    },
  ];

  return (
    <div className="digital-twin-3d-page">
      {/* Header */}
      <div className="page-header">
        <h1>Digital Twin 3D View</h1>
        <div className="header-actions">
          <button 
            className="toggle-btn"
            onClick={() => setShowControls(!showControls)}
          >
            {showControls ? 'Hide Controls' : 'Show Controls'}
          </button>
          <button 
            className="toggle-btn"
            onClick={() => setShowTimeline(!showTimeline)}
          >
            {showTimeline ? 'Hide Timeline' : 'Show Timeline'}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="page-content">
        {/* Globe Viewer */}
        <div className="globe-container">
          <GlobeViewer 
            containerId="cesium-container"
            onReady={() => console.log('Globe ready')}
            onError={(err) => console.error('Globe error:', err)}
          />
          
          {/* Asset Layer */}
          {isInitialized && (
            <Asset3DLayer
              assets={assets}
              showLabels={true}
              showHealth={true}
              selectedAssetId={selectedAssetId}
              onAssetClick={handleAssetClick}
              onAssetHover={handleAssetHover}
            />
          )}

          {/* Tileset Loader */}
          {isInitialized && tilesets.length > 0 && (
            <TilesetLoader tilesets={tilesets} />
          )}

          {/* Floating Controls */}
          {showControls && (
            <div className="floating-controls">
              <CameraController />
              <SceneController />
              <TerrainManager />
            </div>
          )}

          {/* Timeline Controller */}
          {showTimeline && (
            <div className="floating-timeline">
              <TimelineController 
                events={timelineEvents}
                onEventClick={(event) => console.log('Event clicked:', event)}
              />
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="sidebar">
          <h3>Assets</h3>
          <div className="asset-list">
            {assets.length === 0 ? (
              <p className="no-data">No assets to display</p>
            ) : (
              assets.map(asset => (
                <div 
                  key={asset.id}
                  className={`asset-item ${selectedAssetId === asset.id ? 'selected' : ''}`}
                  onClick={() => setSelectedAssetId(asset.id)}
                >
                  <span className="asset-name">{asset.name}</span>
                  <span className={`asset-status status-${asset.status}`}>
                    {asset.status || 'unknown'}
                  </span>
                </div>
              ))
            )}
          </div>

          {/* Selected Asset Details */}
          {selectedAssetId && (
            <div className="asset-details">
              <h4>Asset Details</h4>
              {(() => {
                const asset = assets.find(a => a.id === selectedAssetId);
                if (!asset) return null;
                return (
                  <>
                    <p><strong>Name:</strong> {asset.name}</p>
                    <p><strong>Type:</strong> {asset.type}</p>
                    <p><strong>Status:</strong> {asset.status}</p>
                    {asset.health !== undefined && (
                      <p><strong>Health:</strong> {(asset.health * 100).toFixed(1)}%</p>
                    )}
                    <p><strong>Position:</strong></p>
                    <ul className="position-details">
                      <li>Lon: {asset.position.longitude.toFixed(6)}</li>
                      <li>Lat: {asset.position.latitude.toFixed(6)}</li>
                      {asset.position.height && (
                        <li>Alt: {asset.position.height.toFixed(1)}m</li>
                      )}
                    </ul>
                  </>
                );
              })()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Main export with Cesium provider
export function DigitalTwin3DPage(props: DigitalTwin3DPageProps) {
  return (
    <CesiumProvider>
      <DigitalTwin3DPageContent {...props} />
    </CesiumProvider>
  );
}

export default DigitalTwin3DPage;
