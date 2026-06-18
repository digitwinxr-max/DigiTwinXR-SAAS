/**
 * Root Cause Analysis Page
 * 
 * READ ONLY engine - explains WHY failures occurred.
 * NO automation, NO work orders, NO event modifications.
 */

import React, { useState, useEffect } from 'react';
import { CauseTree } from '../components/CauseTree';
import { FactorPanel } from '../components/FactorPanel';
import { EventSequenceView } from '../components/EventSequenceView';
import {
  analyzeAsset,
  getAnalysis,
  getAnalysesForAsset,
  getHighConfidenceAnalyses
} from '../api/rootCause';
import './RootCauseAnalysis.css';

export function RootCauseAnalysis() {
  // State
  const [selectedAsset, setSelectedAsset] = useState('asset-001');
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [highConfidence, setHighConfidence] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load high confidence on mount
  useEffect(() => {
    loadHighConfidence();
  }, []);

  const loadHighConfidence = async () => {
    try {
      const data = await getHighConfidenceAnalyses(0.5);
      setHighConfidence(data.analyses || []);
    } catch (error) {
      console.error('Failed to load high confidence:', error);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const result = await analyzeAsset(selectedAsset, {
        analysis_type: 'failure',
        time_window_hours: 24
      });
      setCurrentAnalysis(result);
      
      // Refresh history
      const history = await getAnalysesForAsset(selectedAsset, 10);
      setAnalysisHistory(history.analyses || []);
      
      // Refresh high confidence
      await loadHighConfidence();
    } catch (error) {
      console.error('Failed to analyze:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAnalysis = async (analysisId) => {
    try {
      const result = await getAnalysis(analysisId);
      setCurrentAnalysis(result);
    } catch (error) {
      console.error('Failed to load analysis:', error);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#4CAF50';
    if (confidence >= 0.6) return '#FF9800';
    return '#F44336';
  };

  return (
    <div className="root-cause-analysis">
      {/* Header */}
      <header className="page-header">
        <h1>🔍 Root Cause Analysis</h1>
        <div className="read-only-badge">
          READ ONLY - NO automation
        </div>
      </header>

      <div className="page-layout">
        {/* Left Panel - High Confidence */}
        <aside className="left-panel">
          <div className="panel-section">
            <h3>High Confidence</h3>
            <div className="analysis-list">
              {highConfidence.length === 0 ? (
                <p className="empty">No high confidence analyses</p>
              ) : (
                highConfidence.map((analysis) => (
                  <div
                    key={analysis.id}
                    className="analysis-item"
                    onClick={() => handleSelectAnalysis(analysis.id)}
                  >
                    <span className="asset-name">Asset {analysis.asset_id?.slice(0, 8)}</span>
                    <span 
                      className="confidence"
                      style={{ color: getConfidenceColor(analysis.confidence) }}
                    >
                      {(analysis.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="panel-section">
            <h3>Analysis History</h3>
            <div className="analysis-list">
              {analysisHistory.length === 0 ? (
                <p className="empty">No history yet</p>
              ) : (
                analysisHistory.map((analysis) => (
                  <div
                    key={analysis.id}
                    className="analysis-item"
                    onClick={() => handleSelectAnalysis(analysis.id)}
                  >
                    <span className="asset-name">{analysis.analysis_type}</span>
                    <span className="date">
                      {new Date(analysis.created_at).toLocaleDateString()}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </aside>

        {/* Center Panel - Analysis */}
        <main className="center-panel">
          {/* Input Section */}
          <div className="input-section">
            <h3>Run Analysis</h3>
            <div className="form-row">
              <div className="form-group">
                <label>Asset ID</label>
                <input
                  type="text"
                  value={selectedAsset}
                  onChange={(e) => setSelectedAsset(e.target.value)}
                  placeholder="Enter asset ID"
                />
              </div>
              <button
                className="analyze-btn"
                onClick={handleAnalyze}
                disabled={loading}
              >
                {loading ? 'Analyzing...' : '🔍 Analyze'}
              </button>
            </div>
          </div>

          {/* Results Section */}
          {currentAnalysis && (
            <div className="results-section">
              <div className="result-header">
                <h3>Analysis Result</h3>
                <span className="analysis-id">ID: {currentAnalysis.id?.slice(0, 8)}</span>
              </div>

              {/* Summary Card */}
              <div className="summary-card">
                <div className="summary-row">
                  <span className="label">Asset</span>
                  <span className="value">{currentAnalysis.asset_id?.slice(0, 16)}...</span>
                </div>
                <div className="summary-row">
                  <span className="label">Analysis Type</span>
                  <span className="value">{currentAnalysis.analysis_type}</span>
                </div>
                <div className="summary-row">
                  <span className="label">Confidence</span>
                  <span 
                    className="value confidence"
                    style={{ color: getConfidenceColor(currentAnalysis.confidence) }}
                  >
                    {(currentAnalysis.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              {/* Probable Cause */}
              <div className="cause-card">
                <h4>Probable Cause</h4>
                <p>{currentAnalysis.probable_cause}</p>
              </div>

              {/* Summary */}
              {currentAnalysis.summary && (
                <div className="summary-text">
                  <h4>Summary</h4>
                  <p>{currentAnalysis.summary}</p>
                </div>
              )}

              {/* Two Column Layout */}
              <div className="two-column">
                {/* Factors */}
                <div className="column">
                  <FactorPanel 
                    factors={currentAnalysis.factors} 
                    rankedFactors={currentAnalysis.ranked_factors}
                  />
                </div>
                
                {/* Chain */}
                <div className="column">
                  <CauseTree chains={currentAnalysis.chains} />
                </div>
              </div>
            </div>
          )}

          {!currentAnalysis && (
            <div className="no-analysis">
              <p>Select an asset and run analysis to see results</p>
            </div>
          )}
        </main>

        {/* Right Panel - Info */}
        <aside className="right-panel">
          <div className="info-panel">
            <h3>RCA Engine Info</h3>
            
            <div className="info-section">
              <h4>What RCA Does</h4>
              <ul>
                <li>🔍 Explains WHY failures occurred</li>
                <li>📊 Ranks contributing factors</li>
                <li>🔗 Builds causal chains</li>
                <li>📈 Calculates confidence</li>
              </ul>
            </div>

            <div className="info-section">
              <h4>What RCA Does NOT Do</h4>
              <ul className="not-list">
                <li>❌ Modify events</li>
                <li>❌ Create work orders</li>
                <li>❌ Execute agents</li>
                <li>❌ Perform automation</li>
                <li>❌ Send notifications</li>
              </ul>
            </div>

            <div className="info-section">
              <h4>Factor Types</h4>
              <div className="factor-types">
                <span className="type" style={{ backgroundColor: '#2196F3' }}>Measurement</span>
                <span className="type" style={{ backgroundColor: '#F44336' }}>Event</span>
                <span className="type" style={{ backgroundColor: '#FF9800' }}>Health</span>
                <span className="type" style={{ backgroundColor: '#9C27B0' }}>Relationship</span>
                <span className="type" style={{ backgroundColor: '#00BCD4' }}>Timeline</span>
                <span className="type" style={{ backgroundColor: '#795548' }}>Logbook</span>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default RootCauseAnalysis;
