/**
 * Context Sources Component
 * 
 * Displays context sources for a query.
 */

import React from 'react';

export function ContextSources({ context }) {
  if (!context || context.length === 0) {
    return (
      <div className="context-sources empty">
        <p>No context available</p>
        
        <style>{`
          .context-sources.empty {
            padding: 1.5rem;
            background-color: #f5f5f5;
            border-radius: 8px;
            text-align: center;
            color: #666;
          }
        `}</style>
      </div>
    );
  }

  const getSourceColor = (type) => {
    const colors = {
      'semantic': '#2196F3',
      'timeline': '#FF9800',
      'logbook': '#795548',
      'knowledge': '#4CAF50',
      'rag': '#00BCD4',
      'prediction': '#9C27B0',
      'root_cause': '#E91E63',
      'agent': '#673AB7',
      'health': '#F44336',
      'event': '#FF5722'
    };
    return colors[type] || '#9E9E9E';
  };

  const getSourceIcon = (type) => {
    const icons = {
      'semantic': '🔗',
      'timeline': '📅',
      'logbook': '📝',
      'knowledge': '📚',
      'rag': '🔍',
      'prediction': '🔮',
      'root_cause': '🔬',
      'agent': '🤖',
      'health': '💚',
      'event': '⚡'
    };
    return icons[type] || '📊';
  };

  return (
    <div className="context-sources">
      <div className="sources-header">
        <h4>Context Sources</h4>
        <span className="count">{context.length}</span>
      </div>

      <div className="sources-list">
        {context.map((item, idx) => (
          <div 
            key={item.id || idx}
            className="source-item"
            style={{ borderLeftColor: getSourceColor(item.source_type) }}
          >
            <div className="source-header">
              <span className="source-icon">{getSourceIcon(item.source_type)}</span>
              <span className="source-type">{item.source_type}</span>
              <span className="weight">{(item.weight * 100).toFixed(0)}%</span>
            </div>
            
            <p className="source-summary">{item.summary}</p>
            
            {item.relevance_score !== undefined && (
              <div className="relevance-bar">
                <div 
                  className="relevance-fill"
                  style={{ 
                    width: `${item.relevance_score * 100}%`,
                    backgroundColor: getSourceColor(item.source_type)
                  }}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      <style>{`
        .context-sources {
          background-color: #fff;
          border-radius: 8px;
          padding: 1rem;
        }

        .sources-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .sources-header h4 {
          margin: 0;
          font-size: 0.875rem;
        }

        .count {
          background-color: #f5f5f5;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          color: #666;
        }

        .sources-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          max-height: 400px;
          overflow-y: auto;
        }

        .source-item {
          padding: 0.75rem;
          background-color: #fafafa;
          border-radius: 4px;
          border-left: 4px solid;
        }

        .source-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .source-icon {
          font-size: 1rem;
        }

        .source-type {
          flex: 1;
          font-size: 0.75rem;
          font-weight: bold;
          text-transform: uppercase;
          color: #333;
        }

        .weight {
          font-size: 0.75rem;
          color: #666;
        }

        .source-summary {
          margin: 0;
          font-size: 0.875rem;
          color: #333;
          line-height: 1.4;
        }

        .relevance-bar {
          height: 4px;
          background-color: #e0e0e0;
          border-radius: 2px;
          overflow: hidden;
          margin-top: 0.5rem;
        }

        .relevance-fill {
          height: 100%;
        }
      `}</style>
    </div>
  );
}

export default ContextSources;
