/**
 * Logbook Entry Card Component
 * 
 * Displays a single logbook entry with severity colors and type badges.
 */

import React from 'react';

export function LogbookEntryCard({ entry, isSelected, onClick }) {
  const getSeverityColor = (severity) => {
    const colors = {
      info: '#2196F3',
      warning: '#FF9800',
      critical: '#F44336'
    };
    return colors[severity] || '#9E9E9E';
  };

  const getTypeIcon = (type) => {
    const icons = {
      observation: '👁',
      incident: '🚨',
      maintenance: '🔧',
      inspection: '🔍',
      investigation: '📋',
      annotation: '📝'
    };
    return icons[type] || '📄';
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const truncateContent = (content, maxLength = 150) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength).trim() + '...';
  };

  return (
    <div
      className={`logbook-entry-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="card-header">
        <div className="badges">
          <span className="type-badge">
            {getTypeIcon(entry.entry_type)} {entry.entry_type}
          </span>
          <span 
            className="severity-badge"
            style={{ backgroundColor: getSeverityColor(entry.severity) }}
          >
            {entry.severity}
          </span>
        </div>
        <span className="timestamp">
          {formatTimestamp(entry.timestamp)}
        </span>
      </div>
      
      <h4 className="card-title">{entry.title}</h4>
      
      <p className="card-content">
        {truncateContent(entry.content)}
      </p>
      
      <div className="card-footer">
        <span className="author">
          👤 {entry.author}
        </span>
        
        {entry.entity_type && (
          <span className="entity-ref">
            📍 {entry.entity_type}/{entry.entity_id}
          </span>
        )}
        
        {entry.timeline_snapshot_id && (
          <span className="timeline-ref" title="Timeline Reference">
            ⏱️
          </span>
        )}
      </div>
      
      <style>{`
        .logbook-entry-card {
          padding: 1rem;
          background-color: #fff;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.15s;
        }
        
        .logbook-entry-card:hover {
          border-color: #2196f3;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .logbook-entry-card.selected {
          border-color: #2196f3;
          border-width: 2px;
          background-color: #e3f2fd;
        }
        
        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 0.5rem;
        }
        
        .badges {
          display: flex;
          gap: 0.5rem;
        }
        
        .type-badge {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          padding: 0.125rem 0.5rem;
          background-color: #f5f5f5;
          border-radius: 4px;
          font-size: 0.75rem;
          color: #666;
          text-transform: capitalize;
        }
        
        .severity-badge {
          padding: 0.125rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          color: white;
          text-transform: capitalize;
        }
        
        .timestamp {
          font-size: 0.75rem;
          color: #999;
        }
        
        .card-title {
          margin: 0 0 0.5rem 0;
          font-size: 1rem;
          color: #333;
          font-weight: 600;
        }
        
        .card-content {
          margin: 0 0 0.75rem 0;
          font-size: 0.875rem;
          color: #666;
          line-height: 1.4;
        }
        
        .card-footer {
          display: flex;
          gap: 1rem;
          align-items: center;
          font-size: 0.75rem;
          color: #999;
        }
        
        .author {
          display: flex;
          align-items: center;
          gap: 0.25rem;
        }
        
        .entity-ref {
          font-family: monospace;
        }
        
        .timeline-ref {
          cursor: help;
        }
      `}</style>
    </div>
  );
}

export default LogbookEntryCard;
