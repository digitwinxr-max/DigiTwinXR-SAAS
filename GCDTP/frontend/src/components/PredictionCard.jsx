/**
 * Prediction Card Component
 * 
 * Displays asset prediction summary.
 */

import React from 'react';

export function PredictionCard({ prediction }) {
  if (!prediction) {
    return (
      <div className="prediction-card empty">
        <p>No prediction available</p>
        
        <style>{`
          .prediction-card.empty {
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

  const getRiskColor = (level) => {
    const colors = {
      'LOW': '#4CAF50',
      'MEDIUM': '#FF9800',
      'HIGH': '#F44336',
      'CRITICAL': '#9C27B0'
    };
    return colors[level] || '#9E9E9E';
  };

  return (
    <div className="prediction-card">
      <div className="card-header">
        <h3>Prediction Summary</h3>
        <span 
          className="risk-badge"
          style={{ backgroundColor: getRiskColor(prediction.risk_level) }}
        >
          {prediction.risk_level}
        </span>
      </div>

      <div className="card-content">
        <div className="metric">
          <span className="label">Failure Probability</span>
          <span className="value">{prediction.failure_probability.toFixed(1)}%</span>
        </div>

        <div className="metric">
          <span className="label">Predicted Health</span>
          <span className="value">{prediction.predicted_health.toFixed(1)}%</span>
        </div>

        <div className="metric">
          <span className="label">Confidence</span>
          <span className="value">
            {prediction.confidence ? (prediction.confidence * 100).toFixed(0) : 'N/A'}%
          </span>
        </div>

        {prediction.recommended_action && (
          <div className="recommendation">
            <span className="label">Recommendation</span>
            <p>{prediction.recommended_action}</p>
          </div>
        )}

        <div className="factors">
          <span className="section-title">Factor Breakdown</span>
          
          <div className="factor">
            <span className="name">Health Degradation</span>
            <div className="bar">
              <div 
                className="fill" 
                style={{ 
                  width: `${prediction.health_degradation_factor}%`,
                  backgroundColor: '#E91E63'
                }}
              />
            </div>
            <span className="value">{prediction.health_degradation_factor.toFixed(1)}</span>
          </div>

          <div className="factor">
            <span className="name">Active Events</span>
            <div className="bar">
              <div 
                className="fill" 
                style={{ 
                  width: `${prediction.active_events_factor}%`,
                  backgroundColor: '#F44336'
                }}
              />
            </div>
            <span className="value">{prediction.active_events_factor.toFixed(1)}</span>
          </div>

          <div className="factor">
            <span className="name">Measurement Anomalies</span>
            <div className="bar">
              <div 
                className="fill" 
                style={{ 
                  width: `${prediction.measurement_anomalies_factor}%`,
                  backgroundColor: '#FF9800'
                }}
              />
            </div>
            <span className="value">{prediction.measurement_anomalies_factor.toFixed(1)}</span>
          </div>

          <div className="factor">
            <span className="name">Maintenance Age</span>
            <div className="bar">
              <div 
                className="fill" 
                style={{ 
                  width: `${prediction.maintenance_age_factor}%`,
                  backgroundColor: '#2196F3'
                }}
              />
            </div>
            <span className="value">{prediction.maintenance_age_factor.toFixed(1)}</span>
          </div>
        </div>
      </div>

      <style>{`
        .prediction-card {
          background-color: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          overflow: hidden;
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background-color: #fafafa;
          border-bottom: 1px solid #e0e0e0;
        }

        .card-header h3 {
          margin: 0;
          font-size: 1rem;
          color: #333;
        }

        .risk-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 4px;
          color: white;
          font-size: 0.75rem;
          font-weight: bold;
        }

        .card-content {
          padding: 1rem;
        }

        .metric {
          display: flex;
          justify-content: space-between;
          padding: 0.75rem 0;
          border-bottom: 1px solid #f0f0f0;
        }

        .metric .label {
          color: #666;
          font-size: 0.875rem;
        }

        .metric .value {
          font-weight: bold;
          font-size: 1.25rem;
          color: #333;
        }

        .recommendation {
          padding: 1rem;
          background-color: #fff3e0;
          border-radius: 4px;
          margin-top: 1rem;
        }

        .recommendation .label {
          display: block;
          font-size: 0.75rem;
          color: #e65100;
          margin-bottom: 0.5rem;
          font-weight: bold;
        }

        .recommendation p {
          margin: 0;
          font-size: 0.875rem;
          color: #333;
        }

        .factors {
          margin-top: 1rem;
        }

        .section-title {
          display: block;
          font-size: 0.75rem;
          color: #666;
          margin-bottom: 0.75rem;
          text-transform: uppercase;
        }

        .factor {
          display: grid;
          grid-template-columns: 140px 1fr 50px;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .factor .name {
          font-size: 0.75rem;
          color: #666;
        }

        .factor .bar {
          height: 8px;
          background-color: #e0e0e0;
          border-radius: 4px;
          overflow: hidden;
        }

        .factor .fill {
          height: 100%;
          transition: width 0.3s ease;
        }

        .factor .value {
          font-size: 0.75rem;
          text-align: right;
          color: #333;
        }
      `}</style>
    </div>
  );
}

export default PredictionCard;
