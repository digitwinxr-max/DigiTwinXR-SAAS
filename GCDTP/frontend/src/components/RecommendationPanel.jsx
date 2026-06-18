/**
 * Recommendation Panel Component
 * 
 * Displays maintenance recommendations.
 */

import React from 'react';

export function RecommendationPanel({ recommendations }) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="recommendation-panel empty">
        <p>No recommendations available</p>
        
        <style>{`
          .recommendation-panel.empty {
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

  const getPriorityColor = (priority) => {
    const colors = {
      'CRITICAL': '#9C27B0',
      'HIGH': '#F44336',
      'MEDIUM': '#FF9800',
      'LOW': '#4CAF50'
    };
    return colors[priority] || '#9E9E9E';
  };

  return (
    <div className="recommendation-panel">
      <div className="panel-header">
        <h3>Maintenance Recommendations</h3>
        <span className="count">{recommendations.length}</span>
      </div>

      <div className="recommendations-list">
        {recommendations.map((rec, idx) => (
          <div 
            key={idx} 
            className="recommendation-item"
            style={{ borderLeftColor: getPriorityColor(rec.priority) }}
          >
            <div className="rec-header">
              <span 
                className="priority-badge"
                style={{ backgroundColor: getPriorityColor(rec.priority) }}
              >
                {rec.priority}
              </span>
              <span className="asset-name">{rec.asset_name}</span>
            </div>
            
            <p className="rec-text">{rec.recommendation}</p>
            
            {rec.reason && (
              <span className="reason">{rec.reason}</span>
            )}
          </div>
        ))}
      </div>

      <style>{`
        .recommendation-panel {
          background-color: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

        .count {
          background-color: #f5f5f5;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          color: #666;
        }

        .recommendations-list {
          max-height: 400px;
          overflow-y: auto;
        }

        .recommendation-item {
          padding: 1rem;
          border-left: 4px solid;
          border-bottom: 1px solid #f0f0f0;
        }

        .rec-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .priority-badge {
          padding: 0.125rem 0.5rem;
          border-radius: 4px;
          color: white;
          font-size: 0.625rem;
          font-weight: bold;
        }

        .asset-name {
          font-size: 0.875rem;
          font-weight: 600;
          color: #333;
        }

        .rec-text {
          margin: 0;
          font-size: 0.875rem;
          color: #333;
          line-height: 1.4;
        }

        .reason {
          display: block;
          margin-top: 0.5rem;
          font-size: 0.75rem;
          color: #666;
        }
      `}</style>
    </div>
  );
}

export default RecommendationPanel;
