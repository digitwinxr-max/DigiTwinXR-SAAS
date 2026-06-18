/**
 * TerriaJS Portal Page
 */

import React, { useState } from 'react';
import {
  TerriaProvider,
  CatalogProvider,
  StoryProvider,
  TimelineProvider,
  ShareProvider,
  FederationProvider,
  useTerria,
  useCatalog,
  useStoryMap,
  useTimelineLayer,
  useFederation,
  useViewMode,
  ViewMode,
  LayerCatalog,
  MetadataExplorer,
  TerriaViewer,
  ShareButton
} from '../terria';
import type { CatalogItem, CameraPosition } from '../terria/terria_types';

interface TerriaPortalPageProps {
  initialConfig?: any;
}

export function TerriaPortalPage({ initialConfig }: TerriaPortalPageProps) {
  return (
    <TerriaProvider initialConfig={initialConfig}>
      <FederationProvider>
        <CatalogProvider>
          <StoryProvider>
            <TimelineProvider>
              <ShareProvider>
                <TerriaPortalContent />
              </ShareProvider>
            </TimelineProvider>
          </StoryProvider>
        </CatalogProvider>
      </FederationProvider>
    </TerriaProvider>
  );
}

function TerriaPortalContent() {
  const { catalogItems, setCatalogItems } = useCatalog();
  const { stories, createStory, addChapter, currentStory } = useStoryMap();
  const { 
    timeEnabledLayers, 
    currentTime, 
    isPlaying, 
    setIsPlaying,
    setCurrentTime 
  } = useTimelineLayer();
  const { federatedSources } = useFederation();
  const { mode: viewMode, setMode } = useViewMode();
  
  const [selectedItem, setSelectedItem] = useState<CatalogItem | null>(null);
  const [showCatalog, setShowCatalog] = useState(true);

  // Build layer catalogs from federated sources
  const layerCatalogs = federatedSources.map(source => ({
    id: source.id,
    name: source.name,
    items: source.layers,
    isOpen: true
  }));

  // Add any local layers
  const localCatalog = {
    id: 'local',
    name: 'Local Layers',
    items: catalogItems.filter(i => !federatedSources.some(s => s.layers.some(l => l.id === i.id))),
    isOpen: true
  };
  if (localCatalog.items.length > 0) {
    layerCatalogs.push(localCatalog);
  }

  const handleItemToggle = (item: CatalogItem) => {
    setCatalogItems(
      catalogItems.map(i => 
        i.id === item.id ? { ...i, isEnabled: !i.isEnabled } : i
      )
    );
  };

  const handleItemSelect = (item: CatalogItem) => {
    setSelectedItem(item);
  };

  const handleCreateStory = () => {
    const story = createStory('New Story', 'A new story map');
    addChapter(story.id, {
      title: 'Chapter 1',
      narrative: 'First chapter of the story',
      cameraPosition: { longitude: 0, latitude: 0 },
      layerStates: []
    });
  };

  return (
    <div className="terria-portal">
      {/* Header */}
      <header className="portal-header">
        <h1>GCDTP Terria Portal</h1>
        <div className="header-actions">
          <button onClick={handleCreateStory}>Create Story</button>
          <ShareButton />
        </div>
      </header>

      <div className="portal-layout">
        {/* Sidebar */}
        <aside className="portal-sidebar">
          {/* View Mode Switcher */}
          <ViewModeSwitcher />
          
          {/* Catalog Toggle */}
          <button 
            className="sidebar-toggle"
            onClick={() => setShowCatalog(!showCatalog)}
          >
            {showCatalog ? 'Hide Catalog' : 'Show Catalog'}
          </button>
          
          {/* Layer Catalog */}
          {showCatalog && (
            <LayerCatalog
              catalogs={layerCatalogs}
              onItemToggle={handleItemToggle}
              onItemSelect={handleItemSelect}
            />
          )}
        </aside>

        {/* Main Content */}
        <main className="portal-main">
          {/* Viewer */}
          <TerriaViewer
            viewMode={viewMode}
            layers={catalogItems}
            onLayerClick={handleItemSelect}
          />
          
          {/* Timeline Controls */}
          {timeEnabledLayers.length > 0 && (
            <div className="timeline-bar">
              <button 
                className="play-btn"
                onClick={() => setIsPlaying(!isPlaying)}
              >
                {isPlaying ? '⏸' : '▶'}
              </button>
              <input
                type="datetime-local"
                value={currentTime?.slice(0, 16) || ''}
                onChange={(e) => setCurrentTime(e.target.value ? new Date(e.target.value).toISOString() : null)}
              />
            </div>
          )}
        </main>

        {/* Right Panel */}
        <aside className="portal-right">
          {/* Metadata Explorer */}
          {selectedItem && (
            <MetadataExplorer
              item={selectedItem}
              onClose={() => setSelectedItem(null)}
            />
          )}
          
          {/* Story Navigator */}
          {currentStory && (
            <div className="story-panel">
              <h3>{currentStory.title}</h3>
              <div className="chapter-list">
                {currentStory.chapters.map((chapter, i) => (
                  <div key={chapter.id} className="chapter-item">
                    <span>{i + 1}. {chapter.title}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}

// Import ViewModeSwitcher
import { ViewModeSwitcher } from '../components/ViewModeSwitcher';
