import React, { useState, useCallback } from 'react';
import { getHealthColor, getRiskColor } from '../api/recovery';
import './RecoveryImpactTree.css';


/**
 * Recovery tree node component
 */
function RecoveryNode({ node, depth = 0, expandedNodes, toggleExpand, isRoot = false }) {
  const hasChildren = node.children && node.children.length > 0;
  const isExpanded = expandedNodes.has(node.asset_id);
  const beforeColor = getHealthColor(node.before_health);
  const afterColor = getHealthColor(node.after_health);
  const riskColor = getRiskColor(node.remaining_risk);

  const handleToggle = (e) => {
    e.stopPropagation();
    toggleExpand(node.asset_id);
  };

  return (
    <div className="recovery-node-wrapper">
      <div className="recovery-node" style={{ marginLeft: `${depth * 24}px` }}>
        <span
          className={`expand-toggle ${hasChildren ? 'has-children' : ''}`}
          onClick={hasChildren ? handleToggle : undefined}
        >
          {hasChildren && (isExpanded ? '▼' : '▶')}
          {!hasChildren && <span className="no-children">•</span>}
        </span>

        <span className="node-indicator" style={{ backgroundColor: afterColor }} />

        <span className="node-name">
          {node.asset_name}
          {isRoot && <span className="root-badge">ROOT</span>}
        </span>

        <span className="health-transition">
          <span className="before" style={{ color: beforeColor }}>
            {node.before_health.toFixed(0)}
          </span>
          <span className="arrow">→</span>
          <span className="after" style={{ color: afterColor }}>
            {node.after_health.toFixed(0)}
          </span>
        </span>

        <span
          className="improvement-badge"
          style={{ color: node.improvement >= 0 ? '#10b981' : '#ef4444' }}
        >
          {node.improvement >= 0 ? '+' : ''}{node.improvement.toFixed(0)}
        </span>

        <span
          className="risk-badge"
          style={{ backgroundColor: riskColor }}
        >
          {node.remaining_risk}
        </span>
      </div>

      {hasChildren && isExpanded && (
        <div className="recovery-children">
          {node.children.map((child) => (
            <RecoveryNode
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
 * RecoveryImpactTree component
 * 
 * Displays the recovery impact tree showing before/after health transitions.
 */
function RecoveryImpactTree({ tree }) {
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
      <div className="recovery-tree-empty">
        <p>No recovery tree available</p>
      </div>
    );
  }

  return (
    <div className="recovery-impact-tree">
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
        <RecoveryNode
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

export default RecoveryImpactTree;