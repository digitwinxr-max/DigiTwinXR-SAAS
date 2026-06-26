/**
 * Maintenance Timeline Component
 * 
 * Displays health projections over time.
 */

import React from 'react';

export function MaintenanceTimeline({ timeline }) {
  if (!timeline) {
    return (
      <div className="maintenance-timeline empty">
        <p>No timeline data available</p>
        
        <style>{`
          .maintenance-timeline.empty {
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

  const getTrendColor = (trend) => {
    const colors = {
      'degrading': '#F44336',
      'stable': '#FF9800',
      'improving': '#4CAF50'
    };
    return colors[trend] || '#9E9E9E';
  };

  const getHealthColor = (health) => {
    if (health >= 80) return '#4CAF50';
    if (health >= 60) return '#FF9800';
    if (health >= 40) return '#F44336';
    return '#9C27B0';
  };

  return (
    <div className="maintenance-timeline">
      <div className="timeline-header">
        <h3>Health Timeline</h3>
        <span className="degradation-rate">
          Degradation: {timeline.degradation_rate > 0 ? '+' : ''}{timeline.degradation_rate.toFixed(2)}/day
        </span>
      </div>

      <div className="timeline-content">
        {/* Current State */}
        <div className="timeline-item current">
          <div className="time-marker">
            <span className="time">Now</span>
            <span className="health-value" style={{ color: getHealthColor(timeline.current_health) }}>
              {timeline.current_health.toFixed(1)}%
            </span>
          </div>
          <div className="health-bar">
            <div 
              className="health-fill"
              style={{ 
                width: `${timeline.current_health}%`,
                backgroundColor: getHealthColor(timeline.current_health)
              }}
            />
          </div>
        </div>

        {/* Projections */}
        {timeline.projections && timeline.projections.map((projection, idx) => (
          <div key={idx} className="timeline-item projection">
            <div className="time-marker">
              <span className="time">{projection.timeframe}</span>
              <span className="health-value" style={{ color: getHealthColor(projection.predicted_health) }}>
                {projection.predicted_health.toFixed(1)}%
              </span>
            </div>
            <div className="health-bar">
              <div 
                className="health-fill"
                style={{ 
                  width: `${Math.max(0, projection.predicted_health)}%`,
                  backgroundColor: getHealthColor(projection.predicted_health)
                }}
              />
            </div>
            <span 
              className="trend"
              style={{ color: getTrendColor(projection.risk_trend) }}
            >
              {projection.risk_trend === 'degrading' ? '↓' : 
               projection.risk_trend === 'improving' ? '↑' : '→'} {projection.risk_trend}
            </span>
          </div>
        ))}
      </div>

      <style>{`
        .maintenance-timeline {
          background-color: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .timeline-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border-bottom: 1px solid #e0e0e0;
        }

        .timeline-header h3 {
          margin: 0;
          font-size: 1rem;
        }

        .degradation-rate {
          font-size: 0.75rem;
          color: #666;
        }

        .timeline-content {
          padding: 1rem;
        }

        .timeline-item {
          display: grid;
          grid-template-columns: 120px 1fr;
          gap: 1rem;
          align-items: center;
          padding: 0.75rem 0;
          border-bottom: 1px solid #f0f0f0;
        }

        .timeline-item:last-child {
          border-bottom: none;
        }

        .time-marker {
          display: flex;
          flex-direction: column;
        }

        .time {
          font-size: 0.75rem;
          color: #666;
        }

        .health-value {
          font-size: 1.25rem;
          font-weight: bold;
        }

        .health-bar {
          height: 12px;
          background-color: #e0e0e0;
          border-radius: 6px;
          overflow: hidden;
        }

        .health-fill {
          height: 100%;
          transition: width 0.3s ease;
        }

        .timeline-item.projection .health-bar {
          opacity: 0.7;
        }

        .trend {
          grid-column: 2;
          font-size: 0.75rem;
          font-weight: bold;
          text-transform: uppercase;
        }
      `}</style>
    </div>
  );
}

export default MaintenanceTimeline;
