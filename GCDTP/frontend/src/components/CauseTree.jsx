/**
 * Cause Tree Component
 * 
 * Visualizes causal chain of assets.
 */

import React from 'react';

export function CauseTree({ chains, factors }) {
  if (!chains || chains.length === 0) {
    return (
      <div className="cause-tree empty">
        <p>No causal chain available</p>
        
        <style>{`
          .cause-tree.empty {
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

  const getDepthColor = (depth) => {
    const colors = ['#4CAF50', '#FF9800', '#F44336', '#9C27B0'];
    return colors[depth % colors.length];
  };

  return (
    <div className="cause-tree">
      <h3>Causal Chain</h3>
      
      <div className="tree-container">
        {chains.map((chain, idx) => (
          <div key={chain.id || idx} className="chain-node">
            {idx > 0 && <div className="chain-connector">↓</div>}
            
            <div 
              className="node-card"
              style={{ borderLeftColor: getDepthColor(chain.depth) }}
            >
              <div className="node-header">
                <span className="depth-badge">Depth {chain.depth}</span>
                {chain.relationship_type && (
                  <span className="rel-type">{chain.relationship_type}</span>
                )}
              </div>
              
              <div className="node-body">
                <div className="asset-link">
                  <span className="label">From:</span>
                  <span className="asset-id">{chain.source_asset_id?.slice(0, 8) || 'Unknown'}</span>
                </div>
                <div className="asset-link">
                  <span className="label">To:</span>
                  <span className="asset-id">{chain.target_asset_id?.slice(0, 8) || 'Unknown'}</span>
                </div>
              </div>
              
              {chain.description && (
                <p className="node-description">{chain.description}</p>
              )}
              
              {chain.propagation_time_seconds && (
                <span className="propagation-time">
                  Propagation: {chain.propagation_time_seconds}s
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .cause-tree {
          background-color: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 1rem;
        }

        .cause-tree h3 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
          color: #333;
        }

        .tree-container {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .chain-connector {
          text-align: center;
          font-size: 1.5rem;
          color: #999;
        }

        .node-card {
          background-color: #fafafa;
          border-radius: 8px;
          padding: 1rem;
          border-left: 4px solid;
        }

        .node-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.75rem;
        }

        .depth-badge {
          padding: 0.125rem 0.5rem;
          background-color: #e0e0e0;
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: bold;
        }

        .rel-type {
          font-size: 0.75rem;
          color: #666;
          text-transform: uppercase;
        }

        .node-body {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .asset-link {
          display: flex;
          gap: 0.5rem;
          font-size: 0.875rem;
        }

        .asset-link .label {
          color: #666;
        }

        .asset-link .asset-id {
          font-family: monospace;
          color: #333;
        }

        .node-description {
          margin: 0.75rem 0 0 0;
          font-size: 0.875rem;
          color: #333;
        }

        .propagation-time {
          display: block;
          margin-top: 0.5rem;
          font-size: 0.75rem;
          color: #666;
        }
      `}</style>
    </div>
  );
}

export default CauseTree;
