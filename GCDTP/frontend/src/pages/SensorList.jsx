import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getSensors, deleteSensor } from '../api/sensors';

function SensorList() {
  const [sensors, setSensors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSensors();
  }, []);

  async function loadSensors() {
    try {
      setLoading(true);
      const data = await getSensors();
      setSensors(data.items);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Are you sure you want to delete this sensor?')) return;
    try {
      await deleteSensor(id);
      loadSensors();
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) return <div className="loading">Loading sensors...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div>
      <h2>Sensors</h2>
      <Link to="/sensors/create">
        <button>Add Sensor</button>
      </Link>
      
      {sensors.length === 0 ? (
        <p>No sensors found.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Unit</th>
              <th>Status</th>
              <th>Asset ID</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sensors.map((sensor) => (
              <tr key={sensor.id}>
                <td>{sensor.name}</td>
                <td>{sensor.sensor_type}</td>
                <td>{sensor.unit || '-'}</td>
                <td>{sensor.status}</td>
                <td>
                  <Link to={`/assets/${sensor.asset_id}`}>
                    {sensor.asset_id.substring(0, 8)}...
                  </Link>
                </td>
                <td className="actions">
                  <Link to={`/sensors/${sensor.id}`}>
                    <button>View</button>
                  </Link>
                  <button className="danger" onClick={() => handleDelete(sensor.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default SensorList;
