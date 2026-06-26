/**
 * Knowledge Repository Page
 * 
 * Structured knowledge organization and documentation.
 * This is metadata only - NO AI, NO embeddings.
 */

import React, { useState, useEffect } from 'react';
import { KnowledgeGraph } from '../components/KnowledgeGraph';
import {
  listDocuments,
  searchDocuments,
  getCategories,
  getKnowledgeGraph,
  getRelatedDocuments
} from '../api/knowledge';
import './KnowledgeRepository.css';

const DOCUMENT_TYPES = [
  'manual',
  'sop',
  'troubleshooting',
  'adr',
  'report',
  'lesson_learned',
  'reference',
  'external'
];

const CATEGORIES = [
  'infrastructure',
  'operations',
  'maintenance',
  'safety',
  'compliance',
  'training',
  'architecture',
  'general'
];

export function KnowledgeRepository() {
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  
  // Documents state
  const [documents, setDocuments] = useState([]);
  const [totalDocuments, setTotalDocuments] = useState(0);
  
  // Categories state
  const [categories, setCategories] = useState([]);
  
  // Graph state
  const [showGraph, setShowGraph] = useState(false);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  
  // Selected document
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [relatedDocs, setRelatedDocs] = useState([]);
  
  // Loading state
  const [loading, setLoading] = useState(false);

  // Load categories and documents on mount
  useEffect(() => {
    loadCategories();
    loadDocuments();
  }, []);

  const loadCategories = async () => {
    try {
      const result = await getCategories();
      setCategories(result.categories || []);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const loadDocuments = async () => {
    setLoading(true);
    try {
      let result;
      
      if (searchQuery) {
        result = await searchDocuments({
          query: searchQuery,
          category: categoryFilter || undefined,
          document_type: typeFilter || undefined
        });
        setDocuments(result.documents || []);
        setTotalDocuments(result.total || 0);
      } else {
        result = await listDocuments({
          category: categoryFilter || undefined,
          document_type: typeFilter || undefined
        });
        setDocuments(result.documents || []);
        setTotalDocuments(result.total || 0);
      }
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    loadDocuments();
  };

  const handleDocumentSelect = async (doc) => {
    setSelectedDoc(doc);
    try {
      const related = await getRelatedDocuments(doc.id);
      setRelatedDocs(related.related_documents || []);
    } catch (error) {
      console.error('Failed to load related documents:', error);
      setRelatedDocs([]);
    }
  };

  const loadGraph = async () => {
    setLoading(true);
    try {
      const graph = await getKnowledgeGraph(100);
      setGraphData({
        nodes: graph.nodes || [],
        edges: graph.edges || []
      });
      setShowGraph(true);
    } catch (error) {
      console.error('Failed to load graph:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTypeIcon = (type) => {
    const icons = {
      manual: '📖',
      sop: '📋',
      troubleshooting: '🔧',
      adr: '📝',
      report: '📊',
      lesson_learned: '💡',
      reference: '📚',
      external: '🔗'
    };
    return icons[type] || '📄';
  };

  const getCategoryColor = (category) => {
    const colors = {
      infrastructure: '#4CAF50',
      operations: '#2196F3',
      maintenance: '#FF9800',
      safety: '#F44336',
      compliance: '#9C27B0',
      training: '#00BCD4',
      architecture: '#795548',
      general: '#607D8B'
    };
    return colors[category] || '#9E9E9E';
  };

  return (
    <div className="knowledge-repository">
      {/* Header */}
      <header className="repo-header">
        <h1>Knowledge Repository</h1>
        <div className="header-actions">
          <button onClick={loadGraph} disabled={loading}>
            {showGraph ? 'Hide Graph' : 'Show Graph'}
          </button>
        </div>
      </header>

      <div className="repo-layout">
        {/* Left Panel - Filters */}
        <aside className="repo-sidebar left-panel">
          <div className="search-section">
            <h3>Search</h3>
            
            <div className="search-field">
              <input
                type="text"
                placeholder="Search documents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button onClick={handleSearch}>🔍</button>
            </div>
            
            <div className="filter-field">
              <label>Category</label>
              <select
                value={categoryFilter}
                onChange={(e) => {
                  setCategoryFilter(e.target.value);
                  setTimeout(loadDocuments, 0);
                }}
              >
                <option value="">All Categories</option>
                {categories.map(cat => (
                  <option key={cat.category} value={cat.category}>
                    {cat.category} ({cat.document_count})
                  </option>
                ))}
              </select>
            </div>
            
            <div className="filter-field">
              <label>Type</label>
              <select
                value={typeFilter}
                onChange={(e) => {
                  setTypeFilter(e.target.value);
                  setTimeout(loadDocuments, 0);
                }}
              >
                <option value="">All Types</option>
                {DOCUMENT_TYPES.map(type => (
                  <option key={type} value={type}>{type.replace('_', ' ')}</option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Statistics */}
          <div className="stats-section">
            <h3>Statistics</h3>
            <div className="stat-item">
              <span className="stat-value">{totalDocuments}</span>
              <span className="stat-label">Total Documents</span>
            </div>
          </div>
        </aside>

        {/* Center Panel - Documents */}
        <main className="repo-main">
          {showGraph ? (
            <KnowledgeGraph
              nodes={graphData.nodes}
              edges={graphData.edges}
              onNodeClick={(node) => {
                const doc = documents.find(d => d.id === node.id);
                if (doc) handleDocumentSelect(doc);
              }}
            />
          ) : (
            <>
              <div className="documents-header">
                <h3>Documents ({totalDocuments})</h3>
              </div>
              
              {loading ? (
                <div className="loading">Loading...</div>
              ) : documents.length === 0 ? (
                <div className="empty-state">
                  <p>No documents found</p>
                </div>
              ) : (
                <div className="documents-grid">
                  {documents.map(doc => (
                    <DocumentCard
                      key={doc.id}
                      document={doc}
                      isSelected={selectedDoc?.id === doc.id}
                      onClick={() => handleDocumentSelect(doc)}
                      getTypeIcon={getTypeIcon}
                      getCategoryColor={getCategoryColor}
                    />
                  ))}
                </div>
              )}
            </>
          )}
        </main>

        {/* Right Panel - Document Details */}
        <aside className="repo-sidebar right-panel">
          {selectedDoc ? (
            <div className="document-details">
              <h3>Document Details</h3>
              
              <div className="detail-badges">
                <span className="type-badge">
                  {getTypeIcon(selectedDoc.document_type)} {selectedDoc.document_type}
                </span>
                <span 
                  className="category-badge"
                  style={{ backgroundColor: getCategoryColor(selectedDoc.category) }}
                >
                  {selectedDoc.category}
                </span>
              </div>
              
              <h4>{selectedDoc.title}</h4>
              
              <div className="detail-meta">
                <p><strong>Author:</strong> {selectedDoc.author}</p>
                {selectedDoc.source && (
                  <p><strong>Source:</strong> {selectedDoc.source}</p>
                )}
              </div>
              
              {selectedDoc.summary && (
                <div className="detail-summary">
                  <h5>Summary</h5>
                  <p>{selectedDoc.summary}</p>
                </div>
              )}
              
              {selectedDoc.tags?.length > 0 && (
                <div className="detail-tags">
                  <h5>Tags</h5>
                  <div className="tags-list">
                    {selectedDoc.tags.map((tag, idx) => (
                      <span key={idx} className="tag">{tag}</span>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedDoc.external_url && (
                <div className="detail-link">
                  <h5>External Link</h5>
                  <a href={selectedDoc.external_url} target="_blank" rel="noopener noreferrer">
                    {selectedDoc.external_url}
                  </a>
                </div>
              )}
              
              {relatedDocs.length > 0 && (
                <div className="related-section">
                  <h5>Related Documents</h5>
                  {relatedDocs.map(doc => (
                    <div key={doc.id} className="related-item">
                      <span className="rel-icon">{getTypeIcon(doc.document_type)}</span>
                      <span className="rel-title">{doc.title}</span>
                      <span className="rel-type">{doc.relationship_type}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="no-selection">
              <p>Select a document to view details</p>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}

// Document Card Component
function DocumentCard({ document, isSelected, onClick, getTypeIcon, getCategoryColor }) {
  return (
    <div
      className={`document-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="card-icon">
        {getTypeIcon(document.document_type)}
      </div>
      
      <div className="card-content">
        <h4>{document.title}</h4>
        
        <div className="card-badges">
          <span 
            className="category-dot"
            style={{ backgroundColor: getCategoryColor(document.category) }}
          />
          <span className="type-label">{document.document_type}</span>
        </div>
        
        {document.summary && (
          <p className="card-summary">{document.summary.substring(0, 100)}...</p>
        )}
        
        {document.tags?.length > 0 && (
          <div className="card-tags">
            {document.tags.slice(0, 3).map((tag, idx) => (
              <span key={idx} className="tag">{tag}</span>
            ))}
            {document.tags.length > 3 && (
              <span className="more-tags">+{document.tags.length - 3}</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default KnowledgeRepository;
