import React from 'react';
import { getHealthColor } from '../api/scenarios';
import './ScenarioOverlay.css';


/**
 * ScenarioOverlay component
 * 
 * Displays simulated health colors as an overlay on the map.
 * Does NOT alter live markers.
 */
function ScenarioOverlay({ 
  isVisible, 
  onToggle,
  simulatedHealth = {} // { assetId: healthScore }
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
    <div className="scenario-overlay">
      <div className="overlay-header">
        <h4>Simulation Mode</h4>
        <button onClick={onToggle} className="close-btn">
          ×
        </button>
      </div>
      
      <div className="overlay-content">
        <p className="overlay-info">
          Showing simulated health overlay.
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
            <span className="stat-label">Simulated Assets</span>
            <span className="stat-value">{Object.keys(simulatedHealth).length}</span>
          </div>
        </div>
      </div>
    </div>
  );
}


/**
 * Simulated marker overlay
 * 
 * Shows a simulated health indicator at a position.
 * Used as a separate layer on top of live markers.
 */
function SimulatedMarker({ 
  position, // [lat, lng]
  assetId,
  healthScore,
  onClick,
}) {
  const color = getHealthColor(healthScore);

  return (
    <div 
      className="simulated-marker"
      style={{
        position: 'absolute',
        left: `${position[1]}%`, // lng
        top: `${position[0]}%`,  // lat
        transform: 'translate(-50%, -50%)',
        pointerEvents: 'onClick' in {} ? 'auto' : 'none',
      }}
      onClick={onClick}
    >
      <div 
        className="marker-ring"
        style={{ borderColor: color }}
      />
      <div 
        className="marker-inner"
        style={{ backgroundColor: color }}
      >
        {healthScore.toFixed(0)}
      </div>
    </div>
  );
}


/**
 * Toggle button for simulation overlay
 */
function SimulationToggle({ isActive, onClick, scenarioCount = 0 }) {
  return (
    <button 
      className={`simulation-toggle ${isActive ? 'active' : ''}`}
      onClick={onClick}
    >
      <span className="toggle-icon">⚡</span>
      <span className="toggle-label">Simulation</span>
      {scenarioCount > 0 && (
        <span className="toggle-badge">{scenarioCount}</span>
      )}
    </button>
  );
}


export { ScenarioOverlay, SimulatedMarker, SimulationToggle };
export default ScenarioOverlay;