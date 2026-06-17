import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getSensor } from '../api/sensors';
import { getThresholdsBySensor } from '../api/thresholds';

function SensorThresholds() {
  const { id } = useParams();
  const [sensor, setSensor] = useState(null);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, [id]);

  async function loadData() {
    try {
      setLoading(true);
      const [sensorData, rulesData] = await Promise.all([
        getSensor(id),
        getThresholdsBySensor(id).then(data => data.items),
      ]);
      setSensor(sensorData);
      setRules(rulesData);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className="loading">Loading...</div>;
  if (error && !sensor) return <div className="error">{error}</div>;

  return (
    <div>
      <h2>
        Threshold Rules for{' '}
        <Link to={`/sensors/${id}`}>{sensor?.name || id}</Link>
      </h2>
      
      {sensor && (
        <div className="sensor-info">
          <p>Type: {sensor.sensor_type} | Unit: {sensor.unit || 'N/A'}</p>
        </div>
      )}
      
      <div className="page-header">
        <Link to={`/thresholds/create?sensor_id=${id}`}>
          <button>Create Rule for This Sensor</button>
        </Link>
      </div>
      
      {error && <div className="error">{error}</div>}
      
      {rules.length === 0 ? (
        <p>No threshold rules found for this sensor.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Warning Range</th>
              <th>Critical Range</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rules.map((rule) => (
              <tr key={rule.id}>
                <td>{rule.name}</td>
                <td>
                  {rule.warning_min !== null && rule.warning_max !== null
                    ? `${rule.warning_min} - ${rule.warning_max}`
                    : 'Not set'}
                </td>
                <td>
                  {rule.critical_min !== null && rule.critical_max !== null
                    ? `${rule.critical_min} - ${rule.critical_max}`
                    : 'Not set'}
                </td>
                <td>
                  {rule.is_active ? (
                    <span className="status-badge active">Active</span>
                  ) : (
                    <span className="status-badge inactive">Inactive</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default SensorThresholds;