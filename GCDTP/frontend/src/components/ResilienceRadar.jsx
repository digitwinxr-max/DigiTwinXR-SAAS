/**
 * Resilience Radar Chart Component
 * 
 * Visualizes asset resilience across multiple dimensions.
 */

import React, { useEffect, useRef } from 'react';
import { getCriticalityColor, getResilienceColor } from '../api/resilience';


/**
 * Simple radar chart for resilience visualization
 * Shows multiple metrics on a single asset or comparison
 */
function ResilienceRadar({ 
  data, 
  width = 300, 
  height = 300,
  title = 'Resilience Profile' 
}) {
  const canvasRef = useRef(null);


  useEffect(() => {
    if (!canvasRef.current || !data) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    canvas.width = width;
    canvas.height = height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 40;
    
    // Draw background circles
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 1;
    
    for (let i = 1; i <= 4; i++) {
      const r = (radius / 4) * i;
      ctx.beginPath();
      ctx.arc(centerX, centerY, r, 0, Math.PI * 2);
      ctx.stroke();
    }
    
    // Draw axes
    const metrics = ['Criticality', 'Resilience', 'Dependencies', 'Downstream'];
    const numAxes = metrics.length;
    
    ctx.strokeStyle = '#d1d5db';
    ctx.lineWidth = 1;
    
    for (let i = 0; i < numAxes; i++) {
      const angle = (Math.PI * 2 / numAxes) * i - Math.PI / 2;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;
      
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(x, y);
      ctx.stroke();
      
      // Draw labels
      ctx.fillStyle = '#6b7280';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      const labelX = centerX + Math.cos(angle) * (radius + 25);
      const labelY = centerY + Math.sin(angle) * (radius + 25);
      ctx.fillText(metrics[i], labelX, labelY);
    }
    
    // Normalize values to 0-1
    const values = [
      (data.criticality_score || 0) / 100,
      (data.resilience_score || 0) / 100,
      Math.min((data.dependency_count || 0) / 20, 1), // Normalize dependencies
      Math.min((data.downstream_count || 0) / 10, 1), // Normalize downstream
    ];
    
    // Draw data polygon
    ctx.beginPath();
    ctx.strokeStyle = getCriticalityColor(data.criticality_score);
    ctx.fillStyle = getCriticalityColor(data.criticality_score) + '40';
    ctx.lineWidth = 2;
    
    for (let i = 0; i < numAxes; i++) {
      const angle = (Math.PI * 2 / numAxes) * i - Math.PI / 2;
      const r = values[i] * radius;
      const x = centerX + Math.cos(angle) * r;
      const y = centerY + Math.sin(angle) * r;
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    
    // Draw data points
    ctx.fillStyle = getCriticalityColor(data.criticality_score);
    
    for (let i = 0; i < numAxes; i++) {
      const angle = (Math.PI * 2 / numAxes) * i - Math.PI / 2;
      const r = values[i] * radius;
      const x = centerX + Math.cos(angle) * r;
      const y = centerY + Math.sin(angle) * r;
      
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.fill();
    }
    
  }, [data, width, height]);


  if (!data) {
    return (
      <div className="resilience-radar empty">
        <p>No data available</p>
      </div>
    );
  }


  return (
    <div className="resilience-radar">
      {title && <h3 className="radar-title">{title}</h3>}
      <canvas ref={canvasRef}></canvas>
      <div className="radar-legend">
        <div className="legend-item">
          <div 
            className="legend-color" 
            style={{ backgroundColor: getCriticalityColor(data.criticality_score) }}
          ></div>
          <span>Criticality: {data.criticality_score?.toFixed(1)}</span>
        </div>
        <div className="legend-item">
          <div 
            className="legend-color" 
            style={{ backgroundColor: getResilienceColor(data.resilience_score) }}
          ></div>
          <span>Resilience: {data.resilience_score?.toFixed(1)}</span>
        </div>
      </div>
    </div>
  );
}


/**
 * Compare multiple assets on a single radar chart
 */
export function MultiAssetRadar({ assets, width = 400, height = 400 }) {
  const canvasRef = useRef(null);
  
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];


  useEffect(() => {
    if (!canvasRef.current || !assets || assets.length === 0) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    canvas.width = width;
    canvas.height = height;
    
    ctx.clearRect(0, 0, width, height);
    
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 50;
    
    // Draw background circles
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 1;
    
    for (let i = 1; i <= 4; i++) {
      const r = (radius / 4) * i;
      ctx.beginPath();
      ctx.arc(centerX, centerY, r, 0, Math.PI * 2);
      ctx.stroke();
    }
    
    // Draw axes
    const metrics = ['Criticality', 'Resilience', 'Dependencies', 'Downstream'];
    const numAxes = metrics.length;
    
    ctx.strokeStyle = '#d1d5db';
    ctx.lineWidth = 1;
    
    for (let i = 0; i < numAxes; i++) {
      const angle = (Math.PI * 2 / numAxes) * i - Math.PI / 2;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;
      
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(x, y);
      ctx.stroke();
      
      // Labels
      ctx.fillStyle = '#6b7280';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      const labelX = centerX + Math.cos(angle) * (radius + 25);
      const labelY = centerY + Math.sin(angle) * (radius + 25);
      ctx.fillText(metrics[i], labelX, labelY);
    }
    
    // Draw each asset
    assets.forEach((asset, idx) => {
      const values = [
        (asset.criticality_score || 0) / 100,
        (asset.resilience_score || 0) / 100,
        Math.min((asset.dependency_count || 0) / 20, 1),
        Math.min((asset.downstream_count || 0) / 10, 1),
      ];
      
      const color = colors[idx % colors.length];
      
      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.fillStyle = color + '30';
      ctx.lineWidth = 2;
      
      for (let i = 0; i < numAxes; i++) {
        const angle = (Math.PI * 2 / numAxes) * i - Math.PI / 2;
        const r = values[i] * radius;
        const x = centerX + Math.cos(angle) * r;
        const y = centerY + Math.sin(angle) * r;
        
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    });
    
  }, [assets, width, height]);


  return (
    <div className="multi-asset-radar">
      <canvas ref={canvasRef}></canvas>
      <div className="radar-legend">
        {assets.map((asset, idx) => (
          <div key={asset.asset_id} className="legend-item">
            <div 
              className="legend-color" 
              style={{ backgroundColor: colors[idx % colors.length] }}
            ></div>
            <span>{asset.asset_name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}


export default ResilienceRadar;
