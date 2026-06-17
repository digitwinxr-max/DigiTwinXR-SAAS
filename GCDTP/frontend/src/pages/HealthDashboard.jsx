import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getHealthSummary, getAllAssetHealth } from '../api/health';

function HealthDashboard() {
  const [summary, setSummary] = useState(null);
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  async function loadData() {
    try {
      setLoading(true);
      const [summaryData, assetsData] = await Promise.all([
        getHealthSummary(),
        getAllAssetHealth(statusFilter !== 'all' ? { status: statusFilter } : {}),
      ]);
      setSummary(summaryData);
      setAssets(assetsData.items);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function getStatusClass(status) {
    switch (status) {
      case 'HEALTHY': return 'status-healthy';
      case 'DEGRADED': return 'status-degraded';
      case 'CRITICAL': return 'status-critical';
      default: return '';
    }
  }

  function getScoreClass(score) {
    if (score >= 80) return 'score-healthy';
    if (score >= 40) return 'score-degraded';
    return 'score-critical';
  }

  if (loading) return <div className="loading">Loading health data...</div>;

  return (
    <div>
      <h2>Health Dashboard</h2>
      
      {error && <div className="error">{error}</div>}
      
      {summary && (
        <div className="health-summary">
          <div className="summary-card healthy">
            <span className="count">{summary.healthy_count}</span>
            <span className="label">Healthy</span>
          </div>
          <div className="summary-card degraded">
            <span className="count">{summary.degraded_count}</span>
            <span className="label">Degraded</span>
          </div>
          <div className="summary-card critical">
            <span className="count">{summary.critical_count}</span>
            <span className="label">Critical</span>
          </div>
          <div className="summary-card total">
            <span className="count">{summary.total_assets}</span>
            <span className="label">Total Assets</span>
          </div>
          <div className="summary-card avg">
            <span className="count">{summary.average_health_score}</span>
            <span className="label">Avg Score</span>
          </div>
        </div>
      )}
      
      <div className="page-header">
        <div className="filter-group">
          <label>Filter by Status:</label>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="all">All Statuses</option>
            <option value="HEALTHY">Healthy</option>
            <option value="DEGRADED">Degraded</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
      </div>
      
      {assets.length === 0 ? (
        <p>No asset health records found.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Asset Name</th>
              <th>Asset Type</th>
              <th>Health Score</th>
              <th>Status</th>
              <th>Active Events</th>
              <th>Last Updated</th>
            </tr>
          </thead>
          <tbody>
            {assets.map((asset) => (
              <tr key={asset.asset_id}>
                <td>
                  <Link to={`/assets/${asset.asset_id}`}>
                    {asset.asset_name || asset.asset_id}
                  </Link>
                </td>
                <td>{asset.asset_type || 'N/A'}</td>
                <td>
                  <span className={`score ${getScoreClass(asset.health_score)}`}>
                    {asset.health_score}
                  </span>
                </td>
                <td>
                  <span className={`status-badge ${getStatusClass(asset.health_status)}`}>
                    {asset.health_status}
                  </span>
                </td>
                <td>{asset.active_event_count}</td>
                <td>{new Date(asset.last_updated).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default HealthDashboard;