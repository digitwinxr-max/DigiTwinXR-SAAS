/**
 * Session History Component
 * 
 * Displays session history.
 */

import React from 'react';

export function SessionHistory({ sessions, onSelectSession }) {
  if (!sessions || sessions.length === 0) {
    return (
      <div className="session-history empty">
        <p>No sessions yet</p>
        
        <style>{`
          .session-history.empty {
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

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="session-history">
      <h4>Recent Sessions</h4>
      
      <div className="sessions-list">
        {sessions.map((session) => (
          <div 
            key={session.id}
            className="session-item"
            onClick={() => onSelectSession && onSelectSession(session)}
          >
            <div className="session-header">
              <span className="session-name">{session.name}</span>
              <span className="query-count">{session.query_count} queries</span>
            </div>
            
            <div className="session-meta">
              <span className="session-date">{formatDate(session.created_at)}</span>
              {session.asset_id && (
                <span className="asset-id">Asset: {session.asset_id.slice(0, 8)}</span>
              )}
            </div>
            
            {session.context_summary && (
              <p className="session-summary">{session.context_summary}</p>
            )}
          </div>
        ))}
      </div>

      <style>{`
        .session-history {
          background-color: #fff;
          border-radius: 8px;
          padding: 1rem;
        }

        .session-history h4 {
          margin: 0 0 1rem 0;
          font-size: 0.875rem;
          color: #333;
        }

        .sessions-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .session-item {
          padding: 0.75rem;
          background-color: #fafafa;
          border-radius: 4px;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .session-item:hover {
          background-color: #e3f2fd;
        }

        .session-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.25rem;
        }

        .session-name {
          font-weight: bold;
          font-size: 0.875rem;
          color: #333;
        }

        .query-count {
          font-size: 0.75rem;
          color: #666;
        }

        .session-meta {
          display: flex;
          gap: 1rem;
          font-size: 0.75rem;
          color: #666;
          margin-bottom: 0.25rem;
        }

        .session-summary {
          margin: 0;
          font-size: 0.75rem;
          color: #666;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
      `}</style>
    </div>
  );
}

export default SessionHistory;
