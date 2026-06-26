/**
 * Network Risk Summary Component
 * 
 * Displays overall network risk metrics and visualizations.
 */

import React from 'react';
import {
  getCriticalityColor,
  getResilienceColor,
} from '../api/resilience';


function NetworkRiskSummary({ data }) {
  if (!data) {
    return (
      <div className="network-risk-summary empty">
        <p>No data available</p>
      </div>
    );
  }


  const calculateRiskScore = () => {
    // Risk = High criticality - High resilience
    const criticalityWeight = 0.6;
    const resilienceWeight = 0.4;
    
    const risk = 
      (data.avg_criticality * criticalityWeight) - 
      (data.avg_resilience * resilienceWeight);
    
    return Math.max(0, Math.min(100, risk));
  };


  const riskScore = calculateRiskScore();
  const riskLevel = riskScore >= 70 ? 'HIGH' : riskScore >= 40 ? 'MEDIUM' : 'LOW';


  const getRiskColor = (score) => {
    if (score >= 70) return '#ef4444';
    if (score >= 40) return '#f97316';
    return '#22c55e';
  };


  return (
    <div className="network-risk-summary">
      {/* Risk Score Gauge */}
      <div className="risk-gauge">
        <div className="gauge-container">
          <svg viewBox="0 0 200 100" className="gauge-svg">
            {/* Background arc */}
            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="20"
              strokeLinecap="round"
            />
            {/* Colored arc based on risk */}
            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke={getRiskColor(riskScore)}
              strokeWidth="20"
              strokeLinecap="round"
              strokeDasharray={`${riskScore * 2.51} 251`}
            />
          </svg>
          <div className="gauge-center">
            <span 
              className="risk-value"
              style={{ color: getRiskColor(riskScore) }}
            >
              {riskScore.toFixed(0)}
            </span>
            <span className="risk-label">Risk Score</span>
          </div>
        </div>
        <div className={`risk-level ${riskLevel}`}>
          {riskLevel} RISK
        </div>
      </div>


      {/* Metrics Grid */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">📊</div>
          <div className="metric-info">
            <span className="metric-value">{data.analyzed_assets}</span>
            <span className="metric-label">Assets Analyzed</span>
          </div>
        </div>


        <div className="metric-card">
          <div className="metric-icon">⚠️</div>
          <div className="metric-info">
            <span className="metric-value" style={{ color: data.single_points_of_failure > 0 ? '#ef4444' : '#22c55e' }}>
              {data.single_points_of_failure}
            </span>
            <span className="metric-label">Single Points of Failure</span>
          </div>
        </div>


        <div className="metric-card">
          <div className="metric-icon">🔴</div>
          <div className="metric-info">
            <span className="metric-value" style={{ color: '#ef4444' }}>
              {data.high_criticality_count}
            </span>
            <span className="metric-label">High Criticality</span>
          </div>
        </div>


        <div className="metric-card">
          <div className="metric-icon">🟡</div>
          <div className="metric-info">
            <span className="metric-value" style={{ color: '#f97316' }}>
              {data.medium_criticality_count}
            </span>
            <span className="metric-label">Medium Criticality</span>
          </div>
        </div>


        <div className="metric-card">
          <div className="metric-icon">🟢</div>
          <div className="metric-info">
            <span className="metric-value" style={{ color: '#22c55e' }}>
              {data.low_criticality_count}
            </span>
            <span className="metric-label">Low Criticality</span>
          </div>
        </div>


        <div className="metric-card">
          <div className="metric-icon">📈</div>
          <div className="metric-info">
            <span className="metric-value" style={{ color: getCriticalityColor(data.avg_criticality) }}>
              {data.avg_criticality.toFixed(1)}
            </span>
            <span className="metric-label">Avg Criticality</span>
          </div>
        </div>


        <div className="metric-card">
          <div className="metric-icon">🛡️</div>
          <div className="metric-info">
            <span className="metric-value" style={{ color: getResilienceColor(data.avg_resilience) }}>
              {data.avg_resilience.toFixed(1)}
            </span>
            <span className="metric-label">Avg Resilience</span>
          </div>
        </div>
      </div>


      {/* Risk Factors */}
      <div className="risk-factors">
        <h4>Risk Factors</h4>
        <div className="factor-list">
          {data.single_points_of_failure > 0 && (
            <div className="risk-factor critical">
              <span className="factor-icon">⚠️</span>
              <span className="factor-text">
                {data.single_points_of_failure} single point{data.single_points_of_failure > 1 ? 's' : ''} of failure identified
              </span>
            </div>
          )}
          
          {data.high_criticality_count > data.analyzed_assets * 0.3 && (
            <div className="risk-factor high">
              <span className="factor-icon">🔴</span>
              <span className="factor-text">
                High concentration of critical assets ({((data.high_criticality_count / data.analyzed_assets) * 100).toFixed(0)}%)
              </span>
            </div>
          )}
          
          {data.avg_resilience < 50 && (
            <div className="risk-factor medium">
              <span className="factor-icon">📉</span>
              <span className="factor-text">
                Low average resilience ({data.avg_resilience.toFixed(1)})
              </span>
            </div>
          )}
          
          {data.avg_criticality > 60 && (
            <div className="risk-factor medium">
              <span className="factor-icon">📊</span>
              <span className="factor-text">
                High average criticality ({data.avg_criticality.toFixed(1)})
              </span>
            </div>
          )}
          
          {data.single_points_of_failure === 0 && 
           data.high_criticality_count <= data.analyzed_assets * 0.3 && 
           data.avg_resilience >= 50 && (
            <div className="risk-factor low">
              <span className="factor-icon">✅</span>
              <span className="factor-text">
                Network resilience looks healthy
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


export default NetworkRiskSummary;
