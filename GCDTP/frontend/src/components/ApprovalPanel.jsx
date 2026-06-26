/**
 * Approval Panel Component
 * 
 * Displays task details and approval controls.
 */

import React from 'react';

export function ApprovalPanel({ task, onApprove, onReject, onExecute, onClose }) {
  if (!task) {
    return (
      <div className="approval-panel">
        <div className="empty-state">
          <p>Select a task to view details</p>
        </div>
        
        <style>{`
          .approval-panel {
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

  const formatTime = (date) => {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleString();
  };

  const getStatusInfo = (status) => {
    const info = {
      pending: { label: 'Pending Approval', color: '#FF9800' },
      approved: { label: 'Approved', color: '#4CAF50' },
      rejected: { label: 'Rejected', color: '#F44336' },
      executed: { label: 'Executed', color: '#2196F3' },
      failed: { label: 'Failed', color: '#9E9E9E' }
    };
    return info[status] || info.pending;
  };

  const status = getStatusInfo(task.status);

  return (
    <div className="approval-panel">
      <div className="panel-header">
        <h3>Task Details</h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      <div className="panel-content">
        {/* Status */}
        <div className="status-section">
          <span 
            className="status-badge"
            style={{ backgroundColor: status.color }}
          >
            {status.label}
          </span>
        </div>

        {/* Task Info */}
        <div className="info-section">
          <h4>Task Information</h4>
          <div className="info-row">
            <span className="label">Agent:</span>
            <span className="value">{task.agent_name || task.agent_id}</span>
          </div>
          <div className="info-row">
            <span className="label">Type:</span>
            <span className="value">{task.task_type}</span>
          </div>
          <div className="info-row">
            <span className="label">Requested by:</span>
            <span className="value">{task.requested_by}</span>
          </div>
          {task.approved_by && (
            <div className="info-row">
              <span className="label">Approved by:</span>
              <span className="value">{task.approved_by}</span>
            </div>
          )}
          <div className="info-row">
            <span className="label">Created:</span>
            <span className="value">{formatTime(task.created_at)}</span>
          </div>
          {task.executed_at && (
            <div className="info-row">
              <span className="label">Executed:</span>
              <span className="value">{formatTime(task.executed_at)}</span>
            </div>
          )}
        </div>

        {/* Context */}
        {task.context_data && Object.keys(task.context_data).length > 0 && (
          <div className="context-section">
            <h4>Context</h4>
            <pre className="context-data">
              {JSON.stringify(task.context_data, null, 2)}
            </pre>
          </div>
        )}

        {/* Result */}
        {task.result_data && Object.keys(task.result_data).length > 0 && (
          <div className="result-section">
            <h4>Result</h4>
            <pre className="result-data">
              {JSON.stringify(task.result_data, null, 2)}
            </pre>
          </div>
        )}

        {/* Rejection Reason */}
        {task.result_data?.rejection_reason && (
          <div className="rejection-section">
            <h4>Rejection Reason</h4>
            <p className="rejection-reason">
              {task.result_data.rejection_reason}
            </p>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="panel-actions">
        {task.status === 'pending' && (
          <>
            <button 
              className="approve-btn"
              onClick={() => onApprove?.(task.id)}
            >
              ✓ Approve
            </button>
            <button 
              className="reject-btn"
              onClick={() => onReject?.(task.id)}
            >
              ✗ Reject
            </button>
          </>
        )}
        {task.status === 'approved' && (
          <button 
            className="execute-btn"
            onClick={() => onExecute?.(task.id)}
          >
            ▶ Execute
          </button>
        )}
      </div>

      <style>{`
        .approval-panel {
          height: 100%;
          display: flex;
          flex-direction: column;
          background-color: #fff;
        }

        .panel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border-bottom: 1px solid #e0e0e0;
        }

        .panel-header h3 {
          margin: 0;
          font-size: 1rem;
        }

        .close-btn {
          width: 28px;
          height: 28px;
          border: none;
          border-radius: 4px;
          background-color: #f5f5f5;
          color: #666;
          font-size: 1.25rem;
          cursor: pointer;
        }

        .close-btn:hover {
          background-color: #e0e0e0;
        }

        .panel-content {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
        }

        .status-section {
          margin-bottom: 1rem;
        }

        .status-badge {
          display: inline-block;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          color: white;
          font-size: 0.875rem;
          font-weight: bold;
        }

        .info-section,
        .context-section,
        .result-section,
        .rejection-section {
          margin-bottom: 1.5rem;
        }

        .info-section h4,
        .context-section h4,
        .result-section h4,
        .rejection-section h4 {
          margin: 0 0 0.75rem 0;
          font-size: 0.875rem;
          color: #666;
          text-transform: uppercase;
        }

        .info-row {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
          font-size: 0.875rem;
        }

        .info-row .label {
          color: #666;
          min-width: 100px;
        }

        .info-row .value {
          color: #333;
          flex: 1;
        }

        .context-data,
        .result-data {
          padding: 0.75rem;
          background-color: #f5f5f5;
          border-radius: 4px;
          font-size: 0.75rem;
          overflow-x: auto;
          margin: 0;
        }

        .rejection-reason {
          padding: 0.75rem;
          background-color: #ffebee;
          border-radius: 4px;
          color: #c62828;
          font-size: 0.875rem;
          margin: 0;
        }

        .panel-actions {
          display: flex;
          gap: 0.5rem;
          padding: 1rem;
          border-top: 1px solid #e0e0e0;
        }

        .panel-actions button {
          flex: 1;
          padding: 0.75rem;
          border: none;
          border-radius: 4px;
          font-size: 0.875rem;
          font-weight: bold;
          cursor: pointer;
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

        .execute-btn {
          background-color: #2196f3;
          color: white;
        }

        .execute-btn:hover {
          background-color: #1976d2;
        }
      `}</style>
    </div>
  );
}

export default ApprovalPanel;
