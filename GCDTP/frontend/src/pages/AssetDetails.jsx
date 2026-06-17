import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getAsset, updateAsset } from '../api/assets';

function AssetDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [asset, setAsset] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    asset_type: '',
    description: '',
    longitude: '',
    latitude: '',
    status: '',
  });

  useEffect(() => {
    fetchAsset();
  }, [id]);

  async function fetchAsset() {
    try {
      setLoading(true);
      const data = await getAsset(id);
      setAsset(data);
      setFormData({
        name: data.name,
        asset_type: data.asset_type,
        description: data.description || '',
        longitude: data.longitude || '',
        latitude: data.latitude || '',
        status: data.status,
      });
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

  async function handleSave(e) {
    e.preventDefault();
    try {
      setSaving(true);
      setError(null);
      const data = {
        ...formData,
        longitude: formData.longitude ? parseFloat(formData.longitude) : null,
        latitude: formData.latitude ? parseFloat(formData.latitude) : null,
      };
      await updateAsset(id, data);
      setIsEditing(false);
      fetchAsset();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="loading">Loading asset...</div>;

  if (!asset) return <div className="error">Asset not found</div>;

  return (
    <div>
      <h2>Asset Details</h2>

      {error && <div className="error">{error}</div>}

      {!isEditing ? (
        <div>
          <p><strong>ID:</strong> {asset.id}</p>
          <p><strong>Name:</strong> {asset.name}</p>
          <p><strong>Type:</strong> {asset.asset_type}</p>
          <p><strong>Description:</strong> {asset.description || 'N/A'}</p>
          <p><strong>Latitude:</strong> {asset.latitude || 'N/A'}</p>
          <p><strong>Longitude:</strong> {asset.longitude || 'N/A'}</p>
          <p><strong>Status:</strong> {asset.status}</p>
          <p><strong>Created:</strong> {new Date(asset.created_at).toLocaleString()}</p>
          <p><strong>Updated:</strong> {new Date(asset.updated_at).toLocaleString()}</p>

          <div className="actions" style={{ marginTop: '20px' }}>
            <button onClick={() => setIsEditing(true)}>Edit</button>
            <Link to="/assets">
              <button>Back to List</button>
            </Link>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSave}>
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
            <button type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
            <button type="button" onClick={() => setIsEditing(false)}>
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

export default AssetDetails;
