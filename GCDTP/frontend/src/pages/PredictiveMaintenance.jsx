/**
 * Predictive Maintenance Page
 * 
 * Deterministic failure prediction without ML/AI.
 */

import React, { useState, useEffect } from 'react';
import { PredictionCard } from '../components/PredictionCard';
import { RiskGauge } from '../components/RiskGauge';
import { RecommendationPanel } from '../components/RecommendationPanel';
import { MaintenanceTimeline } from '../components/MaintenanceTimeline';
import {
  runPrediction,
  getHighRiskAssets,
  getRecommendations,
  getHealthTimeline
} from '../api/predictive';
import './PredictiveMaintenance.css';

export function PredictiveMaintenance() {
  // State
  const [selectedAsset, setSelectedAsset] = useState('asset-001');
  const [prediction, setPrediction] = useState(null);
  const [highRiskAssets, setHighRiskAssets] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [timeline, setTimeline] = useState(null);
  const [loading, setLoading] = useState(false);

  // Input state
  const [currentHealth, setCurrentHealth] = useState(85);
  const [healthTrend, setHealthTrend] = useState(-1);
  const [activeEvents, setActiveEvents] = useState(1);
  const [measurementAnomalies, setMeasurementAnomalies] = useState(1);
  const [daysSinceMaintenance, setDaysSinceMaintenance] = useState(45);
  const [assetType, setAssetType] = useState('transformer');

  // Load data on mount
  useEffect(() => {
    loadHighRiskAssets();
    loadRecommendations();
  }, []);

  const loadHighRiskAssets = async () => {
    try {
      const data = await getHighRiskAssets(10);
      setHighRiskAssets(data.assets || []);
    } catch (error) {
      console.error('Failed to load high-risk assets:', error);
    }
  };

  const loadRecommendations = async () => {
    try {
      const data = await getRecommendations(20);
      setRecommendations(data.recommendations || []);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    }
  };

  const handleRunPrediction = async () => {
    setLoading(true);
    try {
      const result = await runPrediction(selectedAsset, {
        current_health: currentHealth,
        health_trend: healthTrend,
        active_events: activeEvents,
        measurement_anomalies: measurementAnomalies,
        days_since_maintenance: daysSinceMaintenance,
        asset_type: assetType
      });
      
      setPrediction(result);
      
      // Load timeline
      const timelineData = await getHealthTimeline(selectedAsset, currentHealth, healthTrend);
      setTimeline(timelineData);
      
      // Refresh high-risk and recommendations
      await loadHighRiskAssets();
      await loadRecommendations();
    } catch (error) {
      console.error('Failed to run prediction:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAssetSelect = (asset) => {
    setSelectedAsset(asset.asset_id);
  };

  return (
    <div className="predictive-maintenance">
      {/* Header */}
      <header className="page-header">
        <h1>🔮 Predictive Maintenance</h1>
        <span className="no-ml-badge">Deterministic - NO ML/AI</span>
      </header>

      <div className="page-layout">
        {/* Left Panel - High Risk Assets */}
        <aside className="left-panel">
          <div className="panel-section">
            <h3>High-Risk Assets</h3>
            <div className="asset-list">
              {highRiskAssets.length === 0 ? (
                <p className="empty">No high-risk assets</p>
              ) : (
                highRiskAssets.map((asset) => (
                  <div
                    key={asset.asset_id}
                    className={`asset-item ${selectedAsset === asset.asset_id ? 'selected' : ''}`}
                    onClick={() => handleAssetSelect(asset)}
                  >
                    <span className="asset-name">{asset.asset_name}</span>
                    <span 
                      className="risk-badge"
                      style={{ backgroundColor: asset.risk_level === 'CRITICAL' ? '#9C27B0' : '#F44336' }}
                    >
                      {asset.failure_probability.toFixed(0)}%
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </aside>

        {/* Center Panel - Input & Prediction */}
        <main className="center-panel">
          {/* Input Form */}
          <div className="input-section">
            <h3>Prediction Parameters</h3>
            <div className="form-grid">
              <div className="form-group">
                <label>Current Health (%)</label>
                <input
                  type="number"
                  value={currentHealth}
                  onChange={(e) => setCurrentHealth(Number(e.target.value))}
                  min={0}
                  max={100}
                />
              </div>
              
              <div className="form-group">
                <label>Health Trend (/day)</label>
                <input
                  type="number"
                  value={healthTrend}
                  onChange={(e) => setHealthTrend(Number(e.target.value))}
                  step={0.1}
                />
              </div>
              
              <div className="form-group">
                <label>Active Events</label>
                <input
                  type="number"
                  value={activeEvents}
                  onChange={(e) => setActiveEvents(Number(e.target.value))}
                  min={0}
                />
              </div>
              
              <div className="form-group">
                <label>Measurement Anomalies</label>
                <input
                  type="number"
                  value={measurementAnomalies}
                  onChange={(e) => setMeasurementAnomalies(Number(e.target.value))}
                  min={0}
                />
              </div>
              
              <div className="form-group">
                <label>Days Since Maintenance</label>
                <input
                  type="number"
                  value={daysSinceMaintenance}
                  onChange={(e) => setDaysSinceMaintenance(Number(e.target.value))}
                  min={0}
                />
              </div>
              
              <div className="form-group">
                <label>Asset Type</label>
                <select value={assetType} onChange={(e) => setAssetType(e.target.value)}>
                  <option value="transformer">Transformer</option>
                  <option value="sensor">Sensor</option>
                  <option value="meter">Meter</option>
                  <option value="switch">Switch</option>
                  <option value="generic">Generic</option>
                </select>
              </div>
            </div>
            
            <button 
              className="run-prediction-btn"
              onClick={handleRunPrediction}
              disabled={loading}
            >
              {loading ? 'Running...' : '🔮 Run Prediction'}
            </button>
          </div>

          {/* Prediction Results */}
          {prediction && (
            <div className="prediction-section">
              <div className="prediction-header">
                <h3>Prediction Results</h3>
                <span className="asset-id">Asset: {selectedAsset}</span>
              </div>
              
              <div className="prediction-content">
                <div className="gauge-container">
                  <RiskGauge probability={prediction.failure_probability} />
                </div>
                
                <div className="prediction-details">
                  <PredictionCard prediction={prediction} />
                </div>
              </div>
              
              {timeline && (
                <div className="timeline-container">
                  <MaintenanceTimeline timeline={timeline} />
                </div>
              )}
            </div>
          )}
        </main>

        {/* Right Panel - Recommendations */}
        <aside className="right-panel">
          <RecommendationPanel recommendations={recommendations} />
        </aside>
      </div>

      {/* Formula Reference */}
      <div className="formula-reference">
        <h4>Failure Probability Formula</h4>
        <code>
          FP = 0.30 × health_degradation + 0.25 × active_events + 0.25 × anomalies + 0.20 × maintenance_age
        </code>
        <p className="note">Deterministic calculation - NO ML, NO neural networks</p>
      </div>
    </div>
  );
}

export default PredictiveMaintenance;
