/**
 * Execution History Component
 * 
 * Displays completed task history.
 */

import React from 'react';

export function ExecutionHistory({ history, onSelectTask }) {
  const formatTime = (date) => {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleString();
  };

  const getStatusBadge = (status) => {
    const badges = {
      executed: { label: 'Executed', color: '#2196F3' },
      rejected: { label: 'Rejected', color: '#F44336' },
      failed: { label: 'Failed', color: '#9E9E9E' }
    };
    return badges[status] || badges.executed;
  };

  const getAgentIcon = (type) => {
    const icons = {
      diagnostic_agent: '🔍',
      maintenance_agent: '🔧',
      recovery_agent: '🔄',
      knowledge_agent: '📚',
      timeline_agent: '⏱️'
    };
    return icons[type] || '🤖';
  };

  if (!history || history.length === 0) {
    return (
      <div className="execution-history">
        <div className="empty-state">
          <p>No execution history</p>
        </div>
        
        <style>{`
          .execution-history {
            height: 100%;
            display: flex;
            flex-direction: column;
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

  return (
    <div className="execution-history">
      <div className="history-header">
        <h3>History</h3>
        <span className="count">{history.length}</span>
      </div>

      <div className="history-list">
        {history.map((item) => {
          const badge = getStatusBadge(item.status);
          return (
            <div
              key={item.id}
              className="history-item"
              onClick={() => onSelectTask?.(item)}
            >
              <div className="item-header">
                <span className="agent-icon">
                  {getAgentIcon(item.agent_type)}
                </span>
                <span className="task-type">{item.task_type}</span>
                <span 
                  className="status-badge"
                  style={{ backgroundColor: badge.color }}
                >
                  {badge.label}
                </span>
              </div>
              
              <div className="item-meta">
                <span className="requester">
                  {item.requested_by}
                </span>
                <span className="time">
                  {formatTime(item.created_at)}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <style>{`
        .execution-history {
          height: 100%;
          display: flex;
          flex-direction: column;
        }

        .history-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border-bottom: 1px solid #e0e0e0;
        }

        .history-header h3 {
          margin: 0;
          font-size: 1rem;
        }

        .count {
          font-size: 0.75rem;
          color: #666;
          background-color: #f5f5f5;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
        }

        .history-list {
          flex: 1;
          overflow-y: auto;
          padding: 0.5rem;
        }

        .history-item {
          padding: 0.75rem;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          margin-bottom: 0.5rem;
          cursor: pointer;
          transition: all 0.15s;
        }

        .history-item:hover {
          border-color: #2196f3;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .item-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .agent-icon {
          font-size: 1rem;
        }

        .task-type {
          flex: 1;
          font-size: 0.875rem;
          font-weight: 600;
          color: #333;
        }

        .status-badge {
          font-size: 0.625rem;
          padding: 0.125rem 0.5rem;
          border-radius: 4px;
          color: white;
          font-weight: bold;
        }

        .item-meta {
          display: flex;
          justify-content: space-between;
          font-size: 0.75rem;
          color: #999;
        }
      `}</style>
    </div>
  );
}

export default ExecutionHistory;
