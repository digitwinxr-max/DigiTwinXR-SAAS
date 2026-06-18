/**
 * Semantic Explorer Page
 * 
 * Provides semantic metadata exploration and graph visualization.
 */

import React, { useState, useEffect } from 'react';
import {
  searchSemantic,
  getContext,
  getGraph,
  listEntities,
  getTagSummary
} from '../api/semantic';
import { SemanticGraph } from '../components/SemanticGraph';
import './SemanticExplorer.css';

// Entity types
const ENTITY_TYPES = [
  'asset',
  'sensor',
  'measurement',
  'event',
  'health',
  'relationship',
  'scenario',
  'recovery',
  'timeline',
  'work_order',
  'document'
];

export function SemanticExplorer() {
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [entityTypeFilter, setEntityTypeFilter] = useState('');
  const [ontologyClassFilter, setOntologyClassFilter] = useState('');
  const [tagFilter, setTagFilter] = useState('');
  
  // Results state
  const [searchResults, setSearchResults] = useState([]);
  const [totalResults, setTotalResults] = useState(0);
  
  // Selected entity
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [context, setContext] = useState(null);
  
  // Graph state
  const [showGraph, setShowGraph] = useState(false);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  
  // Tag summary
  const [tagSummary, setTagSummary] = useState([]);
  
  // Loading state
  const [loading, setLoading] = useState(false);

  // Load tag summary on mount
  useEffect(() => {
    loadTagSummary();
  }, []);

  const loadTagSummary = async () => {
    try {
      const summary = await getTagSummary();
      setTagSummary(summary.tags || []);
    } catch (error) {
      console.error('Failed to load tag summary:', error);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      const params = {};
      if (searchQuery) params.query = searchQuery;
      if (entityTypeFilter) params.entity_type = entityTypeFilter;
      if (ontologyClassFilter) params.ontology_class = ontologyClassFilter;
      if (tagFilter) params.tag_name = tagFilter;
      
      const results = await searchSemantic(params);
      setSearchResults(results.results || []);
      setTotalResults(results.total || 0);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEntitySelect = async (entity) => {
    setSelectedEntity(entity);
    try {
      const ctx = await getContext(entity.entity_type, entity.entity_id);
      setContext(ctx);
    } catch (error) {
      console.error('Failed to load context:', error);
      setContext(null);
    }
  };

  const loadGraph = async () => {
    setLoading(true);
    try {
      const graph = await getGraph(500);
      setGraphData({ nodes: graph.nodes || [], edges: graph.edges || [] });
      setShowGraph(true);
    } catch (error) {
      console.error('Failed to load graph:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="semantic-explorer">
      {/* Header */}
      <header className="explorer-header">
        <h1>Semantic Explorer</h1>
        <div className="header-actions">
          <button onClick={loadGraph} disabled={loading}>
            {showGraph ? 'Hide Graph' : 'Show Graph'}
          </button>
        </div>
      </header>

      <div className="explorer-layout">
        {/* Left Panel - Search */}
        <aside className="explorer-sidebar left-panel">
          <div className="search-section">
            <h3>Search</h3>
            
            {/* Search input */}
            <div className="search-field">
              <input
                type="text"
                placeholder="Search entities..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            
            {/* Entity type filter */}
            <div className="filter-field">
              <label>Entity Type</label>
              <select
                value={entityTypeFilter}
                onChange={(e) => setEntityTypeFilter(e.target.value)}
              >
                <option value="">All Types</option>
                {ENTITY_TYPES.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            
            {/* Ontology class filter */}
            <div className="filter-field">
              <label>Ontology Class</label>
              <input
                type="text"
                placeholder="e.g., transformer"
                value={ontologyClassFilter}
                onChange={(e) => setOntologyClassFilter(e.target.value)}
              />
            </div>
            
            {/* Tag filter */}
            <div className="filter-field">
              <label>Tag</label>
              <input
                type="text"
                placeholder="e.g., power"
                value={tagFilter}
                onChange={(e) => setTagFilter(e.target.value)}
              />
            </div>
            
            <button onClick={handleSearch} className="search-btn" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
          
          {/* Tag summary */}
          <div className="tag-summary-section">
            <h3>Popular Tags</h3>
            <div className="tag-list">
              {tagSummary.slice(0, 10).map(tag => (
                <span
                  key={tag.tag_name}
                  className="tag-badge"
                  onClick={() => {
                    setTagFilter(tag.tag_name);
                    handleSearch();
                  }}
                >
                  {tag.tag_name} ({tag.entity_count})
                </span>
              ))}
            </div>
          </div>
        </aside>

        {/* Center Panel - Results */}
        <main className="explorer-main">
          {showGraph ? (
            <SemanticGraph
              nodes={graphData.nodes}
              edges={graphData.edges}
              onNodeClick={(node) => handleEntitySelect(node)}
            />
          ) : (
            <>
              <div className="results-header">
                <h3>Results ({totalResults})</h3>
              </div>
              
              <div className="results-list">
                {searchResults.length === 0 ? (
                  <p className="empty-message">No results found</p>
                ) : (
                  searchResults.map((result, index) => (
                    <EntityCard
                      key={index}
                      entity={result.entity}
                      onClick={() => handleEntitySelect(result.entity)}
                      isSelected={selectedEntity?.id === result.entity.id}
                    />
                  ))
                )}
              </div>
            </>
          )}
        </main>

        {/* Right Panel - Context */}
        <aside className="explorer-sidebar right-panel">
          <div className="context-section">
            <h3>Context</h3>
            
            {!selectedEntity ? (
              <p className="empty-message">Select an entity to view context</p>
            ) : !context ? (
              <p className="empty-message">Loading context...</p>
            ) : (
              <div className="context-content">
                {/* Entity info */}
                <div className="context-entity">
                  <h4>{context.entity?.name}</h4>
                  <div className="entity-meta">
                    <span className="type-badge">{context.entity?.entity_type}</span>
                    {context.entity?.category && (
                      <span className="category-badge">{context.entity.category}</span>
                    )}
                  </div>
                  {context.entity?.ontology_class && (
                    <p className="ontology-class">
                      <strong>Class:</strong> {context.entity.ontology_class}
                    </p>
                  )}
                  {context.entity?.description && (
                    <p className="description">{context.entity.description}</p>
                  )}
                  {context.entity?.tags?.length > 0 && (
                    <div className="entity-tags">
                      {context.entity.tags.map((tag, idx) => (
                        <span key={idx} className="tag">{tag.tag_name}: {tag.tag_value}</span>
                      ))}
                    </div>
                  )}
                </div>
                
                {/* Related entities */}
                {context.asset && (
                  <div className="context-section-item">
                    <h5>Asset</h5>
                    <p>{context.asset.name}</p>
                  </div>
                )}
                
                {context.sensors?.count > 0 && (
                  <div className="context-section-item">
                    <h5>Sensors ({context.sensors.count})</h5>
                    {context.sensors.entities.slice(0, 5).map((s, idx) => (
                      <p key={idx} className="related-entity">{s.name}</p>
                    ))}
                  </div>
                )}
                
                {context.events?.count > 0 && (
                  <div className="context-section-item">
                    <h5>Events ({context.events.count})</h5>
                    {context.events.entities.slice(0, 5).map((e, idx) => (
                      <p key={idx} className="related-entity">{e.name}</p>
                    ))}
                  </div>
                )}
                
                {context.health?.count > 0 && (
                  <div className="context-section-item">
                    <h5>Health ({context.health.count})</h5>
                    {context.health.entities.slice(0, 5).map((h, idx) => (
                      <p key={idx} className="related-entity">{h.name}</p>
                    ))}
                  </div>
                )}
                
                {context.documents?.count > 0 && (
                  <div className="context-section-item">
                    <h5>Documents ({context.documents.count})</h5>
                    {context.documents.entities.slice(0, 5).map((d, idx) => (
                      <p key={idx} className="related-entity">{d.name}</p>
                    ))}
                  </div>
                )}
                
                {context.timeline_entries?.count > 0 && (
                  <div className="context-section-item">
                    <h5>Timeline ({context.timeline_entries.count})</h5>
                    {context.timeline_entries.entities.slice(0, 5).map((t, idx) => (
                      <p key={idx} className="related-entity">{t.name}</p>
                    ))}
                  </div>
                )}
                
                {context.work_orders?.count > 0 && (
                  <div className="context-section-item">
                    <h5>Work Orders ({context.work_orders.count})</h5>
                    {context.work_orders.entities.slice(0, 5).map((w, idx) => (
                      <p key={idx} className="related-entity">{w.name}</p>
                    ))}
                  </div>
                )}
                
                {context.relationships?.length > 0 && (
                  <div className="context-section-item">
                    <h5>Relationships ({context.relationships.length})</h5>
                    {context.relationships.map((r, idx) => (
                      <p key={idx} className="relationship-type">{r.relationship_type}</p>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}

// Entity Card Component
function EntityCard({ entity, onClick, isSelected }) {
  return (
    <div
      className={`entity-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="card-header">
        <h4>{entity.name}</h4>
        <span className="type-badge">{entity.entity_type}</span>
      </div>
      
      {entity.category && (
        <p className="card-category">{entity.category}</p>
      )}
      
      {entity.ontology_class && (
        <p className="card-ontology">{entity.ontology_class}</p>
      )}
      
      {entity.tags?.length > 0 && (
        <div className="card-tags">
          {entity.tags.slice(0, 5).map((tag, idx) => (
            <span key={idx} className="tag">{tag.tag_name}</span>
          ))}
          {entity.tags.length > 5 && (
            <span className="more-tags">+{entity.tags.length - 5}</span>
          )}
        </div>
      )}
    </div>
  );
}

export default SemanticExplorer;
