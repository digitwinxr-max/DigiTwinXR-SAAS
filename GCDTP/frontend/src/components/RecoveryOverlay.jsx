import React from 'react';
import { getHealthColor } from '../api/recovery';
import './RecoveryOverlay.css';


/**
 * RecoveryOverlay component
 * 
 * Displays recovered health colors as an overlay on the map.
 * Does NOT alter live markers.
 */
function RecoveryOverlay({ 
  isVisible, 
  onToggle,
  recoveredHealth = {}, // { assetId: { before, after } }
}) {
  if (!isVisible) {
    return null;
  }

  const legend = [
    { range: '80-100', color: '#22c55e', label: 'Healthy' },
    { range: '40-79', color: '#f97316', label: 'Degraded' },
    { range: '0-39', color: '#ef4444', label: 'Critical' },
  ];

  return (
    <div className="recovery-overlay">
      <div className="overlay-header">
        <h4>Recovery Mode</h4>
        <button onClick={onToggle} className="close-btn">
          ×
        </button>
      </div>
      
      <div className="overlay-content">
        <p className="overlay-info">
          Showing recovered health overlay.
          Live markers are not affected.
        </p>

        <div className="overlay-legend">
          <h5>Health Legend</h5>
          {legend.map((item) => (
            <div key={item.range} className="legend-item">
              <span 
                className="legend-color" 
                style={{ backgroundColor: item.color }} 
              />
              <span className="legend-range">{item.range}</span>
              <span className="legend-label">{item.label}</span>
            </div>
          ))}
        </div>

        <div className="overlay-stats">
          <div className="stat">
            <span className="stat-label">Recovered Assets</span>
            <span className="stat-value">{Object.keys(recoveredHealth).length}</span>
          </div>
        </div>
      </div>
    </div>
  );
}


/**
 * Toggle button for recovery overlay
 */
function RecoveryToggle({ isActive, onClick, recoveryCount = 0 }) {
  return (
    <button 
      className={`recovery-toggle ${isActive ? 'active' : ''}`}
      onClick={onClick}
    >
      <span className="toggle-icon">🔧</span>
      <span className="toggle-label">Recovery</span>
      {recoveryCount > 0 && (
        <span className="toggle-badge">{recoveryCount}</span>
      )}
    </button>
  );
}


export { RecoveryOverlay, RecoveryToggle };
export default RecoveryOverlay;