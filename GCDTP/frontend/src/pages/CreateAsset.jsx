import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createAsset } from '../api/assets';

function CreateAsset() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    asset_type: '',
    description: '',
    longitude: '',
    latitude: '',
    status: 'active',
  });

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      const data = {
        ...formData,
        longitude: formData.longitude ? parseFloat(formData.longitude) : null,
        latitude: formData.latitude ? parseFloat(formData.latitude) : null,
      };
      await createAsset(data);
      navigate('/assets');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>Create New Asset</h2>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit}>
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
          <label>Asset Type *</label>
          <input
            type="text"
            name="asset_type"
            value={formData.asset_type}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows="3"
          />
        </div>

        <div className="form-group">
          <label>Latitude</label>
          <input
            type="number"
            step="any"
            name="latitude"
            value={formData.latitude}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label>Longitude</label>
          <input
            type="number"
            step="any"
            name="longitude"
            value={formData.longitude}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label>Status</label>
          <select name="status" value={formData.status} onChange={handleChange}>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="maintenance">Maintenance</option>
            <option value="retired">Retired</option>
          </select>
        </div>

        <div className="actions">
          <button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Asset'}
          </button>
          <button type="button" onClick={() => navigate('/assets')}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export default CreateAsset;
