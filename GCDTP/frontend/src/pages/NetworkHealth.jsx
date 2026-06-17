import React, { useState, useEffect, useCallback } from 'react';
import { getHealthTree, getContributors, getHealthColor, getRelationshipInfo } from '../api/networkHealth';
import { getAssets } from '../api/assets';
import './NetworkHealth.css';


/**
 * Health badge component
 */
function HealthBadge({ score }) {
  const color = getHealthColor(score);
  
  return (
    <span 
      className="health-badge"
      style={{ backgroundColor: color }}
    >
      {score}
    </span>
  );
}


/**
 * Contributor item component
 */
function ContributorItem({ contributor }) {
  const relInfo = getRelationshipInfo(contributor.relationship_type);
  
  return (
    <div className="contributor-item">
      <div className="contributor-header">
        <span className="contributor-name">{contributor.asset_name}</span>
        <HealthBadge score={contributor.health_score} />
      </div>
      <div className="contributor-meta">
        <span className="relationship-type">{relInfo.label}</span>
        <span className="depth-level">Depth {contributor.depth}</span>
        <span className="penalty">Penalty -{contributor.penalty.toFixed(1)}</span>
      </div>
    </div>
  );
}


/**
 * Health tree node component
 */
function HealthTreeNode({ node, depth = 0, expandedNodes, toggleExpand }) {
  const hasChildren = node.children && node.children.length > 0;
  const isExpanded = expandedNodes.has(node.asset_id);
  const color = getHealthColor(node.health_score);

  const handleToggle = (e) => {
    e.stopPropagation();
    toggleExpand(node.asset_id);
  };

  return (
    <div className="tree-node-container" style={{ marginLeft: `${depth * 24}px` }}>
      <div className="tree-node">
        <span 
          className={`expand-toggle ${hasChildren ? 'has-children' : ''}`}
          onClick={hasChildren ? handleToggle : undefined}
        >
          {hasChildren && (isExpanded ? '▼' : '▶')}
          {!hasChildren && <span className="no-children">•</span>}
        </span>
        
        <span className="depth-badge">Depth {node.depth || 0}</span>
        
        <span className="asset-name">{node.asset_name}</span>
        <span className="asset-type">({node.asset_type || 'asset'})</span>
        
        <HealthBadge score={node.health_score} />
        
        {node.dependency_penalty > 0 && (
          <span className="penalty-badge">
            Dep: -{node.dependency_penalty.toFixed(1)}
          </span>
        )}
        
        {node.local_penalty > 0 && (
          <span className="local-penalty-badge">
            Local: -{node.local_penalty}
          </span>
        )}
      </div>

      {hasChildren && isExpanded && (
        <div className="tree-children">
          {node.children.map((child) => (
            <HealthTreeNodeWithKey
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
 * Wrapper with key
 */
function HealthTreeNodeWithKey(props) {
  return <HealthTreeNode {...props} />;
}


/**
 * NetworkHealth page component
 */
function NetworkHealth() {
  const [assets, setAssets] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [healthTree, setHealthTree] = useState(null);
  const [contributors, setContributors] = useState(null);
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('tree'); // 'tree' or 'contributors'
  const [maxDepth, setMaxDepth] = useState(3);

  // Fetch assets
  const fetchAssets = useCallback(async () => {
    try {
      const response = await getAssets({ limit: 1000 });
      setAssets(response.items || []);
    } catch (err) {
      console.error('Failed to fetch assets:', err);
    }
  }, []);

  // Fetch health tree
  const fetchHealthTree = useCallback(async () => {
    if (!selectedAsset) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await getHealthTree(selectedAsset, maxDepth);
      setHealthTree(data);
      
      // Auto-expand root node
      if (data && !expandedNodes.has(data.asset_id)) {
        setExpandedNodes((prev) => new Set([...prev, data.asset_id]));
      }
    } catch (err) {
      setError(err.message);
      setHealthTree(null);
    } finally {
      setLoading(false);
    }
  }, [selectedAsset, maxDepth, expandedNodes]);

  // Fetch contributors
  const fetchContributors = useCallback(async () => {
    if (!selectedAsset) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await getContributors(selectedAsset);
      setContributors(data);
    } catch (err) {
      setError(err.message);
      setContributors(null);
    } finally {
      setLoading(false);
    }
  }, [selectedAsset]);

  useEffect(() => {
    fetchAssets();
  }, [fetchAssets]);

  useEffect(() => {
    if (selectedAsset) {
      if (viewMode === 'tree') {
        fetchHealthTree();
      } else {
        fetchContributors();
      }
    }
  }, [selectedAsset, viewMode, fetchHealthTree, fetchContributors]);

  // Toggle node expansion
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

  return (
    <div className="network-health-page">
      <div className="network-header">
        <h2>Network Health</h2>
        <p className="subtitle">Dependency-aware health with propagation impact</p>
      </div>

      <div className="network-controls">
        <div className="asset-selector">
          <label>Select Asset:</label>
          <select
            value={selectedAsset || ''}
            onChange={(e) => setSelectedAsset(e.target.value || null)}
          >
            <option value="">-- Select an asset --</option>
            {assets.map((asset) => (
              <option key={asset.id} value={asset.id}>
                {asset.name} ({asset.asset_type})
              </option>
            ))}
          </select>
        </div>

        <div className="view-options">
          <label>
            View:
            <select value={viewMode} onChange={(e) => setViewMode(e.target.value)}>
              <option value="tree">Health Tree</option>
              <option value="contributors">Contributors</option>
            </select>
          </label>

          {viewMode === 'tree' && (
            <label>
              Max Depth:
              <input
                type="number"
                min="1"
                max="10"
                value={maxDepth}
                onChange={(e) => setMaxDepth(parseInt(e.target.value) || 3)}
              />
            </label>
          )}

          <button onClick={viewMode === 'tree' ? fetchHealthTree : fetchContributors} disabled={!selectedAsset || loading}>
            Refresh
          </button>
        </div>
      </div>

      <div className="legend">
        <h4>Health Status</h4>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-dot healthy"></span>
            <span>Healthy (80-100)</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot degraded"></span>
            <span>Degraded (40-79)</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot critical"></span>
            <span>Critical (0-39)</span>
          </div>
        </div>

        <h4>Relationship Weights</h4>
        <div className="legend-items">
          <div className="legend-item">
            <span className="weight">0.7</span>
            <span>Feeds</span>
          </div>
          <div className="legend-item">
            <span className="weight">0.6</span>
            <span>Controls</span>
          </div>
          <div className="legend-item">
            <span className="weight">0.5</span>
            <span>Contains</span>
          </div>
          <div className="legend-item">
            <span className="weight">0.3</span>
            <span>Connected</span>
          </div>
          <div className="legend-item">
            <span className="weight">0.0</span>
            <span>Monitors</span>
          </div>
        </div>
      </div>

      <div className="network-content">
        {loading && (
          <div className="loading">Loading network health...</div>
        )}

        {error && (
          <div className="error">Error: {error}</div>
        )}

        {!selectedAsset && !loading && (
          <div className="empty-state">
            <p>Select an asset above to view its network health.</p>
          </div>
        )}

        {viewMode === 'tree' && healthTree && !loading && (
          <div className="tree-container">
            <div className="health-summary">
              <h4>{healthTree.asset_name}</h4>
              <div className="summary-stats">
                <HealthBadge score={healthTree.health_score} />
                <span className="penalty-info">
                  Local: -{healthTree.local_penalty} | Dep: -{healthTree.dependency_penalty.toFixed(1)}
                </span>
              </div>
            </div>

            {healthTree.children && healthTree.children.length > 0 ? (
              <div className="tree-tree">
                {healthTree.children.map((node) => (
                  <HealthTreeNodeWithKey
                    key={node.asset_id}
                    node={node}
                    depth={0}
                    expandedNodes={expandedNodes}
                    toggleExpand={toggleExpand}
                  />
                ))}
              </div>
            ) : (
              <p className="no-children">No child assets in health tree</p>
            )}
          </div>
        )}

        {viewMode === 'contributors' && contributors && !loading && (
          <div className="contributors-container">
            <div className="contributors-summary">
              <h4>{contributors.asset_name}</h4>
              <div className="summary-stats">
                <HealthBadge score={contributors.current_health_score} />
                <span>Total Penalty: -{contributors.total_dependency_penalty.toFixed(1)}</span>
                <span>{contributors.count} Contributors</span>
              </div>
            </div>

            {contributors.contributors && contributors.contributors.length > 0 ? (
              <div className="contributors-list">
                {contributors.contributors.map((contributor, index) => (
                  <ContributorItem key={index} contributor={contributor} />
                ))}
              </div>
            ) : (
              <p className="no-contributors">No dependency contributors</p>
            )}
          </div>
        )}
      </div>

      <div className="network-footer">
        <div className="explanation">
          <h4>How Health Is Calculated</h4>
          <ul>
            <li>Health = 100 - local_events - dependencies</li>
            <li>Local: CRITICAL=-20, WARNING=-10</li>
            <li>Dependency penalty = (100 - source_health) × weight × decay</li>
            <li>Depth decay: 1=100%, 2=50%, 3=25%</li>
          </ul>
        </div>

        <div className="weight-table">
          <h4>Penalty Formula</h4>
          <pre>
{`(100 - source_score) × weight × decay

Example:
  Source health: 20 (CRITICAL)
  Relationship: feeds (weight 0.7)
  Depth: 1 (decay 1.0)
  
  Penalty = (100 - 20) × 0.7 × 1.0 = 56`}
          </pre>
        </div>
      </div>
    </div>
  );
}

export default NetworkHealth;