import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAssets, deleteAsset } from '../api/assets';

function AssetList() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAssets();
  }, []);

  async function fetchAssets() {
    try {
      setLoading(true);
      const data = await getAssets();
      setAssets(data.items || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Are you sure you want to delete this asset?')) return;
    try {
      await deleteAsset(id);
      fetchAssets();
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) return <div className="loading">Loading assets...</div>;

  return (
    <div>
      <div className="header-actions">
        <Link to="/assets/create">
          <button>Create New Asset</button>
        </Link>
      </div>

      {error && <div className="error">{error}</div>}

      {assets.length === 0 ? (
        <p>No assets found. Create your first asset!</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Status</th>
              <th>Location</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {assets.map((asset) => (
              <tr key={asset.id}>
                <td>{asset.name}</td>
                <td>{asset.asset_type}</td>
                <td>{asset.status}</td>
                <td>
                  {asset.latitude && asset.longitude
                    ? `${asset.latitude}, ${asset.longitude}`
                    : 'N/A'}
                </td>
                <td className="actions">
                  <Link to={`/assets/${asset.id}`}>
                    <button>View</button>
                  </Link>
                  <button
                    className="danger"
                    onClick={() => handleDelete(asset.id)}
                  >
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

export default AssetList;
