/**
 * Metadata Explorer Component
 */

import React, { useState } from 'react';
import type { CatalogItem, LayerMetadata, BoundingBox } from './terria_types';

interface MetadataExplorerProps {
  item: CatalogItem | null;
  onClose?: () => void;
}

export function MetadataExplorer({ item, onClose }: MetadataExplorerProps) {
  const [activeTab, setActiveTab] = useState<'info' | 'metadata' | 'style'>('info');

  if (!item) {
    return (
      <div className="metadata-explorer empty">
        <p>No item selected</p>
      </div>
    );
  }

  return (
    <div className="metadata-explorer">
      <div className="explorer-header">
        <h3>{item.name}</h3>
        <button onClick={onClose} className="close-btn">×</button>
      </div>

      <div className="explorer-tabs">
        <button 
          className={`tab ${activeTab === 'info' ? 'active' : ''}`}
          onClick={() => setActiveTab('info')}
        >
          Info
        </button>
        <button 
          className={`tab ${activeTab === 'metadata' ? 'active' : ''}`}
          onClick={() => setActiveTab('metadata')}
        >
          Metadata
        </button>
        <button 
          className={`tab ${activeTab === 'style' ? 'active' : ''}`}
          onClick={() => setActiveTab('style')}
        >
          Style
        </button>
      </div>

      <div className="explorer-content">
        {activeTab === 'info' && <InfoTab item={item} />}
        {activeTab === 'metadata' && <MetadataTab item={item} />}
        {activeTab === 'style' && <StyleTab item={item} />}
      </div>
    </div>
  );
}

function InfoTab({ item }: { item: CatalogItem }) {
  return (
    <div className="info-tab">
      <div className="info-row">
        <span className="label">Name:</span>
        <span className="value">{item.name}</span>
      </div>
      <div className="info-row">
        <span className="label">Type:</span>
        <span className="value">{item.type}</span>
      </div>
      <div className="info-row">
        <span className="label">Description:</span>
        <span className="value">{item.description || 'N/A'}</span>
      </div>
      <div className="info-row">
        <span className="label">URL:</span>
        <span className="value">{item.url || 'N/A'}</span>
      </div>
      <div className="info-row">
        <span className="label">Enabled:</span>
        <span className="value">{item.isEnabled ? 'Yes' : 'No'}</span>
      </div>
    </div>
  );
}

function MetadataTab({ item }: { item: CatalogItem }) {
  return (
    <div className="metadata-tab">
      <div className="info-row">
        <span className="label">Cache Duration:</span>
        <span className="value">{item.cacheDuration || 'Default'}</span>
      </div>
      {item.legendUrl && (
        <div className="info-row">
          <span className="label">Legend:</span>
          <a href={item.legendUrl} target="_blank" rel="noopener noreferrer">
            View Legend
          </a>
        </div>
      )}
      {item.metadataUrl && (
        <div className="info-row">
          <span className="label">Full Metadata:</span>
          <a href={item.metadataUrl} target="_blank" rel="noopener noreferrer">
            View Metadata
          </a>
        </div>
      )}
    </div>
  );
}

function StyleTab({ item }: { item: CatalogItem }) {
  return (
    <div className="style-tab">
      <p>Style customization coming soon</p>
    </div>
  );
}

// Metadata display component
interface MetadataDisplayProps {
  metadata: LayerMetadata;
}

export function MetadataDisplay({ metadata }: MetadataDisplayProps) {
  return (
    <div className="metadata-display">
      <h4>{metadata.name}</h4>
      {metadata.description && <p>{metadata.description}</p>}
      
      {metadata.keywords && metadata.keywords.length > 0 && (
        <div className="metadata-section">
          <h5>Keywords</h5>
          <div className="keyword-tags">
            {metadata.keywords.map((kw, i) => (
              <span key={i} className="keyword-tag">{kw}</span>
            ))}
          </div>
        </div>
      )}
      
      {metadata.CRS && metadata.CRS.length > 0 && (
        <div className="metadata-section">
          <h5>Coordinate Systems</h5>
          <ul className="crs-list">
            {metadata.CRS.map((crs, i) => (
              <li key={i}>{crs}</li>
            ))}
          </ul>
        </div>
      )}
      
      {metadata.boundingBox && (
        <div className="metadata-section">
          <h5>Bounding Box</h5>
          <div className="bbox-grid">
            <div>West: {metadata.boundingBox.west}</div>
            <div>South: {metadata.boundingBox.south}</div>
            <div>East: {metadata.boundingBox.east}</div>
            <div>North: {metadata.boundingBox.north}</div>
          </div>
        </div>
      )}
      
      {metadata.attribution && (
        <div className="metadata-section">
          <h5>Attribution</h5>
          <p>{metadata.attribution}</p>
        </div>
      )}
    </div>
  );
}
