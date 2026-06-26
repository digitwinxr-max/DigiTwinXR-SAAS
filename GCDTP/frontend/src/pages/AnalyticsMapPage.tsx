/**
 * Analytics Map Page
 */

import React, { useState } from 'react';
import {
  KeplerProvider,
  DatasetProvider,
  HeatmapProvider,
  ClusterProvider,
  FlowMapProvider,
  TrajectoryProvider,
  TemporalProvider,
  AggregationProvider,
  AnalyticsLayerProvider,
  FilterProvider,
  KeplerSyncProvider,
  useKepler,
  useDatasets,
  useTemporal,
  useAnalyticsLayer,
  KeplerViewer,
  KeplerViewerControls,
  KeplerLayerPanel,
  KeplerDatasetPanel,
  KeplerFilterPanel
} from '../kepler';
import type { AnalyticsViewMode } from '../kepler/kepler_types';

interface AnalyticsMapPageProps {
  initialConfig?: any;
}

export function AnalyticsMapPage({ initialConfig }: AnalyticsMapPageProps) {
  return (
    <KeplerProvider initialConfig={initialConfig}>
      <KeplerSyncProvider>
        <DatasetProvider>
          <HeatmapProvider>
            <ClusterProvider>
              <FlowMapProvider>
                <TrajectoryProvider>
                  <TemporalProvider>
                    <AggregationProvider>
                      <AnalyticsLayerProvider>
                        <FilterProvider>
                          <AnalyticsMapContent />
                        </FilterProvider>
                      </AnalyticsLayerProvider>
                    </AggregationProvider>
                  </TemporalProvider>
                </TrajectoryProvider>
              </FlowMapProvider>
            </ClusterProvider>
          </HeatmapProvider>
        </DatasetProvider>
      </KeplerSyncProvider>
    </KeplerProvider>
  );
}

function AnalyticsMapContent() {
  const { datasets, addDataset } = useDatasets();
  const { layers } = useAnalyticsLayer();
  const { 
    timeWindow, 
    isPlaying, 
    currentTime, 
    play, 
    pause,
    setTimeRange 
  } = useTemporal();
  
  const [showPanel, setShowPanel] = useState(true);

  return (
    <div className="analytics-map-page">
      {/* Header */}
      <header className="map-header">
        <h1>GCDTP Analytics Map</h1>
        <div className="header-actions">
          <button onClick={() => setShowPanel(!showPanel)}>
            {showPanel ? 'Hide' : 'Show'} Panel
          </button>
        </div>
      </header>

      {/* Analytics Mode Switcher */}
      <AnalyticsModeSwitcher />

      <div className="map-layout">
        {/* Sidebar */}
        <aside className="map-sidebar">
          {showPanel && (
            <>
              <KeplerDatasetPanel datasets={datasets} />
              <KeplerLayerPanel layers={layers} />
              <KeplerFilterPanel filters={[]} />
            </>
          )}
        </aside>

        {/* Main Content */}
        <main className="map-main">
          <KeplerViewer
            datasets={datasets}
            layers={layers}
          />
          
          <div className="map-overlay">
            <KeplerViewerControls
              onZoomIn={() => {}}
              onZoomOut={() => {}}
              onResetView={() => {}}
              onFullscreen={() => {}}
            />
          </div>
          
          {/* Timeline Controls */}
          {timeWindow && (
            <div className="timeline-bar">
              <button onClick={() => isPlaying ? pause() : play()}>
                {isPlaying ? '⏸' : '▶'}
              </button>
              <span className="current-time">
                {currentTime || 'No time set'}
              </span>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

// Import AnalyticsModeSwitcher
import { AnalyticsModeSwitcher } from '../components/AnalyticsModeSwitcher';
