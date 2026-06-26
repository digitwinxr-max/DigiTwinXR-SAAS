/**
 * Context Panel Component
 * 
 * Displays entity context from all engines.
 */

import React from 'react';

export function ContextPanel({ entity, context, onSetContext, onClearContext }) {
  if (!entity) {
    return (
      <div className="context-panel">
        <div className="context-header">
          <h3>Context</h3>
        </div>
        
        <div className="no-context">
          <p>No context selected</p>
          <p className="hint">Select an entity to view its context</p>
        </div>
        
        <style>{`
          .context-panel {
            display: flex;
            flex-direction: column;
            height: 100%;
            padding: 1rem;
          }

          .context-header {
            margin-bottom: 1rem;
          }

          .context-header h3 {
            margin: 0;
            font-size: 1rem;
            color: #333;
          }

          .no-context {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            text-align: center;
            color: #666;
          }

          .no-context p {
            margin: 0.25rem 0;
          }

          .no-context .hint {
            font-size: 0.75rem;
            color: #999;
          }
        `}</style>
      </div>
    );
  }

  const formatValue = (value) => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'object') return JSON.stringify(value, null, 2);
    return String(value);
  };

  return (
    <div className="context-panel">
      <div className="context-header">
        <h3>Context: {entity.type}/{entity.id}</h3>
        <button className="clear-btn" onClick={onClearContext}>
          Clear
        </button>
      </div>

      <div className="context-content">
        {/* Asset Context */}
        {context?.asset && (
          <div className="context-section">
            <h4>📊 Asset</h4>
            <div className="context-data">
              {Object.entries(context.asset).map(([key, value]) => (
                <div key={key} className="data-item">
                  <span className="data-key">{key}:</span>
                  <span className="data-value">{formatValue(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Health Context */}
        {context?.health && (
          <div className="context-section">
            <h4>❤️ Health</h4>
            <div className="context-data">
              {Object.entries(context.health).map(([key, value]) => (
                <div key={key} className="data-item">
                  <span className="data-key">{key}:</span>
                  <span className="data-value">{formatValue(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Events Context */}
        {context?.events && context.events.length > 0 && (
          <div className="context-section">
            <h4>⚠️ Events ({context.events.length})</h4>
            <div className="context-list">
              {context.events.slice(0, 5).map((event, idx) => (
                <div key={idx} className="list-item">
                  <span className={`severity ${event.severity?.toLowerCase()}`}>
                    {event.severity}
                  </span>
                  <span className="item-message">{event.message || event.title}</span>
                </div>
              ))}
              {context.events.length > 5 && (
                <p className="more">+{context.events.length - 5} more events</p>
              )}
            </div>
          </div>
        )}

        {/* Sensors Context */}
        {context?.sensors && context.sensors.length > 0 && (
          <div className="context-section">
            <h4>📡 Sensors ({context.sensors.length})</h4>
            <div className="context-list">
              {context.sensors.slice(0, 5).map((sensor, idx) => (
                <div key={idx} className="list-item">
                  <span className="item-name">{sensor.name || sensor.id}</span>
                  {sensor.value && (
                    <span className="item-value">{sensor.value}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Timeline Context */}
        {context?.timeline && context.timeline.length > 0 && (
          <div className="context-section">
            <h4>⏱️ Timeline ({context.timeline.length})</h4>
            <div className="context-list">
              {context.timeline.slice(0, 5).map((snap, idx) => (
                <div key={idx} className="list-item">
                  <span className="item-type">{snap.snapshot_type}</span>
                  <span className="item-time">
                    {new Date(snap.timestamp).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Logbook Context */}
        {context?.logbook && context.logbook.length > 0 && (
          <div className="context-section">
            <h4>📖 Logbook ({context.logbook.length})</h4>
            <div className="context-list">
              {context.logbook.slice(0, 3).map((entry, idx) => (
                <div key={idx} className="list-item">
                  <span className={`severity ${entry.severity}`}>
                    {entry.severity}
                  </span>
                  <span className="item-title">{entry.title}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Knowledge Context */}
        {context?.knowledge && context.knowledge.length > 0 && (
          <div className="context-section">
            <h4>📚 Knowledge ({context.knowledge.length})</h4>
            <div className="context-list">
              {context.knowledge.slice(0, 3).map((doc, idx) => (
                <div key={idx} className="list-item">
                  <span className="item-type">{doc.document_type}</span>
                  <span className="item-title">{doc.title}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Semantic Context */}
        {context?.semantic && (
          <div className="context-section">
            <h4>🔗 Semantic</h4>
            <div className="context-data">
              {Object.entries(context.semantic).map(([key, value]) => (
                <div key={key} className="data-item">
                  <span className="data-key">{key}:</span>
                  <span className="data-value">{formatValue(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <style>{`
        .context-panel {
          display: flex;
          flex-direction: column;
          height: 100%;
          padding: 1rem;
        }

        .context-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .context-header h3 {
          margin: 0;
          font-size: 1rem;
          color: #333;
        }

        .clear-btn {
          padding: 0.25rem 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          background-color: #fff;
          color: #666;
          cursor: pointer;
          font-size: 0.75rem;
        }

        .clear-btn:hover {
          background-color: #f5f5f5;
        }

        .context-content {
          flex: 1;
          overflow-y: auto;
        }

        .context-section {
          margin-bottom: 1.5rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #e0e0e0;
        }

        .context-section:last-child {
          border-bottom: none;
        }

        .context-section h4 {
          margin: 0 0 0.75rem 0;
          font-size: 0.875rem;
          color: #333;
        }

        .context-data {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .data-item {
          display: flex;
          gap: 0.5rem;
          font-size: 0.75rem;
        }

        .data-key {
          color: #666;
          font-weight: 500;
          min-width: 100px;
        }

        .data-value {
          color: #333;
          word-break: break-word;
        }

        .context-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .list-item {
          display: flex;
          gap: 0.5rem;
          align-items: center;
          padding: 0.5rem;
          background-color: #f5f5f5;
          border-radius: 4px;
          font-size: 0.75rem;
        }

        .list-item .severity {
          padding: 0.125rem 0.375rem;
          border-radius: 4px;
          font-size: 0.625rem;
          font-weight: bold;
          text-transform: uppercase;
        }

        .severity.critical,
        .severity.CRITICAL {
          background-color: #ffebee;
          color: #c62828;
        }

        .severity.warning,
        .severity.WARNING {
          background-color: #fff3e0;
          color: #e65100;
        }

        .severity.info,
        .severity.INFO {
          background-color: #e3f2fd;
          color: #1565c0;
        }

        .item-message,
        .item-name,
        .item-title {
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .item-type {
          font-size: 0.625rem;
          padding: 0.125rem 0.375rem;
          background-color: #e0e0e0;
          border-radius: 4px;
          text-transform: capitalize;
        }

        .item-value,
        .item-time {
          font-size: 0.625rem;
          color: #666;
        }

        .more {
          font-size: 0.75rem;
          color: #999;
          text-align: center;
          margin: 0.5rem 0 0 0;
        }
      `}</style>
    </div>
  );
}

export default ContextPanel;
