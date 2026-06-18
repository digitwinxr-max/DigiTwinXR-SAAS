/**
 * Risk Gauge Component
 * 
 * Visual gauge for failure probability.
 */

import React from 'react';

export function RiskGauge({ probability, size = 200 }) {
  const getColor = (prob) => {
    if (prob <= 25) return '#4CAF50';  // Low
    if (prob <= 50) return '#FF9800';  // Medium
    if (prob <= 75) return '#F44336';  // High
    return '#9C27B0';                   // Critical
  };

  const getLabel = (prob) => {
    if (prob <= 25) return 'LOW';
    if (prob <= 50) return 'MEDIUM';
    if (prob <= 75) return 'HIGH';
    return 'CRITICAL';
  };

  const color = getColor(probability);
  const label = getLabel(probability);
  
  // Calculate arc
  const angle = (probability / 100) * 180;
  const radians = (angle - 90) * (Math.PI / 180);
  const x = 50 + 40 * Math.cos(radians);
  const y = 50 + 40 * Math.sin(radians);
  const largeArc = angle > 180 ? 1 : 0;

  return (
    <div className="risk-gauge" style={{ width: size, height: size / 2 + 40 }}>
      <svg viewBox="0 0 100 60" width={size} height={size / 2 + 20}>
        {/* Background arc */}
        <path
          d="M 5 50 A 45 45 0 0 1 95 50"
          fill="none"
          stroke="#e0e0e0"
          strokeWidth="10"
          strokeLinecap="round"
        />
        
        {/* Colored arc segments */}
        <path d="M 5 50 A 45 45 0 0 1 27.5 16" fill="none" stroke="#4CAF50" strokeWidth="10" strokeLinecap="round" />
        <path d="M 27.5 16 A 45 45 0 0 1 72.5 16" fill="none" stroke="#FF9800" strokeWidth="10" strokeLinecap="round" />
        <path d="M 72.5 16 A 45 45 0 0 1 95 50" fill="none" stroke="#F44336" strokeWidth="10" strokeLinecap="round" />
        
        {/* Needle */}
        <line
          x1="50"
          y1="50"
          x2={x}
          y2={y}
          stroke="#333"
          strokeWidth="2"
          strokeLinecap="round"
        />
        <circle cx="50" cy="50" r="4" fill="#333" />
      </svg>
      
      <div className="gauge-value" style={{ color }}>
        <span className="percentage">{probability.toFixed(1)}%</span>
        <span className="label">{label}</span>
      </div>
      
      <style>{`
        .risk-gauge {
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .gauge-value {
          display: flex;
          flex-direction: column;
          align-items: center;
          margin-top: 0.5rem;
        }

        .percentage {
          font-size: 1.5rem;
          font-weight: bold;
        }

        .label {
          font-size: 0.75rem;
          font-weight: bold;
          text-transform: uppercase;
        }
      `}</style>
    </div>
  );
}

export default RiskGauge;
