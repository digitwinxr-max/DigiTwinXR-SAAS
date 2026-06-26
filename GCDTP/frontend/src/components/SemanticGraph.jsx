/**
 * Semantic Graph Component
 * 
 * Provides expandable tree visualization for semantic entities.
 * No external graph libraries - pure React tree.
 */

import React, { useState } from 'react';

export function SemanticGraph({ nodes = [], edges = [], onNodeClick }) {
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  
  // Build adjacency list
  const adjacencyList = buildAdjacencyList(nodes, edges);
  
  // Get node by ID
  const nodeMap = new Map(nodes.map(n => [n.id, n]));
  
  // Toggle node expansion
  const toggleExpand = (nodeId) => {
    setExpandedNodes(prev => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  };
  
  // Get type color
  const getTypeColor = (type) => {
    const colors = {
      'asset': '#4caf50',
      'sensor': '#2196f3',
      'measurement': '#ff9800',
      'event': '#f44336',
      'health': '#9c27b0',
      'relationship': '#607d8b',
      'scenario': '#00bcd4',
      'recovery': '#8bc34a',
      'timeline': '#ffc107',
      'work_order': '#ff5722',
      'document': '#795548'
    };
    return colors[type] || '#9e9e9e';
  };
  
  // Render a single node
  const renderNode = (node, depth = 0) => {
    const isExpanded = expandedNodes.has(node.id);
    const children = adjacencyList.get(node.id) || [];
    const hasChildren = children.length > 0;
    
    return (
      <div key={node.id} className="graph-node-container" style={{ marginLeft: depth * 20 }}>
        <div
          className={`graph-node ${hasChildren ? 'expandable' : ''}`}
          onClick={() => {
            if (hasChildren) {
              toggleExpand(node.id);
            }
            onNodeClick?.(node);
          }}
        >
          {hasChildren && (
            <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
              ▶
            </span>
          )}
          {!hasChildren && <span className="leaf-indicator">•</span>}
          
          <span
            className="node-type-indicator"
            style={{ backgroundColor: getTypeColor(node.entity_type) }}
          />
          
          <div className="node-content">
            <span className="node-name">{node.name}</span>
            <span className="node-type">{node.entity_type}</span>
          </div>
          
          {node.tags?.length > 0 && (
            <div className="node-tags">
              {node.tags.slice(0, 3).map((tag, idx) => (
                <span key={idx} className="node-tag">{tag.tag_name}</span>
              ))}
              {node.tags.length > 3 && (
                <span className="more-tags">+{node.tags.length - 3}</span>
              )}
            </div>
          )}
        </div>
        
        {isExpanded && hasChildren && (
          <div className="graph-children">
            {children.map(edge => {
              const childNode = nodeMap.get(edge.target);
              if (!childNode) return null;
              
              return (
                <div key={edge.id} className="graph-edge-container">
                  <div className="edge-label">{edge.relationship_type}</div>
                  {renderNode(childNode, depth + 1)}
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };
  
  // Find root nodes (nodes with no incoming edges)
  const targetIds = new Set(edges.map(e => e.target));
  const rootNodes = nodes.filter(n => !targetIds.has(n.id));
  
  return (
    <div className="semantic-graph">
      <div className="graph-header">
        <h3>Semantic Graph</h3>
        <div className="graph-stats">
          <span>{nodes.length} nodes</span>
          <span>{edges.length} edges</span>
        </div>
      </div>
      
      <div className="graph-legend">
        {['asset', 'sensor', 'event', 'health', 'document'].map(type => (
          <div key={type} className="legend-item">
            <span
              className="legend-color"
              style={{ backgroundColor: getTypeColor(type) }}
            />
            <span className="legend-label">{type}</span>
          </div>
        ))}
      </div>
      
      <div className="graph-content">
        {rootNodes.length === 0 ? (
          <p className="empty-graph">No entities in graph</p>
        ) : (
          rootNodes.map(node => renderNode(node))
        )}
      </div>
      
      <style>{`
        .semantic-graph {
          display: flex;
          flex-direction: column;
          height: 100%;
          background-color: #fff;
          border-radius: 8px;
          overflow: hidden;
        }
        
        .graph-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border-bottom: 1px solid #e0e0e0;
        }
        
        .graph-header h3 {
          margin: 0;
          font-size: 1rem;
          color: #333;
        }
        
        .graph-stats {
          display: flex;
          gap: 1rem;
          font-size: 0.75rem;
          color: #666;
        }
        
        .graph-legend {
          display: flex;
          flex-wrap: wrap;
          gap: 0.75rem;
          padding: 0.75rem 1rem;
          background-color: #fafafa;
          border-bottom: 1px solid #e0e0e0;
        }
        
        .legend-item {
          display: flex;
          align-items: center;
          gap: 0.25rem;
        }
        
        .legend-color {
          width: 12px;
          height: 12px;
          border-radius: 2px;
        }
        
        .legend-label {
          font-size: 0.75rem;
          color: #666;
        }
        
        .graph-content {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
        }
        
        .empty-graph {
          text-align: center;
          color: #666;
          padding: 2rem;
        }
        
        .graph-node-container {
          margin-bottom: 0.25rem;
        }
        
        .graph-node {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 0.75rem;
          border-radius: 4px;
          cursor: pointer;
          transition: background-color 0.15s;
        }
        
        .graph-node:hover {
          background-color: #f5f5f5;
        }
        
        .graph-node.expandable {
          cursor: pointer;
        }
        
        .expand-icon {
          font-size: 0.625rem;
          color: #666;
          transition: transform 0.15s;
        }
        
        .expand-icon.expanded {
          transform: rotate(90deg);
        }
        
        .leaf-indicator {
          color: #999;
          font-size: 1rem;
          width: 12px;
          text-align: center;
        }
        
        .node-type-indicator {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          flex-shrink: 0;
        }
        
        .node-content {
          display: flex;
          flex-direction: column;
          flex: 1;
          min-width: 0;
        }
        
        .node-name {
          font-size: 0.875rem;
          color: #333;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        
        .node-type {
          font-size: 0.75rem;
          color: #666;
          text-transform: uppercase;
        }
        
        .node-tags {
          display: flex;
          gap: 0.25rem;
          flex-wrap: wrap;
        }
        
        .node-tag {
          padding: 0.125rem 0.375rem;
          background-color: #e3f2fd;
          color: #1565c0;
          border-radius: 4px;
          font-size: 0.625rem;
        }
        
        .more-tags {
          font-size: 0.625rem;
          color: #999;
        }
        
        .graph-children {
          margin-left: 1rem;
          border-left: 1px dashed #e0e0e0;
          padding-left: 0.5rem;
        }
        
        .graph-edge-container {
          position: relative;
        }
        
        .edge-label {
          position: absolute;
          left: -1rem;
          top: 0;
          font-size: 0.625rem;
          color: #999;
          background-color: #fff;
          padding: 0 0.25rem;
          transform: translateX(-100%);
        }
      `}</style>
    </div>
  );
}

export default SemanticGraph;

// Helper function to build adjacency list
function buildAdjacencyList(nodes, edges) {
  const adjacencyList = new Map();
  
  // Initialize all nodes
  nodes.forEach(node => {
    adjacencyList.set(node.id, []);
  });
  
  // Add edges
  edges.forEach(edge => {
    if (adjacencyList.has(edge.source)) {
      adjacencyList.get(edge.source).push(edge);
    }
  });
  
  return adjacencyList;
}
