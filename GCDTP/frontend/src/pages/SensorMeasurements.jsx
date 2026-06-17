import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getSensor } from '../api/sensors';
import { getMeasurementsBySensor, deleteMeasurement } from '../api/measurements';
import MeasurementChart from '../components/MeasurementChart';

function SensorMeasurements() {
  const { id } = useParams();
  const [sensor, setSensor] = useState(null);
  const [measurements, setMeasurements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [limit, setLimit] = useState(100);
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');

  useEffect(() => {
    loadData();
  }, [id]);

  async function loadData() {
    try {
      setLoading(true);
      const [sensorData, measurementData] = await Promise.all([
        getSensor(id),
        loadMeasurements(),
      ]);
      setSensor(sensorData);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadMeasurements() {
    const params = { limit };
    if (startTime) params.start_time = startTime;
    if (endTime) params.end_time = endTime;
    const data = await getMeasurementsBySensor(id, params);
    setMeasurements(data.items);
    return data;
  }

  function handleFilter(e) {
    e.preventDefault();
    loadMeasurements();
  }

  async function handleDelete(measurementId) {
    if (!window.confirm('Are you sure you want to delete this measurement?')) return;
    try {
      await deleteMeasurement(measurementId);
      loadMeasurements();
    } catch (err) {
      setError(err.message);
    }
  }

  function getQualityClass(quality) {
    switch (quality) {
      case 'good': return 'quality-good';
      case 'uncertain': return 'quality-uncertain';
      case 'bad': return 'quality-bad';
      default: return '';
    }
  }

  if (loading) return <div className="loading">Loading...</div>;
  if (error && !sensor) return <div className="error">{error}</div>;

  return (
    <div>
      <h2>
        Measurements for{' '}
        <Link to={`/sensors/${id}`}>{sensor?.name || id}</Link>
      </h2>
      
      {sensor && (
        <div className="sensor-info">
          <p>Type: {sensor.sensor_type} | Unit: {sensor.unit || 'N/A'}</p>
        </div>
      )}
      
      <form className="filter-form" onSubmit={handleFilter}>
        <div className="filter-row">
          <label>
            Limit:
            <select value={limit} onChange={(e) => setLimit(e.target.value)}>
              <option value="50">50</option>
              <option value="100">100</option>
              <option value="500">500</option>
              <option value="1000">1000</option>
            </select>
          </label>
          <label>
            Start Time:
            <input
              type="datetime-local"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
            />
          </label>
          <label>
            End Time:
            <input
              type="datetime-local"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
            />
          </label>
          <button type="submit">Apply Filters</button>
        </div>
      </form>
      
      {error && <div className="error">{error}</div>}
      
      <h3>Chart</h3>
      <MeasurementChart data={measurements} unit={sensor?.unit} />
      
      <h3>Data Table</h3>
      {measurements.length === 0 ? (
        <p>No measurements found.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Value</th>
              <th>Quality</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {measurements.map((measurement) => (
              <tr key={measurement.id}>
                <td>{new Date(measurement.timestamp).toLocaleString()}</td>
                <td>{measurement.value}</td>
                <td>
                  <span className={`quality-badge ${getQualityClass(measurement.quality)}`}>
                    {measurement.quality}
                  </span>
                </td>
                <td className="actions">
                  <button className="danger" onClick={() => handleDelete(measurement.id)}>
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

export default SensorMeasurements;
