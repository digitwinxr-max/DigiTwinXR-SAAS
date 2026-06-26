/**
 * Timeline Overlay Component
 * 
 * Overlays historical state on GeoPortal.
 * Timeline Replay is read-only.
 */

import React from 'react';

export function TimelineOverlay({ frame, isActive }) {
  if (!frame || !isActive) {
    return null;
  }
  
  const historicalState = frame.states || {};
  
  return (
    <div className="timeline-overlay">
      <div className="overlay-header">
        <span className="overlay-title">Timeline Replay Active</span>
        <span className="overlay-timestamp">
          {new Date(frame.timestamp).toLocaleString()}
        </span>
      </div>
      
      <div className="overlay-content">
        {/* Health State */}
        {historicalState.health && Object.keys(historicalState.health).length > 0 && (
          <div className="overlay-section">
            <h4>Historical Health</h4>
            <div className="health-list">
              {Object.entries(historicalState.health).slice(0, 5).map(([id, state]) => (
                <div key={id} className="health-item">
                  <span className="health-indicator" style={{
                    backgroundColor: getHealthColor(state.health_status)
                  }} />
                  <span className="health-id">{id}</span>
                  <span className="health-score">{state.health_score}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Events */}
        {frame.events && frame.events.length > 0 && (
          <div className="overlay-section">
            <h4>Events at this Time</h4>
            <div className="event-list">
              {frame.events.slice(0, 5).map((event, idx) => (
                <div key={idx} className={`event-item ${event.severity?.toLowerCase()}`}>
                  <span className={`severity-badge ${event.severity?.toLowerCase()}`}>
                    {event.severity}
                  </span>
                  <span className="event-message">{event.message}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Assets */}
        {historicalState.asset && Object.keys(historicalState.asset).length > 0 && (
          <div className="overlay-section">
            <h4>Asset Status</h4>
            <div className="asset-list">
              {Object.entries(historicalState.asset).slice(0, 5).map(([id, state]) => (
                <div key={id} className="asset-item">
                  <span className="asset-name">{state.name || id}</span>
                  <span className="asset-status">{state.status || 'Unknown'}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      <div className="overlay-footer">
        <span className="readonly-indicator">Read-Only Mode</span>
      </div>
      
      <style>{`
        .timeline-overlay {
          position: fixed;
          top: 1rem;
          right: 1rem;
          width: 300px;
          max-height: 400px;
          background-color: rgba(255, 255, 255, 0.95);
          border: 2px solid #2196f3;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          z-index: 1000;
          overflow: hidden;
        }
        
        .overlay-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem 1rem;
          background-color: #2196f3;
          color: white;
        }
        
        .overlay-title {
          font-weight: bold;
          font-size: 0.875rem;
        }
        
        .overlay-timestamp {
          font-size: 0.75rem;
          opacity: 0.9;
        }
        
        .overlay-content {
          max-height: 300px;
          overflow-y: auto;
          padding: 0.75rem;
        }
        
        .overlay-section {
          margin-bottom: 1rem;
        }
        
        .overlay-section:last-child {
          margin-bottom: 0;
        }
        
        .overlay-section h4 {
          margin: 0 0 0.5rem 0;
          font-size: 0.75rem;
          color: #666;
          text-transform: uppercase;
        }
        
        .health-list,
        .event-list,
        .asset-list {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        
        .health-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.25rem;
          background-color: #f5f5f5;
          border-radius: 4px;
          font-size: 0.75rem;
        }
        
        .health-indicator {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }
        
        .health-id {
          flex: 1;
          font-family: monospace;
        }
        
        .health-score {
          font-weight: bold;
        }
        
        .event-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.25rem;
          background-color: #f5f5f5;
          border-radius: 4px;
          font-size: 0.75rem;
        }
        
        .severity-badge {
          padding: 0.125rem 0.375rem;
          border-radius: 4px;
          font-size: 0.625rem;
          font-weight: bold;
        }
        
        .severity-badge.warning {
          background-color: #fff3e0;
          color: #e65100;
        }
        
        .severity-badge.critical {
          background-color: #ffebee;
          color: #c62828;
        }
        
        .event-message {
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        
        .asset-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.25rem;
          background-color: #f5f5f5;
          border-radius: 4px;
          font-size: 0.75rem;
        }
        
        .asset-name {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        
        .asset-status {
          font-size: 0.625rem;
          padding: 0.125rem 0.375rem;
          background-color: #e0e0e0;
          border-radius: 4px;
        }
        
        .overlay-footer {
          padding: 0.5rem 1rem;
          background-color: #f5f5f5;
          border-top: 1px solid #e0e0e0;
        }
        
        .readonly-indicator {
          font-size: 0.625rem;
          color: #666;
          text-transform: uppercase;
        }
      `}</style>
    </div>
  );
}

// Helper function to get health color
function getHealthColor(status) {
  const colors = {
    'HEALTHY': '#22c55e',
    'DEGRADED': '#f97316',
    'CRITICAL': '#ef4444',
    'UNKNOWN': '#6b7280'
  };
  return colors[status] || colors.UNKNOWN;
}

export default TimelineOverlay;
