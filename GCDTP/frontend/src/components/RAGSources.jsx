/**
 * RAG Sources Component
 * 
 * Displays retrieved context sources with relevance scores.
 */

import React from 'react';

export function RAGSources({ sources, onSourceClick }) {
  if (!sources || sources.length === 0) {
    return (
      <div className="rag-sources">
        <div className="empty-state">
          <p>No sources retrieved</p>
        </div>
        
        <style>{`
          .rag-sources {
            height: 100%;
            overflow-y: auto;
          }
          .empty-state {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #666;
          }
        `}</style>
      </div>
    );
  }

  // Group by source type
  const byType = sources.reduce((acc, source) => {
    const type = source.source_type || 'unknown';
    if (!acc[type]) acc[type] = [];
    acc[type].push(source);
    return acc;
  }, {});

  const getTypeIcon = (type) => {
    const icons = {
      semantic: '🔗',
      health: '❤️',
      event: '⚠️',
      timeline: '⏱️',
      logbook: '📖',
      knowledge: '📚',
      asset: '🏢',
      sensor: '📡'
    };
    return icons[type] || '📄';
  };

  const getTypeLabel = (type) => {
    const labels = {
      semantic: 'Semantic Layer',
      health: 'Health Engine',
      event: 'Event Engine',
      timeline: 'Timeline Engine',
      logbook: 'Digital Logbook',
      knowledge: 'Knowledge Repo',
      asset: 'Asset Engine',
      sensor: 'Sensor Data'
    };
    return labels[type] || type;
  };

  const getTypeColor = (type) => {
    const colors = {
      semantic: '#9C27B0',
      health: '#E91E63',
      event: '#F44336',
      timeline: '#FF9800',
      logbook: '#2196F3',
      knowledge: '#4CAF50',
      asset: '#795548',
      sensor: '#607D8B'
    };
    return colors[type] || '#9E9E9E';
  };

  const getConfidenceLabel = (score) => {
    if (score >= 0.8) return 'High';
    if (score >= 0.5) return 'Medium';
    return 'Low';
  };

  return (
    <div className="rag-sources">
      <div className="sources-header">
        <h3>Retrieved Sources</h3>
        <span className="count">{sources.length} chunks</span>
      </div>

      <div className="sources-list">
        {Object.entries(byType).map(([type, typeSources]) => (
          <div key={type} className="source-group">
            <div 
              className="group-header"
              style={{ borderLeftColor: getTypeColor(type) }}
            >
              <span className="icon">{getTypeIcon(type)}</span>
              <span className="label">{getTypeLabel(type)}</span>
              <span className="badge">{typeSources.length}</span>
            </div>

            <div className="source-items">
              {typeSources.map((source, idx) => (
                <div
                  key={source.chunk_id || idx}
                  className="source-item"
                  onClick={() => onSourceClick?.(source)}
                >
                  <div className="source-content">
                    <p>{source.content}</p>
                  </div>
                  
                  <div className="source-meta">
                    <div className="relevance">
                      <span className="score" style={{ 
                        color: source.relevance_score >= 0.7 ? '#4CAF50' : 
                               source.relevance_score >= 0.4 ? '#FF9800' : '#9E9E9E'
                      }}>
                        {(source.relevance_score * 100).toFixed(0)}%
                      </span>
                      <span className="label">{getConfidenceLabel(source.relevance_score)}</span>
                    </div>
                    
                    {source.source_id && (
                      <span className="source-id">
                        {source.source_id.substring(0, 12)}...
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .rag-sources {
          height: 100%;
          overflow-y: auto;
        }

        .sources-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background-color: #fff;
          border-bottom: 1px solid #e0e0e0;
        }

        .sources-header h3 {
          margin: 0;
          font-size: 1rem;
        }

        .sources-header .count {
          font-size: 0.75rem;
          color: #666;
          background-color: #f5f5f5;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
        }

        .sources-list {
          padding: 1rem;
        }

        .source-group {
          margin-bottom: 1.5rem;
        }

        .group-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 0.75rem;
          background-color: #fafafa;
          border-left: 3px solid;
          margin-bottom: 0.5rem;
        }

        .group-header .icon {
          font-size: 1rem;
        }

        .group-header .label {
          flex: 1;
          font-size: 0.875rem;
          font-weight: 600;
          color: #333;
        }

        .group-header .badge {
          font-size: 0.75rem;
          color: #666;
          background-color: #e0e0e0;
          padding: 0.125rem 0.5rem;
          border-radius: 10px;
        }

        .source-items {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .source-item {
          padding: 0.75rem;
          background-color: #fff;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.15s;
        }

        .source-item:hover {
          border-color: #2196f3;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .source-content p {
          margin: 0;
          font-size: 0.75rem;
          color: #333;
          line-height: 1.4;
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
        }

        .source-meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 0.5rem;
          padding-top: 0.5rem;
          border-top: 1px dashed #e0e0e0;
        }

        .relevance {
          display: flex;
          align-items: center;
          gap: 0.25rem;
        }

        .relevance .score {
          font-size: 0.875rem;
          font-weight: bold;
        }

        .relevance .label {
          font-size: 0.625rem;
          color: #666;
        }

        .source-id {
          font-size: 0.625rem;
          color: #999;
          font-family: monospace;
        }
      `}</style>
    </div>
  );
}

export default RAGSources;
