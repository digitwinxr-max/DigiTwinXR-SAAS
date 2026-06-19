/**
 * Insight Graph Component
 * 
 * Visualizes context sources for a query.
 */

import React from 'react';

export function InsightGraph({ graph }) {
  if (!graph || !graph.nodes || graph.nodes.length === 0) {
    return (
      <div className="insight-graph empty">
        <p>No graph data available</p>
        
        <style>{`
          .insight-graph.empty {
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

  const getNodeColor = (type) => {
    const colors = {
      'query': '#1976d2',
      'source': '#4CAF50',
      'semantic': '#2196F3',
      'timeline': '#FF9800',
      'health': '#F44336',
      'prediction': '#9C27B0',
      'root_cause': '#795548'
    };
    return colors[type] || '#9E9E9E';
  };

  return (
    <div className="insight-graph">
      <h4>Context Sources</h4>
      
      <div className="graph-visual">
        {/* Center node */}
        <div className="center-node">
          <div 
            className="node query-node"
            style={{ backgroundColor: getNodeColor('query') }}
          >
            Query
          </div>
        </div>
        
        {/* Source nodes */}
        <div className="sources-grid">
          {graph.nodes.filter(n => n.type !== 'query').map((node) => (
            <div 
              key={node.id}
              className="source-node"
              style={{ borderColor: getNodeColor(node.type) }}
            >
              <span className="node-label">{node.label}</span>
              {node.properties?.weight && (
                <span className="node-weight">
                  {(node.properties.weight * 100).toFixed(0)}%
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="legend">
        <span className="legend-item">
          <span className="dot" style={{ backgroundColor: '#1976d2' }}></span>
          Query
        </span>
        <span className="legend-item">
          <span className="dot" style={{ backgroundColor: '#4CAF50' }}></span>
          Sources
        </span>
      </div>

      <style>{`
        .insight-graph {
          background-color: #fff;
          border-radius: 8px;
          padding: 1rem;
        }

        .insight-graph h4 {
          margin: 0 0 1rem 0;
          font-size: 0.875rem;
          color: #333;
        }

        .graph-visual {
          min-height: 150px;
        }

        .center-node {
          display: flex;
          justify-content: center;
          margin-bottom: 1rem;
        }

        .node {
          padding: 0.5rem 1rem;
          border-radius: 4px;
          color: white;
          font-weight: bold;
          font-size: 0.875rem;
        }

        .query-node {
          background-color: #1976d2;
        }

        .sources-grid {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          justify-content: center;
        }

        .source-node {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 0.5rem 0.75rem;
          border: 2px solid;
          border-radius: 4px;
          background-color: #fafafa;
        }

        .node-label {
          font-size: 0.75rem;
          font-weight: 500;
          text-transform: capitalize;
        }

        .node-weight {
          font-size: 0.625rem;
          color: #666;
        }

        .legend {
          display: flex;
          gap: 1rem;
          justify-content: center;
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 1px solid #e0e0e0;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.75rem;
          color: #666;
        }

        .dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }
      `}</style>
    </div>
  );
}

export default InsightGraph;
