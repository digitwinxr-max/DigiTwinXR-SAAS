import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getSensor, updateSensor, deleteSensor } from '../api/sensors';
import { getAssets } from '../api/assets';

const SENSOR_TYPES = [
  'temperature',
  'pressure',
  'humidity',
  'vibration',
  'flow',
  'voltage',
];

const STATUS_OPTIONS = ['active', 'inactive', 'maintenance'];

function SensorDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [sensor, setSensor] = useState(null);
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    asset_id: '',
    name: '',
    sensor_type: 'temperature',
    unit: '',
    description: '',
    status: 'active',
  });

  useEffect(() => {
    loadSensor();
    loadAssets();
  }, [id]);

  async function loadSensor() {
    try {
      setLoading(true);
      const data = await getSensor(id);
      setSensor(data);
      setFormData({
        asset_id: data.asset_id,
        name: data.name,
        sensor_type: data.sensor_type,
        unit: data.unit || '',
        description: data.description || '',
        status: data.status,
      });
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadAssets() {
    try {
      const data = await getAssets();
      setAssets(data.items);
    } catch (err) {
      // Ignore asset load errors
    }
  }

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  async function handleUpdate(e) {
    e.preventDefault();
    try {
      setError(null);
      await updateSensor(id, formData);
      setEditing(false);
      loadSensor();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete() {
    if (!window.confirm('Are you sure you want to delete this sensor?')) return;
    try {
      await deleteSensor(id);
      navigate('/sensors');
    } catch (err) {
      setError(err.message);
    }
  }

  function cancelEdit() {
    setEditing(false);
    if (sensor) {
      setFormData({
        asset_id: sensor.asset_id,
        name: sensor.name,
        sensor_type: sensor.sensor_type,
        unit: sensor.unit || '',
        description: sensor.description || '',
        status: sensor.status,
      });
    }
  }

  if (loading) return <div className="loading">Loading...</div>;
  if (error && !sensor) return <div className="error">{error}</div>;

  return (
    <div>
      <h2>Sensor Details</h2>
      
      {error && <div className="error">{error}</div>}
      
      {!editing ? (
        <div className="sensor-detail">
          <div className="info-row">
            <span className="label">Name:</span> {sensor.name}
          </div>
          <div className="info-row">
            <span className="label">Type:</span> {sensor.sensor_type}
          </div>
          <div className="info-row">
            <span className="label">Unit:</span> {sensor.unit || '-'}
          </div>
          <div className="info-row">
            <span className="label">Status:</span> {sensor.status}
          </div>
          <div className="info-row">
            <span className="label">Description:</span> {sensor.description || '-'}
          </div>
          <div className="info-row">
            <span className="label">Asset:</span>{' '}
            <Link to={`/assets/${sensor.asset_id}`}>
              {sensor.asset_id}
            </Link>
          </div>
          <div className="info-row">
            <span className="label">Created:</span> {new Date(sensor.created_at).toLocaleString()}
          </div>
          <div className="info-row">
            <span className="label">Updated:</span> {new Date(sensor.updated_at).toLocaleString()}
          </div>
          
          <div className="actions">
            <button onClick={() => setEditing(true)}>Edit</button>
            <Link to={`/sensors/${sensor.id}/measurements`}>
              <button>View Measurements</button>
            </Link>
            <Link to={`/sensors/${sensor.id}/thresholds`}>
              <button>View Thresholds</button>
            </Link>
            <button className="danger" onClick={handleDelete}>Delete</button>
            <Link to="/sensors">
              <button>Back</button>
            </Link>
          </div>
        </div>
      ) : (
        <form onSubmit={handleUpdate}>
          <div className="form-group">
            <label>Asset *</label>
            <select
              name="asset_id"
              value={formData.asset_id}
              onChange={handleChange}
              required
            >
              <option value="">Select an asset...</option>
              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.name} ({asset.asset_type})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Sensor Type *</label>
            <select
              name="sensor_type"
              value={formData.sensor_type}
              onChange={handleChange}
              required
            >
              {SENSOR_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Unit</label>
            <input
              type="text"
              name="unit"
              value={formData.unit}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
            >
              {STATUS_OPTIONS.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </div>

          <button type="submit">Update</button>
          <button type="button" onClick={cancelEdit} style={{ marginLeft: '10px' }}>
            Cancel
          </button>
        </form>
      )}
    </div>
  );
}

export default SensorDetails;
