/**
 * RAG Context Panel Component
 * 
 * Displays aggregated context from all engines.
 */

import React from 'react';

export function RAGContextPanel({ context }) {
  if (!context) {
    return (
      <div className="rag-context-panel">
        <div className="empty-state">
          <p>No context loaded</p>
          <p className="hint">Ask a question to load context</p>
        </div>
        
        <style>{`
          .rag-context-panel {
            height: 100%;
            display: flex;
            flex-direction: column;
          }
          .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            text-align: center;
            color: #666;
          }
          .hint {
            font-size: 0.75rem;
            color: #999;
          }
        `}</style>
      </div>
    );
  }

  const contextSummary = context.context_summary || {};
  const sources = context.sources || [];

  return (
    <div className="rag-context-panel">
      <div className="panel-header">
        <h3>Context Summary</h3>
      </div>

      <div className="panel-content">
        {/* Overview */}
        <div className="overview-section">
          <h4>Overview</h4>
          <div className="overview-grid">
            <div className="overview-item">
              <span className="value">{sources.length}</span>
              <span className="label">Total Chunks</span>
            </div>
            <div className="overview-item">
              <span className="value">{context.chunks_used || 0}</span>
              <span className="label">Chunks Used</span>
            </div>
            <div className="overview-item">
              <span className="value">{context.model_name || 'template'}</span>
              <span className="label">Model</span>
            </div>
          </div>
        </div>

        {/* Source Breakdown */}
        <div className="breakdown-section">
          <h4>Sources by Engine</h4>
          <div className="breakdown-list">
            {Object.entries(contextSummary).map(([type, count]) => (
              <div key={type} className="breakdown-item">
                <span className="type-icon">{getTypeIcon(type)}</span>
                <span className="type-name">{getTypeLabel(type)}</span>
                <span className="type-count">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Context Types */}
        <div className="types-section">
          <h4>Available Context</h4>
          <div className="context-types">
            {contextSummary.semantic && (
              <div className="context-type available">
                <span className="icon">🔗</span>
                <span>Semantic Relationships</span>
              </div>
            )}
            {contextSummary.health && (
              <div className="context-type available">
                <span className="icon">❤️</span>
                <span>Health Status</span>
              </div>
            )}
            {contextSummary.event && (
              <div className="context-type available">
                <span className="icon">⚠️</span>
                <span>Events</span>
              </div>
            )}
            {contextSummary.timeline && (
              <div className="context-type available">
                <span className="icon">⏱️</span>
                <span>Timeline</span>
              </div>
            )}
            {contextSummary.logbook && (
              <div className="context-type available">
                <span className="icon">📖</span>
                <span>Logbook</span>
              </div>
            )}
            {contextSummary.knowledge && (
              <div className="context-type available">
                <span className="icon">📚</span>
                <span>Knowledge</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <style>{`
        .rag-context-panel {
          height: 100%;
          display: flex;
          flex-direction: column;
          background-color: #fff;
        }

        .panel-header {
          padding: 1rem;
          border-bottom: 1px solid #e0e0e0;
        }

        .panel-header h3 {
          margin: 0;
          font-size: 1rem;
        }

        .panel-content {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
        }

        .overview-section,
        .breakdown-section,
        .types-section {
          margin-bottom: 1.5rem;
        }

        .overview-section h4,
        .breakdown-section h4,
        .types-section h4 {
          margin: 0 0 0.75rem 0;
          font-size: 0.875rem;
          color: #666;
          text-transform: uppercase;
        }

        .overview-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 0.5rem;
        }

        .overview-item {
          text-align: center;
          padding: 0.75rem;
          background-color: #f5f5f5;
          border-radius: 4px;
        }

        .overview-item .value {
          display: block;
          font-size: 1.25rem;
          font-weight: bold;
          color: #333;
        }

        .overview-item .label {
          font-size: 0.625rem;
          color: #666;
        }

        .breakdown-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .breakdown-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem;
          background-color: #fafafa;
          border-radius: 4px;
        }

        .breakdown-item .type-icon {
          font-size: 1rem;
        }

        .breakdown-item .type-name {
          flex: 1;
          font-size: 0.875rem;
          color: #333;
        }

        .breakdown-item .type-count {
          font-size: 0.875rem;
          font-weight: bold;
          color: #2196f3;
        }

        .context-types {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .context-type {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 0.75rem;
          border-radius: 4px;
          font-size: 0.875rem;
        }

        .context-type.available {
          background-color: #e8f5e9;
          color: #2e7d32;
        }

        .context-type:not(.available) {
          background-color: #f5f5f5;
          color: #999;
        }

        .context-type .icon {
          font-size: 1rem;
        }
      `}</style>
    </div>
  );
}

function getTypeIcon(type) {
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
}

function getTypeLabel(type) {
  const labels = {
    semantic: 'Semantic',
    health: 'Health',
    event: 'Events',
    timeline: 'Timeline',
    logbook: 'Logbook',
    knowledge: 'Knowledge',
    asset: 'Assets',
    sensor: 'Sensors'
  };
  return labels[type] || type;
}

export default RAGContextPanel;
