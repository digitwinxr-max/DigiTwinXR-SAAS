/**
 * Knowledge Graph Component
 * 
 * Displays document nodes and reference links.
 * Read-only visualization.
 */

import React, { useState } from 'react';

export function KnowledgeGraph({ nodes = [], edges = [], onNodeClick }) {
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  
  // Get category color
  const getCategoryColor = (category) => {
    const colors = {
      infrastructure: '#4CAF50',
      operations: '#2196F3',
      maintenance: '#FF9800',
      safety: '#F44336',
      compliance: '#9C27B0',
      training: '#00BCD4',
      architecture: '#795548',
      general: '#607D8B'
    };
    return colors[category] || '#9E9E9E';
  };
  
  // Get type icon
  const getTypeIcon = (type) => {
    const icons = {
      manual: '📖',
      sop: '📋',
      troubleshooting: '🔧',
      adr: '📝',
      report: '📊',
      lesson_learned: '💡',
      reference: '📚',
      external: '🔗'
    };
    return icons[type] || '📄';
  };
  
  // Get relationship icon
  const getRelationshipIcon = (type) => {
    const icons = {
      references: '→',
      extends: '↗',
      supersedes: '↑',
      related_to: '↔'
    };
    return icons[type] || '↔';
  };
  
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
  
  // Get connected edges for a node
  const getNodeEdges = (nodeId) => {
    return edges.filter(e => e.source === nodeId || e.target === nodeId);
  };
  
  // Render a node with its connections
  const renderNode = (node, depth = 0) => {
    const isExpanded = expandedNodes.has(node.id);
    const nodeEdges = getNodeEdges(node.id);
    const hasConnections = nodeEdges.length > 0;
    
    return (
      <div key={node.id} className="graph-node-container" style={{ marginLeft: depth * 20 }}>
        <div
          className={`graph-node ${hasConnections ? 'expandable' : ''}`}
          onClick={() => {
            if (hasConnections) {
              toggleExpand(node.id);
            }
            onNodeClick?.(node);
          }}
        >
          {hasConnections && (
            <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
              ▶
            </span>
          )}
          {!hasConnections && <span className="leaf-indicator">•</span>}
          
          <span
            className="node-category-indicator"
            style={{ backgroundColor: getCategoryColor(node.category) }}
          />
          
          <span className="node-type-icon">
            {getTypeIcon(node.document_type)}
          </span>
          
          <div className="node-content">
            <span className="node-title">{node.title}</span>
            <span className="node-type">{node.document_type}</span>
          </div>
          
          {node.tags?.length > 0 && (
            <div className="node-tags">
              {node.tags.slice(0, 3).map((tag, idx) => (
                <span key={idx} className="node-tag">{tag}</span>
              ))}
            </div>
          )}
        </div>
        
        {isExpanded && (
          <div className="graph-children">
            {nodeEdges.map(edge => {
              const connectedId = edge.source === node.id ? edge.target : edge.source;
              const connectedNode = nodes.find(n => n.id === connectedId);
              
              if (!connectedNode) return null;
              
              return (
                <div key={edge.id} className="graph-edge-container">
                  <div className="edge-label">
                    {getRelationshipIcon(edge.relationship_type)} {edge.relationship_type}
                  </div>
                  {renderNode(connectedNode, depth + 1)}
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };
  
  // Group nodes by category
  const nodesByCategory = nodes.reduce((acc, node) => {
    if (!acc[node.category]) {
      acc[node.category] = [];
    }
    acc[node.category].push(node);
    return acc;
  }, {});
  
  return (
    <div className="knowledge-graph">
      <div className="graph-header">
        <h3>Knowledge Graph</h3>
        <div className="graph-stats">
          <span>{nodes.length} documents</span>
          <span>{edges.length} links</span>
        </div>
      </div>
      
      <div className="graph-legend">
        {['infrastructure', 'operations', 'safety', 'architecture'].map(cat => (
          <div key={cat} className="legend-item">
            <span
              className="legend-color"
              style={{ backgroundColor: getCategoryColor(cat) }}
            />
            <span className="legend-label">{cat}</span>
          </div>
        ))}
      </div>
      
      <div className="graph-content">
        {Object.keys(nodesByCategory).length === 0 ? (
          <p className="empty-graph">No documents in graph</p>
        ) : (
          Object.entries(nodesByCategory).map(([category, categoryNodes]) => (
            <div key={category} className="category-group">
              <h4 className="category-header" style={{ borderLeftColor: getCategoryColor(category) }}>
                {category}
              </h4>
              <div className="category-nodes">
                {categoryNodes.map(node => renderNode(node))}
              </div>
            </div>
          ))
        )}
      </div>
      
      <style>{`
        .knowledge-graph {
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
          text-transform: capitalize;
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
        
        .category-group {
          margin-bottom: 1.5rem;
        }
        
        .category-header {
          margin: 0 0 0.75rem 0;
          padding-left: 0.75rem;
          font-size: 0.875rem;
          color: #333;
          border-left: 3px solid;
          text-transform: capitalize;
        }
        
        .category-nodes {
          padding-left: 0.5rem;
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
        
        .node-category-indicator {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          flex-shrink: 0;
        }
        
        .node-type-icon {
          font-size: 1rem;
        }
        
        .node-content {
          display: flex;
          flex-direction: column;
          flex: 1;
          min-width: 0;
        }
        
        .node-title {
          font-size: 0.875rem;
          color: #333;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        
        .node-type {
          font-size: 0.75rem;
          color: #666;
          text-transform: capitalize;
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
          top: 0.5rem;
          font-size: 0.625rem;
          color: #999;
          background-color: #fff;
          padding: 0 0.25rem;
          transform: translateX(-100%);
          white-space: nowrap;
        }
      `}</style>
    </div>
  );
}

export default KnowledgeGraph;
