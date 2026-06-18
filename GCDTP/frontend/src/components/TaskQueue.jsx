/**
 * Task Queue Component
 * 
 * Displays pending tasks awaiting approval.
 */

import React from 'react';

export function TaskQueue({ tasks, onSelectTask, onApprove, onReject }) {
  const formatTime = (date) => {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleString();
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: { label: 'Pending', color: '#FF9800' },
      approved: { label: 'Approved', color: '#4CAF50' },
      rejected: { label: 'Rejected', color: '#F44336' },
      executed: { label: 'Executed', color: '#2196F3' },
      failed: { label: 'Failed', color: '#9E9E9E' }
    };
    return badges[status] || badges.pending;
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

  if (!tasks || tasks.length === 0) {
    return (
      <div className="task-queue">
        <div className="queue-header">
          <h3>Approval Queue</h3>
          <span className="count">0</span>
        </div>
        <div className="empty-state">
          <p>No pending tasks</p>
        </div>
        
        <style>{`
          .task-queue {
            display: flex;
            flex-direction: column;
            height: 100%;
          }
          .queue-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            border-bottom: 1px solid #e0e0e0;
          }
          .queue-header h3 {
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
    <div className="task-queue">
      <div className="queue-header">
        <h3>Approval Queue</h3>
        <span className="count">{tasks.length}</span>
      </div>

      <div className="tasks">
        {tasks.map((task) => {
          const badge = getStatusBadge(task.status);
          return (
            <div
              key={task.id}
              className="task-item"
              onClick={() => onSelectTask?.(task)}
            >
              <div className="task-header">
                <span className="agent-icon">
                  {getAgentIcon(task.agent_type)}
                </span>
                <span className="agent-name">{task.agent_name}</span>
                <span 
                  className="status-badge"
                  style={{ backgroundColor: badge.color }}
                >
                  {badge.label}
                </span>
              </div>
              
              <div className="task-type">{task.task_type}</div>
              
              <div className="task-meta">
                <span className="requester">
                  Requested by: {task.requested_by}
                </span>
                <span className="time">
                  {formatTime(task.created_at)}
                </span>
              </div>
              
              {task.status === 'pending' && (
                <div className="task-actions">
                  <button 
                    className="approve-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      onApprove?.(task.id);
                    }}
                  >
                    ✓ Approve
                  </button>
                  <button 
                    className="reject-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      onReject?.(task.id);
                    }}
                  >
                    ✗ Reject
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <style>{`
        .task-queue {
          display: flex;
          flex-direction: column;
          height: 100%;
        }

        .queue-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border-bottom: 1px solid #e0e0e0;
        }

        .queue-header h3 {
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

        .tasks {
          flex: 1;
          overflow-y: auto;
          padding: 0.5rem;
        }

        .task-item {
          padding: 0.75rem;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          margin-bottom: 0.5rem;
          cursor: pointer;
          transition: all 0.15s;
        }

        .task-item:hover {
          border-color: #2196f3;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .task-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .agent-icon {
          font-size: 1rem;
        }

        .agent-name {
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

        .task-type {
          font-size: 0.875rem;
          color: #666;
          margin-bottom: 0.5rem;
        }

        .task-meta {
          display: flex;
          justify-content: space-between;
          font-size: 0.75rem;
          color: #999;
        }

        .task-actions {
          display: flex;
          gap: 0.5rem;
          margin-top: 0.75rem;
          padding-top: 0.75rem;
          border-top: 1px dashed #e0e0e0;
        }

        .task-actions button {
          flex: 1;
          padding: 0.5rem;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.75rem;
          font-weight: bold;
        }

        .approve-btn {
          background-color: #4caf50;
          color: white;
        }

        .approve-btn:hover {
          background-color: #388e3c;
        }

        .reject-btn {
          background-color: #f44336;
          color: white;
        }

        .reject-btn:hover {
          background-color: #c62828;
        }
      `}</style>
    </div>
  );
}

export default TaskQueue;
