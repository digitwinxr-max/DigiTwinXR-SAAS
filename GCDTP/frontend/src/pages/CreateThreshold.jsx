import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { createThreshold, updateThreshold, getThreshold } from '../api/thresholds';
import { getSensors } from '../api/sensors';

function CreateThreshold() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const [formData, setFormData] = useState({
    name: '',
    sensor_id: '',
    rule_type: 'range',
    warning_min: '',
    warning_max: '',
    critical_min: '',
    critical_max: '',
    is_active: true,
  });
  const [sensors, setSensors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSensors();
    if (isEditing) {
      loadRule();
    }
  }, [id]);

  async function loadSensors() {
    try {
      const data = await getSensors();
      setSensors(data.items);
    } catch (err) {
      console.error('Failed to load sensors:', err);
    }
  }

  async function loadRule() {
    try {
      const data = await getThreshold(id);
      setFormData({
        name: data.name || '',
        sensor_id: data.sensor_id || '',
        rule_type: data.rule_type || 'range',
        warning_min: data.warning_min ?? '',
        warning_max: data.warning_max ?? '',
        critical_min: data.critical_min ?? '',
        critical_max: data.critical_max ?? '',
        is_active: data.is_active ?? true,
      });
    } catch (err) {
      setError(err.message);
    }
  }

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        name: formData.name,
        rule_type: formData.rule_type,
        is_active: formData.is_active,
        warning_min: formData.warning_min ? parseFloat(formData.warning_min) : null,
        warning_max: formData.warning_max ? parseFloat(formData.warning_max) : null,
        critical_min: formData.critical_min ? parseFloat(formData.critical_min) : null,
        critical_max: formData.critical_max ? parseFloat(formData.critical_max) : null,
      };

      if (formData.sensor_id) {
        payload.sensor_id = formData.sensor_id;
      }

      if (isEditing) {
        await updateThreshold(id, payload);
      } else {
        await createThreshold(payload);
      }

      navigate('/thresholds');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>{isEditing ? 'Edit Threshold Rule' : 'Create Threshold Rule'}</h2>
      
      {error && <div className="error">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Rule Name *</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            placeholder="e.g., Temperature High Alert"
          />
        </div>

        <div className="form-group">
          <label htmlFor="sensor_id">Sensor (leave empty for global rule)</label>
          <select
            id="sensor_id"
            name="sensor_id"
            value={formData.sensor_id}
            onChange={handleChange}
          >
            <option value="">-- Global Rule (All Sensors) --</option>
            {sensors.map((sensor) => (
              <option key={sensor.id} value={sensor.id}>
                {sensor.name} ({sensor.sensor_type})
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="rule_type">Rule Type</label>
          <select
            id="rule_type"
            name="rule_type"
            value={formData.rule_type}
            onChange={handleChange}
          >
            <option value="range">Range</option>
            <option value="static">Static</option>
          </select>
        </div>

        <fieldset>
          <legend>Warning Thresholds</legend>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="warning_min">Warning Min</label>
              <input
                type="number"
                id="warning_min"
                name="warning_min"
                value={formData.warning_min}
                onChange={handleChange}
                step="any"
                placeholder="e.g., 15"
              />
            </div>
            <div className="form-group">
              <label htmlFor="warning_max">Warning Max</label>
              <input
                type="number"
                id="warning_max"
                name="warning_max"
                value={formData.warning_max}
                onChange={handleChange}
                step="any"
                placeholder="e.g., 30"
              />
            </div>
          </div>
        </fieldset>

        <fieldset>
          <legend>Critical Thresholds</legend>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="critical_min">Critical Min</label>
              <input
                type="number"
                id="critical_min"
                name="critical_min"
                value={formData.critical_min}
                onChange={handleChange}
                step="any"
                placeholder="e.g., 10"
              />
            </div>
            <div className="form-group">
              <label htmlFor="critical_max">Critical Max</label>
              <input
                type="number"
                id="critical_max"
                name="critical_max"
                value={formData.critical_max}
                onChange={handleChange}
                step="any"
                placeholder="e.g., 35"
              />
            </div>
          </div>
        </fieldset>

        <div className="form-group checkbox">
          <label>
            <input
              type="checkbox"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
            />
            Active
          </label>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading}>
            {loading ? 'Saving...' : isEditing ? 'Update Rule' : 'Create Rule'}
          </button>
          <Link to="/thresholds">
            <button type="button">Cancel</button>
          </Link>
        </div>
      </form>
    </div>
  );
}

export default CreateThreshold;