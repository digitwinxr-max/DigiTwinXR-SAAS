/**
 * Explanation Panel Component
 * 
 * Displays explanation for a query.
 */

import React from 'react';

export function ExplanationPanel({ explanation, confidence }) {
  if (!explanation) {
    return (
      <div className="explanation-panel empty">
        <p>No explanation available</p>
        
        <style>{`
          .explanation-panel.empty {
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

  const getConfidenceColor = (conf) => {
    if (conf >= 0.8) return '#4CAF50';
    if (conf >= 0.6) return '#FF9800';
    return '#F44336';
  };

  return (
    <div className="explanation-panel">
      <div className="explanation-header">
        <h4>Explanation</h4>
        {confidence !== undefined && (
          <span 
            className="confidence-badge"
            style={{ backgroundColor: getConfidenceColor(confidence) }}
          >
            {(confidence * 100).toFixed(0)}% confident
          </span>
        )}
      </div>

      <div className="explanation-content">
        {typeof explanation === 'string' ? (
          <p className="explanation-text">{explanation}</p>
        ) : (
          explanation.split('\n').map((line, idx) => (
            <p key={idx} className="explanation-line">{line}</p>
          ))
        )}
      </div>

      <div className="explanation-footer">
        <span className="advisory-note">
          ⚠️ Advisory only - human review recommended
        </span>
      </div>

      <style>{`
        .explanation-panel {
          background-color: #fff;
          border-radius: 8px;
          padding: 1rem;
        }

        .explanation-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .explanation-header h4 {
          margin: 0;
          font-size: 0.875rem;
          color: #333;
        }

        .confidence-badge {
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          color: white;
          font-size: 0.75rem;
          font-weight: bold;
        }

        .explanation-content {
          background-color: #f5f5f5;
          border-radius: 4px;
          padding: 1rem;
          margin-bottom: 1rem;
        }

        .explanation-text {
          margin: 0;
          font-size: 0.875rem;
          color: #333;
          line-height: 1.6;
        }

        .explanation-line {
          margin: 0 0 0.5rem 0;
          font-size: 0.875rem;
          color: #333;
          line-height: 1.5;
        }

        .explanation-line:last-child {
          margin-bottom: 0;
        }

        .explanation-footer {
          text-align: center;
        }

        .advisory-note {
          font-size: 0.75rem;
          color: #666;
          font-style: italic;
        }
      `}</style>
    </div>
  );
}

export default ExplanationPanel;
