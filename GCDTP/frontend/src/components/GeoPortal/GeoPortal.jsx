import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapContainer, TileLayer, CircleMarker, Popup, LayerGroup } from 'react-leaflet';
import { useSystemEvents, EVENT_TYPES } from '../../hooks/useSystemEvents';
import { getAssetImpacts } from '../../api/propagation';
import { getContributors, getHealthColor } from '../../api/networkHealth';
import 'leaflet/dist/leaflet.css';
import './GeoPortal.css';

const HEALTH_COLORS = {
  HEALTHY: { color: '#22c55e', fillColor: '#22c55e' },
  DEGRADED: { color: '#f97316', fillColor: '#f97316' },
  CRITICAL: { color: '#ef4444', fillColor: '#ef4444' },
  UNKNOWN: { color: '#6b7280', fillColor: '#6b7280' },
};

const SEVERITY_COLORS = {
  WARNING: '#eab308',
  CRITICAL: '#ef4444',
};

const PROPAGATION_COLORS = {
  CHILD_FAILURE: '#ef4444',
  UPSTREAM_FAILURE: '#f97316',
  DOWNSTREAM_FAILURE: '#eab308',
  DEPENDENCY_IMPACT: '#8b5cf6',
};

function GeoPortal() {
  const navigate = useNavigate();
  const [geojsonData, setGeojsonData] = useState(null);
  const [healthData, setHealthData] = useState({});
  const [events, setEvents] = useState([]);
  const [sensorCounts, setSensorCounts] = useState({});
  const [assetImpacts, setAssetImpacts] = useState({});
  const [assetContributors, setAssetContributors] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [layers, setLayers] = useState({
    assets: true,
    events: true,
    sensors: false,
  });

  const mapRef = useRef(null);

  const fetchAllData = useCallback(async () => {
    try {
      setLoading(true);
      const [geoRes, healthRes, eventsRes] = await Promise.all([
        fetch('/api/assets/geojson'),
        fetch('/api/health/assets'),
        fetch('/api/events/active'),
      ]);

      if (!geoRes.ok) throw new Error('Failed to fetch GeoJSON');
      if (!healthRes.ok) throw new Error('Failed to fetch health data');
      if (!eventsRes.ok) throw new Error('Failed to fetch events');

      const geoData = await geoRes.json();
      const healthData = await healthRes.json();
      const eventsData = await eventsRes.json();

      setGeojsonData(geoData);
      
      const healthMap = {};
      healthData.items?.forEach(h => {
        healthMap[h.asset_id] = h;
      });
      setHealthData(healthMap);
      
      setEvents(eventsData.items || []);
      
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSensorCount = useCallback(async (assetId) => {
    try {
      const response = await fetch(`/api/assets/${assetId}/sensors`);
      if (response.ok) {
        const data = await response.json();
        setSensorCounts(prev => ({ ...prev, [assetId]: data.total || 0 }));
      }
    } catch (err) {
      console.error('Failed to fetch sensor count:', err);
    }
  }, []);

  const fetchAssetImpacts = useCallback(async (assetId) => {
    try {
      const impacts = await getAssetImpacts(assetId);
      setAssetImpacts(prev => ({ ...prev, [assetId]: impacts }));
    } catch (err) {
      console.error('Failed to fetch asset impacts:', err);
    }
  }, []);

  const fetchAssetContributors = useCallback(async (assetId) => {
    try {
      const contributors = await getContributors(assetId);
      setAssetContributors(prev => ({ ...prev, [assetId]: contributors }));
    } catch (err) {
      console.error('Failed to fetch contributors:', err);
    }
  }, []);

  const handleSimulateFailure = (assetId, assetName) => {
    // Navigate to Scenario Studio with pre-filled data
    navigate(`/scenarios?root_asset=${assetId}&name=${encodeURIComponent(`${assetName} Failure Simulation`)}&severity=CRITICAL`);
  };

  const handleSimulateRecovery = (assetId, assetName) => {
    // Navigate to Recovery Studio with pre-filled data
    navigate(`/recovery?root_asset=${assetId}&name=${encodeURIComponent(`${assetName} Recovery`)}`);
  };

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  useEffect(() => {
    if (geojsonData?.features) {
      geojsonData.features.forEach(feature => {
        const assetId = feature.id || feature.properties?.id;
        if (assetId && !sensorCounts[assetId]) {
          fetchSensorCount(assetId);
        }
      });
    }
  }, [geojsonData, sensorCounts, fetchSensorCount]);

  useSystemEvents(
    [
      EVENT_TYPES.EVENT_CREATED,
      EVENT_TYPES.EVENT_RESOLVED,
      EVENT_TYPES.HEALTH_UPDATED,
      EVENT_TYPES.ASSET_UPDATED,
    ],
    () => {
      fetchAllData();
    }
  );

  const getAssetHealthStatus = (assetId) => {
    const health = healthData[assetId];
    return health?.health_status || 'UNKNOWN';
  };

  const getAssetHealthScore = (assetId) => {
    const health = healthData[assetId];
    return health?.health_score;
  };

  const getAssetEventCount = (assetId) => {
    const health = healthData[assetId];
    return health?.active_event_count || 0;
  };

  const getAssetEvents = (assetId) => {
    return events.filter(e => e.asset_id === assetId);
  };

  const toggleLayer = (layerName) => {
    setLayers(prev => ({ ...prev, [layerName]: !prev[layerName] }));
  };

  const getHealthColorOptions = (assetId) => {
    const status = getAssetHealthStatus(assetId);
    return HEALTH_COLORS[status] || HEALTH_COLORS.UNKNOWN;
  };

  const getEventSeverityCounts = (assetId) => {
    const assetEvents = getAssetEvents(assetId);
    return {
      WARNING: assetEvents.filter(e => e.severity === 'WARNING').length,
      CRITICAL: assetEvents.filter(e => e.severity === 'CRITICAL').length,
    };
  };

  const eventSummary = events.reduce(
    (acc, e) => {
      if (e.severity === 'WARNING') acc.WARNING++;
      if (e.severity === 'CRITICAL') acc.CRITICAL++;
      return acc;
    },
    { WARNING: 0, CRITICAL: 0 }
  );

  if (loading) {
    return <div className="loading">Loading GeoPortal data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="geoportal-container">
      <div className="geoportal-sidebar">
        <h2>GeoPortal</h2>
        <p className="subtitle">Operational Intelligence Dashboard</p>

        <div className="layer-toggles">
          <h3>Layers</h3>
          <label className="layer-toggle">
            <input
              type="checkbox"
              checked={layers.assets}
              onChange={() => toggleLayer('assets')}
            />
            <span className="toggle-indicator" style={{ backgroundColor: '#22c55e' }}></span>
            Assets
          </label>
          <label className="layer-toggle">
            <input
              type="checkbox"
              checked={layers.events}
              onChange={() => toggleLayer('events')}
            />
            <span className="toggle-indicator" style={{ backgroundColor: '#ef4444' }}></span>
            Events
          </label>
          <label className="layer-toggle">
            <input
              type="checkbox"
              checked={layers.sensors}
              onChange={() => toggleLayer('sensors')}
            />
            <span className="toggle-indicator" style={{ backgroundColor: '#3b82f6' }}></span>
            Sensors
          </label>
        </div>

        <div className="summary-cards">
          <h3>Summary</h3>
          <div className="summary-card">
            <span className="card-value">{events.length}</span>
            <span className="card-label">Active Events</span>
          </div>
          <div className="summary-card warning">
            <span className="card-value">{eventSummary.WARNING}</span>
            <span className="card-label">Warnings</span>
          </div>
          <div className="summary-card critical">
            <span className="card-value">{eventSummary.CRITICAL}</span>
            <span className="card-label">Critical</span>
          </div>
          <div className="summary-card healthy">
            <span className="card-value">
              {Object.values(healthData).filter(h => h.health_status === 'HEALTHY').length}
            </span>
            <span className="card-label">Healthy</span>
          </div>
        </div>

        <div className="legend">
          <h3>Legend</h3>
          <div className="legend-item">
            <span className="legend-color healthy"></span>
            <span>Healthy (80-100)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color degraded"></span>
            <span>Degraded (40-79)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color critical"></span>
            <span>Critical (0-39)</span>
          </div>
          <div className="legend-item event-warning">
            <span className="legend-pulse warning"></span>
            <span>Warning Event</span>
          </div>
          <div className="legend-item event-critical">
            <span className="legend-pulse critical"></span>
            <span>Critical Event</span>
          </div>
        </div>

        <button onClick={fetchAllData} className="refresh-button">
          Refresh Data
        </button>
      </div>

      <div className="geoportal-map">
        <MapContainer
          ref={mapRef}
          center={[-22.3285, 24.6849]}
          zoom={6}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {layers.assets && geojsonData?.features?.map((feature) => {
            if (!feature.geometry?.coordinates) return null;
            const [lng, lat] = feature.geometry.coordinates;
            const { name, asset_type, status } = feature.properties;
            const assetId = feature.id || feature.properties?.id;
            const healthColor = getHealthColorOptions(assetId);
            const healthScore = getAssetHealthScore(assetId);
            const eventCount = getAssetEventCount(assetId);
            const sensorCount = sensorCounts[assetId] || 0;
            const severityCounts = getEventSeverityCounts(assetId);

            return (
              <CircleMarker
                key={`asset-${assetId}`}
                center={[lat, lng]}
                radius={10}
                pathOptions={{
                  color: healthColor.color,
                  fillColor: healthColor.fillColor,
                  fillOpacity: 0.7,
                  weight: 2,
                }}
              >
                <Popup>
                  <div className="asset-popup">
                    <h3>{name}</h3>
                    <p className="asset-type">{asset_type}</p>
                    
                    <div className="popup-section">
                      <strong>Health Status</strong>
                      <div className={`health-badge ${getAssetHealthStatus(assetId).toLowerCase()}`}>
                        {getAssetHealthStatus(assetId)}
                        {healthScore !== undefined && (
                          <span className="score"> ({healthScore})</span>
                        )}
                      </div>
                    </div>

                    <div className="popup-section">
                      <strong>Asset Info</strong>
                      <p>Status: {status}</p>
                      <p>Sensors: {sensorCount}</p>
                    </div>

                    <div className="popup-section">
                      <button
                        className="simulate-button"
                        onClick={() => handleSimulateFailure(assetId, name)}
                      >
                        ⚡ Simulate Failure
                      </button>
                      <button
                        className="recover-button"
                        onClick={() => handleSimulateRecovery(assetId, name)}
                      >
                        🔧 Simulate Recovery
                      </button>
                    </div>

                    {eventCount > 0 && (
                      <div className="popup-section">
                        <strong>Active Events ({eventCount})</strong>
                        {severityCounts.WARNING > 0 && (
                          <p className="event-count warning">
                            ⚠ Warning: {severityCounts.WARNING}
                          </p>
                        )}
                        {severityCounts.CRITICAL > 0 && (
                          <p className="event-count critical">
                            🔴 Critical: {severityCounts.CRITICAL}
                          </p>
                        )}
                      </div>
                    )}

                    <div className="popup-section">
                      <button 
                        className="impact-button"
                        onClick={() => fetchAssetImpacts(assetId)}
                      >
                        Load Dependency Impact
                      </button>
                      
                      {assetImpacts[assetId] && assetImpacts[assetId].length > 0 && (
                        <div className="dependency-impact">
                          <strong>Dependency Impact ({assetImpacts[assetId].length})</strong>
                          {assetImpacts[assetId].slice(0, 3).map((impact, idx) => (
                            <div key={idx} className="impact-item">
                              <span 
                                className="severity-dot"
                                style={{ backgroundColor: PROPAGATION_COLORS[impact.propagation_type] || '#6b7280' }}
                              ></span>
                              <span className="impact-source">{impact.source_asset_name}</span>
                              <span className={`impact-severity ${impact.severity.toLowerCase()}`}>
                                {impact.severity}
                              </span>
                              <span className="impact-depth">Depth {impact.depth}</span>
                            </div>
                          ))}
                          {assetImpacts[assetId].length > 3 && (
                            <p className="more-impacts">
                              +{assetImpacts[assetId].length - 3} more impacts
                            </p>
                          )}
                        </div>
                      )}

                      {healthData[assetId] && healthData[assetId].dependency_penalty > 0 && (
                        <div className="health-contributors">
                          <strong>Health Contributors</strong>
                          <p className="current-health">
                            Current Health: <span style={{ color: getHealthColor(healthData[assetId].health_score) }}>
                              {healthData[assetId].health_score}
                            </span>
                            <span className="dep-penalty">
                              (-{healthData[assetId].dependency_penalty.toFixed(1)} from dependencies)
                            </span>
                          </p>
                          <button 
                            className="contributors-button"
                            onClick={() => fetchAssetContributors(assetId)}
                          >
                            Load Contributors
                          </button>
                          
                          {assetContributors[assetId] && assetContributors[assetId].contributors && (
                            <div className="contributors-list">
                              {assetContributors[assetId].contributors.slice(0, 5).map((contrib, idx) => (
                                <div key={idx} className="contributor-item">
                                  <span 
                                    className="contributor-dot"
                                    style={{ backgroundColor: getHealthColor(contrib.health_score) }}
                                  ></span>
                                  <span className="contributor-name">{contrib.asset_name}</span>
                                  <span className={`contributor-severity ${contrib.health_status.toLowerCase()}`}>
                                    {contrib.health_status}
                                  </span>
                                  <span className="contributor-penalty">-{contrib.penalty.toFixed(1)}</span>
                                </div>
                              ))}
                              {assetContributors[assetId].contributors.length > 5 && (
                                <p className="more-contributors">
                                  +{assetContributors[assetId].contributors.length - 5} more
                                </p>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}

          {layers.events && events.map((event) => {
            if (!geojsonData?.features) return null;
            const assetFeature = geojsonData.features.find(
              f => (f.id || f.properties?.id) === event.asset_id
            );
            if (!assetFeature?.geometry?.coordinates) return null;
            
            const [lng, lat] = assetFeature.geometry.coordinates;
            const color = SEVERITY_COLORS[event.severity] || '#6b7280';

            return (
              <CircleMarker
                key={`event-${event.id}`}
                center={[lat, lng]}
                radius={15}
                pathOptions={{
                  color: color,
                  fillColor: color,
                  fillOpacity: 0,
                  weight: 3,
                  className: `pulsing-marker ${event.severity.toLowerCase()}`,
                }}
              >
                <Popup>
                  <div className="event-popup">
                    <h3>Event</h3>
                    <p className={`severity ${event.severity.toLowerCase()}`}>
                      {event.severity}
                    </p>
                    <p className="message">{event.message}</p>
                    <p className="timestamp">
                      {new Date(event.timestamp).toLocaleString()}
                    </p>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}

export default GeoPortal;