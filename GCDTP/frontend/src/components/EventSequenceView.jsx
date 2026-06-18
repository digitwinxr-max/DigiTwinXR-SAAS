/**
 * Event Sequence View Component
 * 
 * Displays event sequence timeline.
 */

import React from 'react';

export function EventSequenceView({ events }) {
  if (!events || events.length === 0) {
    return (
      <div className="event-sequence empty">
        <p>No events in sequence</p>
        
        <style>{`
          .event-sequence.empty {
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

  const getSeverityColor = (severity) => {
    const colors = {
      'critical': '#9C27B0',
      'high': '#F44336',
      'medium': '#FF9800',
      'low': '#4CAF50'
    };
    return colors[severity?.toLowerCase()] || '#9E9E9E';
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <div className="event-sequence">
      <div className="sequence-header">
        <h3>Event Sequence</h3>
        <span className="count">{events.length} events</span>
      </div>

      <div className="timeline">
        {events.map((event, idx) => (
          <div key={event.id || idx} className="timeline-item">
            <div className="timeline-marker">
              <div 
                className="marker-dot"
                style={{ backgroundColor: getSeverityColor(event.severity) }}
              />
              {idx < events.length - 1 && <div className="marker-line" />}
            </div>
            
            <div className="timeline-content">
              <div className="event-header">
                <span className="event-type">{event.event_type}</span>
                <span 
                  className="severity-badge"
                  style={{ backgroundColor: getSeverityColor(event.severity) }}
                >
                  {event.severity}
                </span>
              </div>
              
              <p className="event-description">{event.description}</p>
              
              <div className="event-meta">
                <span className="timestamp">{formatTime(event.timestamp)}</span>
                <span className="asset">Asset: {event.asset_id?.slice(0, 8) || 'Unknown'}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .event-sequence {
          background-color: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .sequence-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border-bottom: 1px solid #e0e0e0;
        }

        .sequence-header h3 {
          margin: 0;
          font-size: 1rem;
        }

        .count {
          background-color: #f5f5f5;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          color: #666;
        }

        .timeline {
          padding: 1rem;
        }

        .timeline-item {
          display: flex;
          gap: 1rem;
        }

        .timeline-marker {
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .marker-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          flex-shrink: 0;
        }

        .marker-line {
          width: 2px;
          flex: 1;
          background-color: #e0e0e0;
          min-height: 30px;
        }

        .timeline-content {
          flex: 1;
          padding-bottom: 1.5rem;
        }

        .event-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .event-type {
          font-weight: bold;
          font-size: 0.875rem;
          color: #333;
        }

        .severity-badge {
          padding: 0.125rem 0.5rem;
          border-radius: 4px;
          color: white;
          font-size: 0.625rem;
          font-weight: bold;
          text-transform: uppercase;
        }

        .event-description {
          margin: 0 0 0.5rem 0;
          font-size: 0.875rem;
          color: #333;
          line-height: 1.4;
        }

        .event-meta {
          display: flex;
          gap: 1rem;
          font-size: 0.75rem;
          color: #666;
        }

        .timestamp {
          font-family: monospace;
        }
      `}</style>
    </div>
  );
}

export default EventSequenceView;
