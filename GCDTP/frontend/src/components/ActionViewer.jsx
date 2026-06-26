/**
 * Action Viewer Component
 * 
 * Displays proposed actions with details.
 */

import React from 'react';

export function ActionViewer({ action }) {
  if (!action) {
    return (
      <div className="action-viewer">
        <div className="empty-state">
          <p>Select an action to view details</p>
        </div>
        
        <style>{`
          .action-viewer {
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

  const getTypeIcon = (type) => {
    const icons = {
      analyze: '🔍',
      diagnose: '🩺',
      recommend: '💡',
      suggest_maintenance: '🔧',
      suggest_recovery: '🔄',
      retrieve_knowledge: '📚',
      analyze_timeline: '⏱️'
    };
    return icons[type] || '📋';
  };

  const getTypeLabel = (type) => {
    return type.replace(/_/g, ' ');
  };

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

  const status = getStatusBadge(action.approval_status);

  return (
    <div className="action-viewer">
      <div className="viewer-header">
        <span className="action-icon">{getTypeIcon(action.action_type)}</span>
        <span className="action-type">{getTypeLabel(action.action_type)}</span>
        <span 
          className="status-badge"
          style={{ backgroundColor: status.color }}
        >
          {status.label}
        </span>
      </div>

      <div className="viewer-content">
        <div className="info-section">
          <div className="info-row">
            <span className="label">Action ID:</span>
            <span className="value">{action.id.substring(0, 8)}...</span>
          </div>
          <div className="info-row">
            <span className="label">Task ID:</span>
            <span className="value">{action.task_id.substring(0, 8)}...</span>
          </div>
          <div className="info-row">
            <span className="label">Created:</span>
            <span className="value">{formatTime(action.created_at)}</span>
          </div>
          {action.executed_at && (
            <div className="info-row">
              <span className="label">Executed:</span>
              <span className="value">{formatTime(action.executed_at)}</span>
            </div>
          )}
        </div>

        {action.action_payload && Object.keys(action.action_payload).length > 0 && (
          <div className="payload-section">
            <h4>Action Payload</h4>
            <pre className="payload-data">
              {JSON.stringify(action.action_payload, null, 2)}
            </pre>
          </div>
        )}
      </div>

      <style>{`
        .action-viewer {
          height: 100%;
          display: flex;
          flex-direction: column;
          background-color: #fff;
        }

        .viewer-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 1rem;
          border-bottom: 1px solid #e0e0e0;
        }

        .action-icon {
          font-size: 1.25rem;
        }

        .action-type {
          flex: 1;
          font-size: 0.875rem;
          font-weight: 600;
          color: #333;
          text-transform: capitalize;
        }

        .status-badge {
          font-size: 0.625rem;
          padding: 0.125rem 0.5rem;
          border-radius: 4px;
          color: white;
          font-weight: bold;
        }

        .viewer-content {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
        }

        .info-section {
          margin-bottom: 1rem;
        }

        .info-row {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
          font-size: 0.75rem;
        }

        .info-row .label {
          color: #666;
          min-width: 80px;
        }

        .info-row .value {
          color: #333;
          font-family: monospace;
        }

        .payload-section {
          margin-top: 1rem;
        }

        .payload-section h4 {
          margin: 0 0 0.5rem 0;
          font-size: 0.75rem;
          color: #666;
          text-transform: uppercase;
        }

        .payload-data {
          padding: 0.75rem;
          background-color: #f5f5f5;
          border-radius: 4px;
          font-size: 0.75rem;
          overflow-x: auto;
          margin: 0;
        }
      `}</style>
    </div>
  );
}

export default ActionViewer;
