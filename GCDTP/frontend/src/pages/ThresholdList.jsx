import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getThresholds, deleteThreshold } from '../api/thresholds';

function ThresholdList() {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadRules();
  }, [filter]);

  async function loadRules() {
    try {
      setLoading(true);
      const params = {};
      if (filter === 'active') params.is_active = true;
      if (filter === 'inactive') params.is_active = false;
      
      const data = await getThresholds(params);
      setRules(data.items);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Are you sure you want to delete this rule?')) return;
    try {
      await deleteThreshold(id);
      loadRules();
    } catch (err) {
      setError(err.message);
    }
  }

  function getStatusBadge(rule) {
    return rule.is_active ? (
      <span className="status-badge active">Active</span>
    ) : (
      <span className="status-badge inactive">Inactive</span>
    );
  }

  if (loading) return <div className="loading">Loading threshold rules...</div>;

  return (
    <div>
      <h2>Threshold Rules</h2>
      
      <div className="page-header">
        <div className="filter-group">
          <label>Filter:</label>
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">All Rules</option>
            <option value="active">Active Only</option>
            <option value="inactive">Inactive Only</option>
          </select>
        </div>
        <Link to="/thresholds/create">
          <button>Create New Rule</button>
        </Link>
      </div>
      
      {error && <div className="error">{error}</div>}
      
      {rules.length === 0 ? (
        <p>No threshold rules found.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Sensor</th>
              <th>Warning Range</th>
              <th>Critical Range</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rules.map((rule) => (
              <tr key={rule.id}>
                <td>{rule.name}</td>
                <td>
                  {rule.sensor_id ? (
                    <Link to={`/sensors/${rule.sensor_id}`}>
                      {rule.sensor_id.substring(0, 8)}...
                    </Link>
                  ) : (
                    <span className="global-rule">Global</span>
                  )}
                </td>
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
                <td>{getStatusBadge(rule)}</td>
                <td className="actions">
                  <button className="danger" onClick={() => handleDelete(rule.id)}>
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

export default ThresholdList;