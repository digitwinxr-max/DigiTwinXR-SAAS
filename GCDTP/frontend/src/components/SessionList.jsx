/**
 * Session List Component
 * 
 * Displays and manages copilot sessions.
 */

import React, { useState } from 'react';

export function SessionList({ sessions, currentSession, onSelect, onCreate }) {
  const [newSessionName, setNewSessionName] = useState('');
  const [showNewSession, setShowNewSession] = useState(false);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleCreate = () => {
    if (newSessionName.trim()) {
      onCreate(newSessionName.trim());
      setNewSessionName('');
      setShowNewSession(false);
    }
  };

  return (
    <div className="session-list">
      <div className="session-header">
        <h3>Sessions</h3>
        <button
          className="new-session-btn"
          onClick={() => setShowNewSession(!showNewSession)}
        >
          + New
        </button>
      </div>

      {showNewSession && (
        <div className="new-session-form">
          <input
            type="text"
            placeholder="Session name..."
            value={newSessionName}
            onChange={(e) => setNewSessionName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
          />
          <button onClick={handleCreate}>Create</button>
        </div>
      )}

      <div className="sessions">
        {sessions.length === 0 ? (
          <p className="empty-sessions">No sessions yet</p>
        ) : (
          sessions.map((session) => (
            <div
              key={session.id}
              className={`session-item ${currentSession?.id === session.id ? 'active' : ''}`}
              onClick={() => onSelect(session)}
            >
              <div className="session-name">{session.session_name}</div>
              <div className="session-meta">
                <span className="message-count">{session.message_count} messages</span>
                <span className="last-activity">{formatDate(session.last_activity_at)}</span>
              </div>
            </div>
          ))
        )}
      </div>

      <style>{`
        .session-list {
          display: flex;
          flex-direction: column;
          height: 100%;
          padding: 1rem;
        }

        .session-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .session-header h3 {
          margin: 0;
          font-size: 1rem;
          color: #333;
        }

        .new-session-btn {
          padding: 0.25rem 0.75rem;
          border: none;
          border-radius: 4px;
          background-color: #4caf50;
          color: white;
          cursor: pointer;
          font-size: 0.75rem;
        }

        .new-session-btn:hover {
          background-color: #388e3c;
        }

        .new-session-form {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }

        .new-session-form input {
          flex: 1;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.875rem;
        }

        .new-session-form button {
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 4px;
          background-color: #2196f3;
          color: white;
          cursor: pointer;
          font-size: 0.875rem;
        }

        .sessions {
          flex: 1;
          overflow-y: auto;
        }

        .empty-sessions {
          text-align: center;
          color: #666;
          padding: 2rem;
          font-size: 0.875rem;
        }

        .session-item {
          padding: 0.75rem;
          margin-bottom: 0.5rem;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.15s;
        }

        .session-item:hover {
          border-color: #2196f3;
          background-color: #f5f5f5;
        }

        .session-item.active {
          border-color: #2196f3;
          background-color: #e3f2fd;
        }

        .session-name {
          font-weight: 600;
          font-size: 0.875rem;
          color: #333;
          margin-bottom: 0.25rem;
        }

        .session-meta {
          display: flex;
          justify-content: space-between;
          font-size: 0.75rem;
          color: #666;
        }
      `}</style>
    </div>
  );
}

export default SessionList;
