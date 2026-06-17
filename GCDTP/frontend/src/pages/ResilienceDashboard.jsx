/**
 * Resilience Dashboard
 * 
 * Shows network resilience analysis including:
 * - Average network resilience
 * - Top critical assets
 * - Single points of failure
 * - Recommendations
 */

import React, { useState, useEffect } from 'react';
import {
  analyzeNetwork,
  getNetworkResilience,
  getTopCriticalAssets,
  getCriticalityColor,
  getResilienceColor,
  getPriorityColor,
  getCriticalityLevel,
  getResilienceLevel,
  formatRecommendationType,
} from '../api/resilience';
import CriticalAssetTable from '../components/CriticalAssetTable';
import NetworkRiskSummary from '../components/NetworkRiskSummary';
import './ResilienceDashboard.css';


function ResilienceDashboard() {
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [networkData, setNetworkData] = useState(null);
  const [criticalAssets, setCriticalAssets] = useState([]);
  const [error, setError] = useState(null);
  const [selectedAsset, setSelectedAsset] = useState(null);


  useEffect(() => {
    loadNetworkData();
  }, []);


  const loadNetworkData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Try to get existing network resilience
      const data = await getNetworkResilience();
      setNetworkData(data);
      setCriticalAssets(data.critical_assets || []);
    } catch (err) {
      // No analysis exists yet
      if (err.message.includes('No analyses found')) {
        setNetworkData(null);
        setCriticalAssets([]);
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };


  const handleAnalyzeNetwork = async () => {
    setAnalyzing(true);
    setError(null);
    
    try {
      const data = await analyzeNetwork(true);
      setNetworkData(data);
      setCriticalAssets(data.critical_assets || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };


  const getRecommendationsByPriority = () => {
    if (!networkData?.recommendations_by_priority) return {};
    return networkData.recommendations_by_priority;
  };


  if (loading) {
    return (
      <div className="resilience-dashboard">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading resilience data...</p>
        </div>
      </div>
    );
  }


  return (
    <div className="resilience-dashboard">
      <div className="dashboard-header">
        <h1>Resilience Dashboard</h1>
        <button
          className="btn-primary"
          onClick={handleAnalyzeNetwork}
          disabled={analyzing}
        >
          {analyzing ? 'Analyzing...' : 'Analyze Network'}
        </button>
      </div>


      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}


      {!networkData ? (
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h2>No Resilience Analysis</h2>
          <p>Click "Analyze Network" to generate resilience insights.</p>
        </div>
      ) : (
        <>
          {/* Network Overview */}
          <div className="network-overview">
            <div className="overview-card network-resilience">
              <h3>Network Resilience</h3>
              <div className="metric-large">
                <span 
                  className="metric-value"
                  style={{ color: getResilienceColor(networkData.avg_resilience) }}
                >
                  {networkData.avg_resilience.toFixed(1)}
                </span>
                <span className="metric-label">/ 100</span>
              </div>
              <div className={`resilience-badge ${getResilienceLevel(networkData.avg_resilience)}`}>
                {getResilienceLevel(networkData.avg_resilience)}
              </div>
            </div>


            <div className="overview-card network-criticality">
              <h3>Network Criticality</h3>
              <div className="metric-large">
                <span 
                  className="metric-value"
                  style={{ color: getCriticalityColor(networkData.avg_criticality) }}
                >
                  {networkData.avg_criticality.toFixed(1)}
                </span>
                <span className="metric-label">/ 100</span>
              </div>
              <div className={`criticality-badge ${getCriticalityLevel(networkData.avg_criticality)}`}>
                {getCriticalityLevel(networkData.avg_criticality)}
              </div>
            </div>


            <div className="overview-card spof-count">
              <h3>Single Points of Failure</h3>
              <div className="metric-large">
                <span 
                  className="metric-value"
                  style={{ color: networkData.single_points_of_failure > 0 ? '#ef4444' : '#22c55e' }}
                >
                  {networkData.single_points_of_failure}
                </span>
              </div>
              {networkData.single_points_of_failure > 0 && (
                <div className="warning-badge">
                  ⚠️ {networkData.single_points_of_failure} at risk
                </div>
              )}
            </div>


            <div className="overview-card asset-count">
              <h3>Assets Analyzed</h3>
              <div className="metric-large">
                <span className="metric-value">
                  {networkData.analyzed_assets}
                </span>
                <span className="metric-label">/ {networkData.total_assets}</span>
              </div>
            </div>
          </div>


          {/* Criticality Distribution */}
          <div className="criticality-distribution">
            <h2>Criticality Distribution</h2>
            <div className="distribution-bars">
              <div className="dist-bar high">
                <div 
                  className="bar-fill"
                  style={{ 
                    width: `${(networkData.high_criticality_count / networkData.analyzed_assets) * 100}%`,
                    backgroundColor: '#ef4444'
                  }}
                ></div>
                <span className="bar-label">HIGH (&gt;70)</span>
                <span className="bar-count">{networkData.high_criticality_count}</span>
              </div>
              <div className="dist-bar medium">
                <div 
                  className="bar-fill"
                  style={{ 
                    width: `${(networkData.medium_criticality_count / networkData.analyzed_assets) * 100}%`,
                    backgroundColor: '#f97316'
                  }}
                ></div>
                <span className="bar-label">MEDIUM (40-70)</span>
                <span className="bar-count">{networkData.medium_criticality_count}</span>
              </div>
              <div className="dist-bar low">
                <div 
                  className="bar-fill"
                  style={{ 
                    width: `${(networkData.low_criticality_count / networkData.analyzed_assets) * 100}%`,
                    backgroundColor: '#22c55e'
                  }}
                ></div>
                <span className="bar-label">LOW (&lt;40)</span>
                <span className="bar-count">{networkData.low_criticality_count}</span>
              </div>
            </div>
          </div>


          {/* Main Content Grid */}
          <div className="dashboard-grid">
            {/* Critical Assets Table */}
            <div className="dashboard-section critical-assets-section">
              <h2>Top Critical Assets</h2>
              <CriticalAssetTable 
                assets={criticalAssets}
                onSelectAsset={setSelectedAsset}
                selectedAsset={selectedAsset}
              />
            </div>


            {/* Recommendations Panel */}
            <div className="dashboard-section recommendations-section">
              <h2>Recommendations</h2>
              <div className="recommendations-list">
                {Object.entries(getRecommendationsByPriority()).map(([priority, recs]) => (
                  <div key={priority} className="priority-group">
                    <div 
                      className="priority-header"
                      style={{ borderColor: getPriorityColor(priority) }}
                    >
                      <span 
                        className="priority-badge"
                        style={{ backgroundColor: getPriorityColor(priority) }}
                      >
                        {priority}
                      </span>
                      <span className="priority-count">{recs.length} recommendations</span>
                    </div>
                    <div className="recommendations">
                      {recs.slice(0, 5).map((rec, idx) => (
                        <div key={idx} className="recommendation-item">
                          <span className="rec-type">
                            {formatRecommendationType(rec.type)}
                          </span>
                          <p className="rec-desc">{rec.description}</p>
                        </div>
                      ))}
                      {recs.length > 5 && (
                        <button className="show-more">
                          Show {recs.length - 5} more...
                        </button>
                      )}
                    </div>
                  </div>
                ))}
                {Object.keys(getRecommendationsByPriority()).length === 0 && (
                  <p className="no-recommendations">No recommendations yet.</p>
                )}
              </div>
            </div>
          </div>


          {/* Network Risk Summary */}
          <div className="dashboard-section risk-section">
            <h2>Network Risk Summary</h2>
            <NetworkRiskSummary data={networkData} />
          </div>
        </>
      )}
    </div>
  );
}


export default ResilienceDashboard;
