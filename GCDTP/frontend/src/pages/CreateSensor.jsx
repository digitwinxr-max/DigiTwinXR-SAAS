import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { createSensor } from '../api/sensors';
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

function CreateSensor() {
  const navigate = useNavigate();
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
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
    loadAssets();
  }, []);

  async function loadAssets() {
    try {
      setLoading(true);
      const data = await getAssets();
      setAssets(data.items);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      setError(null);
      await createSensor(formData);
      navigate('/sensors');
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div>
      <h2>Create Sensor</h2>
      
      {error && <div className="error">{error}</div>}
      
      <form onSubmit={handleSubmit}>
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
            placeholder="e.g., °C, Pa, %, V"
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

        <button type="submit">Create Sensor</button>
        <Link to="/sensors">
          <button type="button" style={{ marginLeft: '10px' }}>Cancel</button>
        </Link>
      </form>
    </div>
  );
}

export default CreateSensor;
