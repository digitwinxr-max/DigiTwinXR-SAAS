/**
 * Confidence Badge Component
 * 
 * Displays confidence score with visual indicator.
 */

import React from 'react';

export function ConfidenceBadge({ confidence }) {
  const getConfidenceLevel = (score) => {
    if (score >= 0.8) return { label: 'High Confidence', color: '#4CAF50' };
    if (score >= 0.6) return { label: 'Medium Confidence', color: '#FF9800' };
    if (score >= 0.4) return { label: 'Low Confidence', color: '#F44336' };
    return { label: 'Very Low', color: '#9E9E9E' };
  };

  const level = getConfidenceLevel(confidence);
  const percentage = Math.round(confidence * 100);

  return (
    <div className="confidence-badge" title={`Confidence: ${percentage}%`}>
      <div className="badge-bar">
        <div 
          className="badge-fill"
          style={{ 
            width: `${percentage}%`,
            backgroundColor: level.color
          }}
        />
      </div>
      <span className="badge-label" style={{ color: level.color }}>
        {level.label} ({percentage}%)
      </span>
      
      <style>{`
        .confidence-badge {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-top: 0.5rem;
          padding: 0.5rem;
          background-color: #f5f5f5;
          border-radius: 4px;
        }

        .badge-bar {
          flex: 1;
          height: 4px;
          background-color: #e0e0e0;
          border-radius: 2px;
          overflow: hidden;
        }

        .badge-fill {
          height: 100%;
          transition: width 0.3s ease;
        }

        .badge-label {
          font-size: 0.625rem;
          font-weight: bold;
          white-space: nowrap;
        }
      `}</style>
    </div>
  );
}

export default ConfidenceBadge;
