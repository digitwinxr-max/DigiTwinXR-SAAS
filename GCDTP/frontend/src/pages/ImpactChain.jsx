import React, { useState, useEffect, useCallback } from 'react';
import { getImpactChain, getAssetImpacts, PROPAGATION_TYPE_INFO, getSeverityColor } from '../api/propagation';
import { getAssets } from '../api/assets';
import './ImpactChain.css';


/**
 * Severity badge component
 */
function SeverityBadge({ severity }) {
  const color = getSeverityColor(severity);
  
  return (
    <span 
      className="severity-badge"
      style={{ backgroundColor: color }}
    >
      {severity}
    </span>
  );
}


/**
 * Propagation type badge component
 */
function PropagationTypeBadge({ type }) {
  const info = PROPAGATION_TYPE_INFO[type] || {};
  
  return (
    <span 
      className="propagation-type-badge"
      title={info.description || type}
    >
      {info.label || type}
    </span>
  );
}


/**
 * Chain node component
 */
function ChainNode({ node, depth = 0, expandedNodes, toggleExpand }) {
  const hasChildren = node.children && node.children.length > 0;
  const isExpanded = expandedNodes.has(node.asset_id);

  const handleToggle = (e) => {
    e.stopPropagation();
    toggleExpand(node.asset_id);
  };

  return (
    <div className="chain-node-container" style={{ marginLeft: `${depth * 24}px` }}>
      <div className="chain-node">
        <span 
          className={`expand-toggle ${hasChildren ? 'has-children' : ''}`}
          onClick={hasChildren ? handleToggle : undefined}
        >
          {hasChildren && (isExpanded ? '▼' : '▶')}
          {!hasChildren && <span className="no-children">•</span>}
        </span>
        
        <span className="depth-badge">Depth {node.depth}</span>
        
        <span className="asset-name">{node.asset_name}</span>
        <span className="asset-type">({node.asset_type || 'asset'})</span>
        
        <SeverityBadge severity={node.severity} />
        
        {node.propagation_type && (
          <PropagationTypeBadge type={node.propagation_type} />
        )}
        
        {node.relationship_type && (
          <span className="relationship-label">
            via {node.relationship_type}
          </span>
        )}
      </div>

      {hasChildren && isExpanded && (
        <div className="chain-children">
          {node.children.map((child) => (
            <ChainNodeWithKey
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
function ChainNodeWithKey(props) {
  return <ChainNode {...props} />;
}


/**
 * ImpactChain page component
 */
function ImpactChain() {
  const [assets, setAssets] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [chainData, setChainData] = useState(null);
  const [assetImpacts, setAssetImpacts] = useState([]);
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('chain'); // 'chain' or 'impacts'
  const [maxDepth, setMaxDepth] = useState(10);

  // Fetch assets
  const fetchAssets = useCallback(async () => {
    try {
      const response = await getAssets({ limit: 1000 });
      setAssets(response.items || []);
    } catch (err) {
      console.error('Failed to fetch assets:', err);
    }
  }, []);

  // Fetch chain data
  const fetchChain = useCallback(async () => {
    if (!selectedAsset) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await getImpactChain(
        selectedAsset,
        selectedEvent,
        maxDepth
      );
      setChainData(data);
      
      // Auto-expand first level
      if (data.chain && data.chain.length > 0) {
        setExpandedNodes((prev) => new Set([...prev, data.chain[0].asset_id]));
      }
    } catch (err) {
      setError(err.message);
      setChainData(null);
    } finally {
      setLoading(false);
    }
  }, [selectedAsset, selectedEvent, maxDepth]);

  // Fetch asset impacts
  const fetchImpacts = useCallback(async () => {
    if (!selectedAsset) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const impacts = await getAssetImpacts(selectedAsset);
      setAssetImpacts(impacts);
    } catch (err) {
      setError(err.message);
      setAssetImpacts([]);
    } finally {
      setLoading(false);
    }
  }, [selectedAsset]);

  useEffect(() => {
    fetchAssets();
  }, [fetchAssets]);

  useEffect(() => {
    if (selectedAsset) {
      if (viewMode === 'chain') {
        fetchChain();
      } else {
        fetchImpacts();
      }
    }
  }, [selectedAsset, viewMode, fetchChain, fetchImpacts]);

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

  // Get events for selected asset
  const getEventsForAsset = useCallback(() => {
    if (!selectedAsset || !chainData || !chainData.chains) return [];
    return chainData.chains.map(c => ({
      id: c.source_event_id,
      message: c.root_event_message || 'Event',
      severity: c.source_severity,
    }));
  }, [selectedAsset, chainData]);

  return (
    <div className="impact-chain-page">
      <div className="chain-header">
        <h2>Impact Chain Analysis</h2>
        <p className="subtitle">Visualize cascading failure propagation through asset relationships</p>
      </div>

      <div className="chain-controls">
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
              <option value="chain">Impact Chain</option>
              <option value="impacts">Asset Impacts</option>
            </select>
          </label>

          {viewMode === 'chain' && (
            <label>
              Max Depth:
              <input
                type="number"
                min="1"
                max="100"
                value={maxDepth}
                onChange={(e) => setMaxDepth(parseInt(e.target.value) || 10)}
              />
            </label>
          )}

          <button onClick={viewMode === 'chain' ? fetchChain : fetchImpacts} disabled={!selectedAsset || loading}>
            Refresh
          </button>
        </div>
      </div>

      <div className="legend">
        <h4>Propagation Types</h4>
        <div className="legend-items">
          {Object.entries(PROPAGATION_TYPE_INFO).map(([type, info]) => (
            <div key={type} className="legend-item">
              <span 
                className="legend-dot"
                style={{ backgroundColor: info.color }}
              ></span>
              <span className="legend-label">{info.label}</span>
            </div>
          ))}
        </div>

        <h4>Severity</h4>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#eab308' }}></span>
            <span className="legend-label">WARNING</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#ef4444' }}></span>
            <span className="legend-label">CRITICAL</span>
          </div>
        </div>
      </div>

      <div className="chain-content">
        {loading && (
          <div className="loading">Loading impact chain...</div>
        )}

        {error && (
          <div className="error">Error: {error}</div>
        )}

        {!selectedAsset && !loading && (
          <div className="empty-state">
            <p>Select an asset above to view its impact chain.</p>
          </div>
        )}

        {viewMode === 'chain' && chainData && !loading && (
          <div className="chain-container">
            {chainData.chains && chainData.chains.length > 0 ? (
              chainData.chains.map((chain, index) => (
                <div key={index} className="chain-section">
                  <div className="chain-source">
                    <h4>
                      Source Event: {chain.root_event_message || 'Event'}
                    </h4>
                    <div className="source-info">
                      <SeverityBadge severity={chain.source_severity} />
                      <span>Asset: {chain.source_asset_name}</span>
                      <span>Total Affected: {chain.total_affected}</span>
                    </div>
                  </div>

                  {chain.chain && chain.chain.length > 0 ? (
                    <div className="chain-tree">
                      {chain.chain.map((node) => (
                        <ChainNodeWithKey
                          key={node.asset_id}
                          node={node}
                          depth={0}
                          expandedNodes={expandedNodes}
                          toggleExpand={toggleExpand}
                        />
                      ))}
                    </div>
                  ) : (
                    <p className="no-impacts">No downstream impacts</p>
                  )}
                </div>
              ))
            ) : (
              <div className="empty-state">
                <p>No propagation chains found for this asset.</p>
              </div>
            )}
          </div>
        )}

        {viewMode === 'impacts' && assetImpacts.length > 0 && !loading && (
          <div className="impacts-container">
            <div className="impacts-summary">
              <h4>Impacts on This Asset</h4>
              <div className="summary-stats">
                <span>Total: {assetImpacts.length}</span>
                <span className="critical">
                  Critical: {assetImpacts.filter(i => i.severity === 'CRITICAL').length}
                </span>
                <span className="warning">
                  Warning: {assetImpacts.filter(i => i.severity === 'WARNING').length}
                </span>
              </div>
            </div>

            <div className="impacts-list">
              {assetImpacts.map((impact, index) => (
                <div key={index} className="impact-item">
                  <div className="impact-header">
                    <SeverityBadge severity={impact.severity} />
                    <PropagationTypeBadge type={impact.propagation_type} />
                    <span className="depth-label">Depth {impact.depth}</span>
                  </div>
                  
                  <div className="impact-details">
                    <p className="source-asset">
                      <strong>From:</strong> {impact.source_asset_name}
                    </p>
                    <p className="event-message">
                      <strong>Event:</strong> {impact.event_message || 'N/A'}
                    </p>
                  </div>

                  <div className="impact-meta">
                    <span className="relationship">
                      via {impact.propagation_type?.replace('_', ' ')}
                    </span>
                    <span className="timestamp">
                      {new Date(impact.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {viewMode === 'impacts' && assetImpacts.length === 0 && selectedAsset && !loading && (
          <div className="empty-state">
            <p>No impacts found for this asset.</p>
          </div>
        )}
      </div>

      <div className="chain-footer">
        <div className="instructions">
          <h4>How to Use</h4>
          <ul>
            <li>Select an asset to view its impact chain</li>
            <li>Use "Impact Chain" view to see propagation hierarchies</li>
            <li>Use "Asset Impacts" view to see all impacts on this asset</li>
            <li>Click ▶/▼ to expand/collapse nodes</li>
            <li>Depth indicates how far from the source event</li>
          </ul>
        </div>

        <div className="explanation">
          <h4>Propagation Rules</h4>
          <ul>
            <li><strong>contains:</strong> Child failure → parent</li>
            <li><strong>feeds:</strong> Upstream failure → downstream</li>
            <li><strong>controls:</strong> Controller failure → controlled</li>
            <li><strong>connected_to:</strong> Bidirectional impact</li>
            <li><strong>monitors:</strong> Informational only</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ImpactChain;