import React, { useState, useEffect, useCallback } from 'react';
import {
  createRecovery,
  runRecovery,
  getRecovery,
  getResults,
  compareRecovery,
  getRecoveryTree,
  deleteRecovery,
  listRecoveries,
  getHealthColor,
  getRiskColor,
  formatImprovement,
  RECOVERY_TYPES,
} from '../api/recovery';
import RecoveryImpactTree from '../components/RecoveryImpactTree';
import './RecoveryStudio.css';


/**
 * Recovery Studio page component
 * 
 * Three-panel layout:
 * - Left: Recovery Builder
 * - Center: Recovery Results
 * - Right: Statistics
 */
function RecoveryStudio({ scenarioId, onBack }) {
  // Recovery state
  const [recoveries, setRecoveries] = useState([]);
  const [currentRecovery, setCurrentRecovery] = useState(null);
  
  // Form state
  const [strategyName, setStrategyName] = useState('');
  const [recoveryType, setRecoveryType] = useState(RECOVERY_TYPES.MANUAL);
  const [duration, setDuration] = useState(60);
  
  // Results state
  const [results, setResults] = useState([]);
  const [recoveryTree, setRecoveryTree] = useState(null);
  const [comparison, setComparison] = useState(null);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasRun, setHasRun] = useState(false);

  // Fetch recoveries
  const fetchRecoveries = useCallback(async () => {
    try {
      const params = scenarioId ? { scenario_id: scenarioId } : {};
      const response = await listRecoveries(params);
      setRecoveries(response.items || []);
    } catch (err) {
      console.error('Failed to fetch recoveries:', err);
    }
  }, [scenarioId]);

  useEffect(() => {
    fetchRecoveries();
  }, [fetchRecoveries]);

  // Handle recovery creation and run
  const handleRunRecovery = async () => {
    if (!strategyName.trim()) {
      setError('Please enter a strategy name');
      return;
    }
    if (!scenarioId) {
      setError('No scenario selected');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Create recovery
      const recovery = await createRecovery({
        scenario_id: scenarioId,
        strategy_name: strategyName,
        recovery_type: recoveryType,
        estimated_duration_minutes: duration,
      });

      setCurrentRecovery(recovery);

      // Run recovery simulation
      await runRecovery(recovery.id);

      // Fetch results
      const resultsData = await getResults(recovery.id);
      setResults(resultsData.items || []);
      
      // Fetch recovery tree
      const treeData = await getRecoveryTree(recovery.id);
      setRecoveryTree(treeData);
      
      // Fetch comparison
      const compareData = await compareRecovery(recovery.id);
      setComparison(compareData);
      
      setHasRun(true);
      
      // Refresh recoveries list
      fetchRecoveries();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle recovery selection
  const handleSelectRecovery = async (recoveryId) => {
    setLoading(true);
    setError(null);

    try {
      const recovery = await getRecovery(recoveryId);
      setCurrentRecovery(recovery);
      setStrategyName(recovery.strategy_name);
      setRecoveryType(recovery.recovery_type);
      setDuration(recovery.estimated_duration_minutes);

      // Fetch results if completed
      const resultsData = await getResults(recoveryId);
      setResults(resultsData.items || []);
      
      const treeData = await getRecoveryTree(recoveryId);
      setRecoveryTree(treeData);
      
      const compareData = await compareRecovery(recoveryId);
      setComparison(compareData);
      
      setHasRun(results.items && results.items.length > 0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    if (!currentRecovery) return;

    setLoading(true);
    try {
      await deleteRecovery(currentRecovery.id);
      setCurrentRecovery(null);
      setStrategyName('');
      setRecoveryType(RECOVERY_TYPES.MANUAL);
      setDuration(60);
      setResults([]);
      setRecoveryTree(null);
      setComparison(null);
      setHasRun(false);
      fetchRecoveries();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Calculate statistics
  const stats = React.useMemo(() => {
    if (!results.length) {
      return {
        totalAssets: 0,
        assetsRecovered: 0,
        worstRecovery: 100,
        bestRecovery: 0,
        averageImprovement: 0,
        remainingCritical: 0,
      };
    }

    const afterHealths = results.map(r => r.after_health);
    const improvements = results.map(r => r.improvement);

    return {
      totalAssets: results.length,
      assetsRecovered: results.filter(r => r.after_health >= 90).length,
      worstRecovery: Math.min(...afterHealths),
      bestRecovery: Math.max(...afterHealths),
      averageImprovement: improvements.reduce((a, b) => a + b, 0) / improvements.length,
      remainingCritical: results.filter(r => r.remaining_risk === 'HIGH' || r.remaining_risk === 'CRITICAL').length,
    };
  }, [results]);

  return (
    <div className="recovery-studio">
      <div className="studio-header">
        <div className="header-content">
          {onBack && (
            <button onClick={onBack} className="back-button">
              ← Back to Scenarios
            </button>
          )}
          <div>
            <h2>Recovery Studio</h2>
            <p className="subtitle">Simulate recovery strategies for failure scenarios</p>
          </div>
        </div>
      </div>

      <div className="studio-content">
        {/* Left Panel - Recovery Builder */}
        <div className="panel builder-panel">
          <h3>Recovery Builder</h3>
          
          {!scenarioId && (
            <div className="warning-message">
              Select a scenario first to create a recovery
            </div>
          )}
          
          <div className="form-group">
            <label>Strategy Name</label>
            <input
              type="text"
              value={strategyName}
              onChange={(e) => setStrategyName(e.target.value)}
              placeholder="e.g., Transformer A Recovery"
              disabled={!scenarioId}
            />
          </div>

          <div className="form-group">
            <label>Recovery Type</label>
            <select
              value={recoveryType}
              onChange={(e) => setRecoveryType(e.target.value)}
              disabled={!scenarioId}
            >
              <option value={RECOVERY_TYPES.MANUAL}>Manual (+20)</option>
              <option value={RECOVERY_TYPES.AUTOMATIC}>Automatic (+30)</option>
              <option value={RECOVERY_TYPES.STAGED}>Staged (+15 per depth)</option>
              <option value={RECOVERY_TYPES.REROUTE}>Reroute (+25)</option>
            </select>
          </div>

          <div className="form-group">
            <label>Estimated Duration (minutes)</label>
            <input
              type="number"
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value) || 60)}
              min="1"
              disabled={!scenarioId}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            className="run-button"
            onClick={handleRunRecovery}
            disabled={loading || !scenarioId}
          >
            {loading ? 'Running...' : 'Run Recovery'}
          </button>

          {currentRecovery && (
            <button
              className="delete-button"
              onClick={handleDelete}
              disabled={loading}
            >
              Delete Recovery
            </button>
          )}

          <div className="saved-recoveries">
            <h4>Recent Recoveries</h4>
            <ul>
              {recoveries.slice(0, 5).map((r) => (
                <li
                  key={r.id}
                  className={currentRecovery?.id === r.id ? 'active' : ''}
                  onClick={() => handleSelectRecovery(r.id)}
                >
                  <span className="recovery-name">{r.strategy_name}</span>
                  <span className={`type-badge ${r.recovery_type}`}>
                    {r.recovery_type}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Center Panel - Recovery Results */}
        <div className="panel results-panel">
          <h3>Recovery Results</h3>
          
          {!hasRun ? (
            <div className="empty-state">
              <p>Run a recovery simulation to see results</p>
            </div>
          ) : results.length > 0 ? (
            <>
              <RecoveryImpactTree tree={recoveryTree} />
              
              <div className="results-table">
                <table>
                  <thead>
                    <tr>
                      <th>Asset</th>
                      <th>Before</th>
                      <th>After</th>
                      <th>Improvement</th>
                      <th>Risk</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((result) => (
                      <tr key={result.id}>
                        <td>
                          <span className="asset-name">{result.asset_name}</span>
                        </td>
                        <td>
                          <span
                            className="health-badge"
                            style={{ backgroundColor: getHealthColor(result.before_health) }}
                          >
                            {result.before_health.toFixed(0)}
                          </span>
                        </td>
                        <td>
                          <span
                            className="health-badge"
                            style={{ backgroundColor: getHealthColor(result.after_health) }}
                          >
                            {result.after_health.toFixed(0)}
                          </span>
                        </td>
                        <td>
                          <span className="improvement">
                            {formatImprovement(result.improvement)}
                          </span>
                        </td>
                        <td>
                          <span
                            className="risk-badge"
                            style={{ backgroundColor: getRiskColor(result.remaining_risk) }}
                          >
                            {result.remaining_risk}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <p>No recovery results</p>
            </div>
          )}
        </div>

        {/* Right Panel - Statistics */}
        <div className="panel stats-panel">
          <h3>Statistics</h3>
          
          <div className="stat-card">
            <span className="stat-label">Worst Recovery</span>
            <span
              className="stat-value health-badge"
              style={{ backgroundColor: getHealthColor(stats.worstRecovery) }}
            >
              {stats.worstRecovery.toFixed(0)}
            </span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Best Recovery</span>
            <span
              className="stat-value health-badge"
              style={{ backgroundColor: getHealthColor(stats.bestRecovery) }}
            >
              {stats.bestRecovery.toFixed(0)}
            </span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Average Improvement</span>
            <span className="stat-value improvement">
              {formatImprovement(stats.averageImprovement)}
            </span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Assets Recovered</span>
            <span className="stat-value">
              {stats.assetsRecovered}/{stats.totalAssets}
            </span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Remaining Critical</span>
            <span
              className="stat-value"
              style={{ color: stats.remainingCritical > 0 ? '#ef4444' : '#22c55e' }}
            >
              {stats.remainingCritical}
            </span>
          </div>

          {comparison && (
            <div className="comparison-section">
              <h4>Overall Recovery</h4>
              <div className="comparison-grid">
                <span>Before:</span>
                <span style={{ color: getHealthColor(comparison.before_health) }}>
                  {comparison.before_health.toFixed(0)}
                </span>
                <span>After:</span>
                <span style={{ color: getHealthColor(comparison.after_health) }}>
                  {comparison.after_health.toFixed(0)}
                </span>
                <span>Improvement:</span>
                <span className="improvement">
                  {formatImprovement(comparison.improvement)}
                </span>
              </div>
            </div>
          )}

          <div className="info-section">
            <h4>Recovery Types</h4>
            <ul>
              <li><strong>Manual:</strong> +20 per asset</li>
              <li><strong>Automatic:</strong> +30 per asset</li>
              <li><strong>Staged:</strong> +15 per depth</li>
              <li><strong>Reroute:</strong> +25 (path-based)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RecoveryStudio;