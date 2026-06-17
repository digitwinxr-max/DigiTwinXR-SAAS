import React, { useState, useEffect, useCallback } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { getGraph, createRelationship, deleteRelationship, RELATIONSHIP_TYPES, RELATIONSHIP_TYPE_INFO } from '../api/relationships';
import { getAssets } from '../api/assets';
import HealthBadge from '../components/Health/HealthBadge';
import './AssetHierarchy.css';


/**
 * HealthBadge component for displaying health status
 */
function HealthBadge({ status, score }) {
  const getColor = () => {
    switch (status) {
      case 'HEALTHY': return '#22c55e';
      case 'DEGRADED': return '#f97316';
      case 'CRITICAL': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <span 
      className="health-badge-inline"
      style={{ backgroundColor: getColor() }}
      title={`${status || 'UNKNOWN'} (${score ?? '-'})`}
    >
      {status || 'N/A'}
      {score !== undefined && score !== null && (
        <span className="health-score">({score})</span>
      )}
    </span>
  );
}


/**
 * TreeNode component for displaying a single node in the hierarchy
 */
function TreeNode({ node, depth = 0, expandedNodes, toggleExpand, onDragStart, onDrop }) {
  const hasChildren = node.children && node.children.length > 0;
  const isExpanded = expandedNodes.has(node.asset_id);
  const hasParents = node.parents && node.parents.length > 0;

  const handleToggle = (e) => {
    e.stopPropagation();
    toggleExpand(node.asset_id);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.currentTarget.classList.add('drop-target');
  };

  const handleDragLeave = (e) => {
    e.currentTarget.classList.remove('drop-target');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('drop-target');
    const draggedAssetId = e.dataTransfer.getData('asset_id');
    if (draggedAssetId && draggedAssetId !== node.asset_id) {
      onDrop(draggedAssetId, node.asset_id);
    }
  };

  return (
    <div className="tree-node-container" style={{ marginLeft: `${depth * 24}px` }}>
      <div 
        className="tree-node"
        draggable
        onDragStart={(e) => {
          e.dataTransfer.setData('asset_id', node.asset_id);
          onDragStart(node.asset_id);
        }}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <span 
          className={`expand-toggle ${hasChildren ? 'has-children' : ''}`}
          onClick={hasChildren ? handleToggle : undefined}
        >
          {hasChildren && (isExpanded ? '▼' : '▶')}
          {!hasChildren && <span className="no-children">•</span>}
        </span>
        
        <span className="asset-name">{node.asset_name}</span>
        <span className="asset-type">({node.asset_type || 'asset'})</span>
        
        {node.health_status && (
          <HealthBadge status={node.health_status} score={node.health_score} />
        )}
        
        <span className="relationship-hint">
          Drop asset here to create "contains" relationship
        </span>
      </div>

      {hasChildren && isExpanded && (
        <div className="tree-children">
          {node.children.map((child) => (
            <TreeNodeWithKey
              key={child.asset_id}
              node={child}
              depth={depth + 1}
              expandedNodes={expandedNodes}
              toggleExpand={toggleExpand}
              onDragStart={onDragStart}
              onDrop={onDrop}
            />
          ))}
        </div>
      )}
    </div>
  );
}


/**
 * Wrapper component with key for proper list rendering
 */
function TreeNodeWithKey(props) {
  return <TreeNode {...props} />;
}


/**
 * AssetHierarchy page component
 */
function AssetHierarchy() {
  const [assets, setAssets] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [draggedAsset, setDraggedAsset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [direction, setDirection] = useState('down');
  const [maxDepth, setMaxDepth] = useState(5);
  const [showAssetSelector, setShowAssetSelector] = useState(false);

  // Fetch assets for the selector
  const fetchAssets = useCallback(async () => {
    try {
      const response = await getAssets({ limit: 1000 });
      setAssets(response.items || []);
    } catch (err) {
      console.error('Failed to fetch assets:', err);
    }
  }, []);

  // Fetch graph data for selected asset
  const fetchGraph = useCallback(async () => {
    if (!selectedAsset) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await getGraph(selectedAsset, direction, maxDepth);
      setGraphData(data);
      
      // Auto-expand root node
      if (data && !expandedNodes.has(data.asset_id)) {
        setExpandedNodes((prev) => new Set([...prev, data.asset_id]));
      }
    } catch (err) {
      setError(err.message);
      setGraphData(null);
    } finally {
      setLoading(false);
    }
  }, [selectedAsset, direction, maxDepth, expandedNodes]);

  useEffect(() => {
    fetchAssets();
  }, [fetchAssets]);

  useEffect(() => {
    if (selectedAsset) {
      fetchGraph();
    }
  }, [selectedAsset, fetchGraph]);

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

  // Handle drag start
  const handleDragStart = useCallback((assetId) => {
    setDraggedAsset(assetId);
  }, []);

  // Handle drop to create relationship
  const handleDrop = useCallback(async (childAssetId, parentAssetId) => {
    try {
      await createRelationship({
        parent_asset_id: parentAssetId,
        child_asset_id: childAssetId,
        relationship_type: RELATIONSHIP_TYPES.CONTAINS,
      });
      
      // Refresh graph
      fetchGraph();
    } catch (err) {
      alert(`Failed to create relationship: ${err.message}`);
    }
  }, [fetchGraph]);

  // Handle delete relationship
  const handleDeleteRelationship = useCallback(async (relationshipId) => {
    if (!confirm('Are you sure you want to delete this relationship?')) {
      return;
    }
    
    try {
      await deleteRelationship(relationshipId);
      fetchGraph();
    } catch (err) {
      alert(`Failed to delete relationship: ${err.message}`);
    }
  }, [fetchGraph]);

  // Select asset from dropdown
  const handleAssetSelect = (assetId) => {
    setSelectedAsset(assetId);
    setShowAssetSelector(false);
  };

  return (
    <div className="asset-hierarchy-page">
      <div className="hierarchy-header">
        <h2>Asset Hierarchy</h2>
        <p className="subtitle">Visualize and manage asset relationships</p>
      </div>

      <div className="hierarchy-controls">
        <div className="asset-selector">
          <label>Select Root Asset:</label>
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

        <div className="graph-options">
          <label>
            Direction:
            <select value={direction} onChange={(e) => setDirection(e.target.value)}>
              <option value="down">Children (Down)</option>
              <option value="up">Parents (Up)</option>
              <option value="both">Both</option>
            </select>
          </label>

          <label>
            Max Depth:
            <input
              type="number"
              min="1"
              max="100"
              value={maxDepth}
              onChange={(e) => setMaxDepth(parseInt(e.target.value) || 5)}
            />
          </label>

          <button onClick={fetchGraph} disabled={!selectedAsset || loading}>
            Refresh
          </button>
        </div>
      </div>

      <div className="legend">
        <h4>Relationship Types</h4>
        <div className="legend-items">
          {Object.entries(RELATIONSHIP_TYPE_INFO).map(([type, info]) => (
            <div key={type} className="legend-item">
              <span 
                className="legend-line"
                style={{ 
                  borderStyle: info.lineStyle === 'arrow' ? 'solid' : info.lineStyle,
                  borderColor: info.color,
                }}
              ></span>
              <span className="legend-label">{info.label}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="hierarchy-content">
        {loading && (
          <div className="loading">Loading hierarchy...</div>
        )}

        {error && (
          <div className="error">Error: {error}</div>
        )}

        {!loading && !error && !graphData && selectedAsset && (
          <div className="empty-state">
            <p>No relationships found for this asset.</p>
            <p>Drag assets onto other assets to create relationships.</p>
          </div>
        )}

        {!selectedAsset && !loading && (
          <div className="empty-state">
            <p>Select an asset above to view its hierarchy.</p>
          </div>
        )}

        {graphData && !loading && (
          <div className="tree-container">
            <div className="tree-root">
              <div className="root-node">
                <span className="root-icon">🏠</span>
                <span className="asset-name">{graphData.asset_name}</span>
                <span className="asset-type">({graphData.asset_type || 'asset'})</span>
                {graphData.health_status && (
                  <HealthBadge status={graphData.health_status} score={graphData.health_score} />
                )}
              </div>

              {graphData.children && graphData.children.length > 0 && (
                <div className="tree-children">
                  {graphData.children.map((child) => (
                    <TreeNodeWithKey
                      key={child.asset_id}
                      node={child}
                      depth={0}
                      expandedNodes={expandedNodes}
                      toggleExpand={toggleExpand}
                      onDragStart={handleDragStart}
                      onDrop={handleDrop}
                    />
                  ))}
                </div>
              )}

              {graphData.parents && graphData.parents.length > 0 && direction === 'both' && (
                <div className="tree-parents">
                  <h4>Parent Assets</h4>
                  {graphData.parents.map((parent) => (
                    <TreeNodeWithKey
                      key={parent.asset_id}
                      node={parent}
                      depth={0}
                      expandedNodes={expandedNodes}
                      toggleExpand={toggleExpand}
                      onDragStart={handleDragStart}
                      onDrop={handleDrop}
                    />
                  ))}
                </div>
              )}

              {direction === 'up' && graphData.parents && (
                <div className="tree-parents">
                  <h4>Parent Assets</h4>
                  {graphData.parents.length === 0 ? (
                    <p className="no-parents">No parent assets</p>
                  ) : (
                    graphData.parents.map((parent) => (
                      <TreeNodeWithKey
                        key={parent.asset_id}
                        node={parent}
                        depth={0}
                        expandedNodes={expandedNodes}
                        toggleExpand={toggleExpand}
                        onDragStart={handleDragStart}
                        onDrop={handleDrop}
                      />
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="hierarchy-footer">
        <div className="instructions">
          <h4>How to use</h4>
          <ul>
            <li>Select an asset to view its hierarchy</li>
            <li>Drag an asset onto another to create a "contains" relationship</li>
            <li>Click ▶/▼ to expand/collapse nodes</li>
            <li>Use direction and depth controls to explore the graph</li>
          </ul>
        </div>

        <div className="stats">
          {graphData && (
            <>
              <span>Depth: {graphData.depth}</span>
              <span>Children: {graphData.children?.length || 0}</span>
              <span>Parents: {graphData.parents?.length || 0}</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default AssetHierarchy;