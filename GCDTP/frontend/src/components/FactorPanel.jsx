/**
 * Factor Panel Component
 * 
 * Displays ranked contributing factors.
 */

import React from 'react';

export function FactorPanel({ factors, rankedFactors }) {
  const displayFactors = rankedFactors || factors || [];
  
  if (displayFactors.length === 0) {
    return (
      <div className="factor-panel empty">
        <p>No factors identified</p>
        
        <style>{`
          .factor-panel.empty {
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

  const getFactorColor = (type) => {
    const colors = {
      'measurement': '#2196F3',
      'event': '#F44336',
      'health': '#FF9800',
      'relationship': '#9C27B0',
      'timeline': '#00BCD4',
      'logbook': '#795548',
      'knowledge': '#4CAF50'
    };
    return colors[type] || '#9E9E9E';
  };

  const formatFactor = (factor) => {
    if (factor.rank !== undefined) {
      return {
        ...factor.factor,
        rank: factor.rank
      };
    }
    return factor;
  };

  return (
    <div className="factor-panel">
      <div className="panel-header">
        <h3>Contributing Factors</h3>
        <span className="count">{displayFactors.length}</span>
      </div>

      <div className="factors-list">
        {displayFactors.map((item, idx) => {
          const factor = formatFactor(item);
          const weight = factor.weight || factor.factor?.weight || 0;
          
          return (
            <div 
              key={factor.id || idx} 
              className="factor-item"
              style={{ borderLeftColor: getFactorColor(factor.factor_type) }}
            >
              <div className="factor-header">
                <span className="rank">#{factor.rank || idx + 1}</span>
                <span 
                  className="type-badge"
                  style={{ backgroundColor: getFactorColor(factor.factor_type) }}
                >
                  {factor.factor_type}
                </span>
              </div>
              
              <p className="factor-description">{factor.description}</p>
              
              <div className="factor-weight">
                <div className="weight-bar">
                  <div 
                    className="weight-fill"
                    style={{ 
                      width: `${weight * 100}%`,
                      backgroundColor: getFactorColor(factor.factor_type)
                    }}
                  />
                </div>
                <span className="weight-value">{(weight * 100).toFixed(0)}%</span>
              </div>
              
              {factor.evidence && (
                <span className="evidence">{factor.evidence}</span>
              )}
            </div>
          );
        })}
      </div>

      <style>{`
        .factor-panel {
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

        .factors-list {
          max-height: 400px;
          overflow-y: auto;
        }

        .factor-item {
          padding: 1rem;
          border-left: 4px solid;
          border-bottom: 1px solid #f0f0f0;
        }

        .factor-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .rank {
          font-weight: bold;
          font-size: 0.875rem;
          color: #333;
        }

        .type-badge {
          padding: 0.125rem 0.5rem;
          border-radius: 4px;
          color: white;
          font-size: 0.625rem;
          font-weight: bold;
          text-transform: uppercase;
        }

        .factor-description {
          margin: 0;
          font-size: 0.875rem;
          color: #333;
          line-height: 1.4;
        }

        .factor-weight {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-top: 0.75rem;
        }

        .weight-bar {
          flex: 1;
          height: 8px;
          background-color: #e0e0e0;
          border-radius: 4px;
          overflow: hidden;
        }

        .weight-fill {
          height: 100%;
          transition: width 0.3s ease;
        }

        .weight-value {
          font-size: 0.75rem;
          font-weight: bold;
          color: #333;
          min-width: 40px;
          text-align: right;
        }

        .evidence {
          display: block;
          margin-top: 0.5rem;
          font-size: 0.75rem;
          color: #666;
          font-style: italic;
        }
      `}</style>
    </div>
  );
}

export default FactorPanel;
