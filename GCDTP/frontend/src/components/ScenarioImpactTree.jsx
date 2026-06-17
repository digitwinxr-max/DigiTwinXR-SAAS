import React, { useState, useCallback } from 'react';
import { getHealthColor, getDeltaColor, formatDelta } from '../api/scenarios';
import './ScenarioImpactTree.css';


/**
 * Tree node component
 */
function TreeNode({ node, depth = 0, expandedNodes, toggleExpand, isRoot = false }) {
  const hasChildren = node.children && node.children.length > 0;
  const isExpanded = expandedNodes.has(node.asset_id);
  const healthColor = getHealthColor(node.predicted_health);
  const deltaColor = getDeltaColor(node.delta_health);

  const handleToggle = (e) => {
    e.stopPropagation();
    toggleExpand(node.asset_id);
  };

  return (
    <div className="tree-node-wrapper">
      <div className="tree-node" style={{ marginLeft: `${depth * 24}px` }}>
        <span
          className={`expand-toggle ${hasChildren ? 'has-children' : ''}`}
          onClick={hasChildren ? handleToggle : undefined}
        >
          {hasChildren && (isExpanded ? '▼' : '▶')}
          {!hasChildren && <span className="no-children">•</span>}
        </span>

        <span className="node-indicator" style={{ backgroundColor: healthColor }} />

        <span className="node-name">
          {node.asset_name}
          {isRoot && <span className="root-badge">ROOT</span>}
        </span>

        <span className="node-health" style={{ backgroundColor: healthColor }}>
          {node.predicted_health.toFixed(0)}
        </span>

        {node.relationship_type && node.relationship_type !== 'root' && (
          <span className="node-relationship">{node.relationship_type}</span>
        )}

        {node.delta_health !== 0 && (
          <span className="node-delta" style={{ color: deltaColor }}>
            {formatDelta(node.delta_health)}
          </span>
        )}

        {node.propagation_depth > 0 && (
          <span className="node-depth">Depth {node.propagation_depth}</span>
        )}
      </div>

      {hasChildren && isExpanded && (
        <div className="tree-children">
          {node.children.map((child) => (
            <TreeNode
              key={child.asset_id}
              node={child}
              depth={depth + 1}
              expandedNodes={expandedNodes}
              toggleExpand={toggleExpand}
            />
          ))}
        </div>
      )}
    </div>
  );
}


/**
 * ScenarioImpactTree component
 * 
 * Displays the impact tree of a simulation scenario.
 * Shows relationship hierarchy with health predictions.
 */
function ScenarioImpactTree({ tree }) {
  const [expandedNodes, setExpandedNodes] = useState(new Set());

  // Auto-expand first level on mount
  React.useEffect(() => {
    if (tree && tree.children && tree.children.length > 0) {
      setExpandedNodes(new Set([tree.asset_id]));
    }
  }, [tree]);

  const toggleExpand = useCallback((assetId) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      if (next.has(assetId)) {
        next.delete(assetId);
      } else {
        next.add(assetId);
      }
      return next;
    });
  }, []);

  const expandAll = useCallback(() => {
    const allIds = new Set();
    const collectIds = (node) => {
      allIds.add(node.asset_id);
      if (node.children) {
        node.children.forEach(collectIds);
      }
    };
    if (tree) {
      collectIds(tree);
    }
    setExpandedNodes(allIds);
  }, [tree]);

  const collapseAll = useCallback(() => {
    setExpandedNodes(new Set());
  }, []);

  if (!tree) {
    return (
      <div className="impact-tree-empty">
        <p>No impact tree available</p>
      </div>
    );
  }

  return (
    <div className="scenario-impact-tree">
      <div className="tree-controls">
        <button onClick={expandAll} className="tree-btn">
          Expand All
        </button>
        <button onClick={collapseAll} className="tree-btn">
          Collapse All
        </button>
      </div>

      <div className="tree-legend">
        <span className="legend-item">
          <span className="legend-dot" style={{ backgroundColor: '#22c55e' }} />
          Healthy (80-100)
        </span>
        <span className="legend-item">
          <span className="legend-dot" style={{ backgroundColor: '#f97316' }} />
          Degraded (40-79)
        </span>
        <span className="legend-item">
          <span className="legend-dot" style={{ backgroundColor: '#ef4444' }} />
          Critical (0-39)
        </span>
      </div>

      <div className="tree-container">
        <TreeNode
          node={tree}
          depth={0}
          expandedNodes={expandedNodes}
          toggleExpand={toggleExpand}
          isRoot={true}
        />
      </div>
    </div>
  );
}

export default ScenarioImpactTree;