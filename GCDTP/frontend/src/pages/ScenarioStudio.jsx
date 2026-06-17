import React, { useState, useEffect, useCallback } from 'react';
import {
  createScenario,
  runScenario,
  getScenario,
  getResults,
  getImpactTree,
  compareScenario,
  deleteScenario,
  getHealthColor,
  getDeltaColor,
  formatDelta,
  SCENARIO_TYPES,
  SEVERITY_LEVELS,
} from '../api/scenarios';
import { getAssets } from '../api/assets';
import ScenarioImpactTree from '../components/ScenarioImpactTree';
import './ScenarioStudio.css';


/**
 * Scenario Studio page component
 * 
 * Three-panel layout:
 * - Left: Scenario Builder
 * - Center: Impact Results
 * - Right: Statistics
 */
function ScenarioStudio() {
  // Asset data
  const [assets, setAssets] = useState([]);
  
  // Scenario state
  const [scenarios, setScenarios] = useState([]);
  const [currentScenario, setCurrentScenario] = useState(null);
  
  // Form state
  const [scenarioName, setScenarioName] = useState('');
  const [scenarioDescription, setScenarioDescription] = useState('');
  const [scenarioType, setScenarioType] = useState(SCENARIO_TYPES.FAILURE);
  const [severity, setSeverity] = useState(SEVERITY_LEVELS.CRITICAL);
  const [rootAssetId, setRootAssetId] = useState('');
  
  // Results state
  const [results, setResults] = useState([]);
  const [impactTree, setImpactTree] = useState(null);
  const [comparison, setComparison] = useState(null);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasRun, setHasRun] = useState(false);

  // Fetch assets
  const fetchAssets = useCallback(async () => {
    try {
      const response = await getAssets({ limit: 1000 });
      setAssets(response.items || []);
    } catch (err) {
      console.error('Failed to fetch assets:', err);
    }
  }, []);

  // Fetch scenarios
  const fetchScenarios = useCallback(async () => {
    try {
      const response = await listScenarios();
      setScenarios(response.items || []);
    } catch (err) {
      console.error('Failed to fetch scenarios:', err);
    }
  }, []);

  useEffect(() => {
    fetchAssets();
    fetchScenarios();
  }, [fetchAssets, fetchScenarios]);

  // Handle scenario creation and run
  const handleRunSimulation = async () => {
    if (!scenarioName.trim()) {
      setError('Please enter a scenario name');
      return;
    }
    if (!rootAssetId) {
      setError('Please select a root asset');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Create scenario
      const scenario = await createScenario({
        name: scenarioName,
        description: scenarioDescription,
        scenario_type: scenarioType,
        root_asset_id: rootAssetId,
        severity: severity,
      });

      setCurrentScenario(scenario);

      // Run simulation
      await runScenario(scenario.id);

      // Fetch results
      const resultsData = await getResults(scenario.id);
      setResults(resultsData.items || []);
      
      // Fetch impact tree
      const treeData = await getImpactTree(scenario.id);
      setImpactTree(treeData);
      
      // Fetch comparison
      const compareData = await compareScenario(scenario.id);
      setComparison(compareData);
      
      setHasRun(true);
      
      // Refresh scenarios list
      fetchScenarios();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle scenario selection
  const handleSelectScenario = async (scenarioId) => {
    setLoading(true);
    setError(null);

    try {
      const scenario = await getScenario(scenarioId);
      setCurrentScenario(scenario);
      setScenarioName(scenario.name);
      setScenarioDescription(scenario.description || '');
      setScenarioType(scenario.scenario_type);
      setSeverity(scenario.severity);
      setRootAssetId(scenario.root_asset_id);

      // Fetch results if completed
      if (scenario.status === 'completed') {
        const resultsData = await getResults(scenarioId);
        setResults(resultsData.items || []);
        
        const treeData = await getImpactTree(scenarioId);
        setImpactTree(treeData);
        
        const compareData = await compareScenario(scenarioId);
        setComparison(compareData);
        
        setHasRun(true);
      } else {
        setResults([]);
        setImpactTree(null);
        setComparison(null);
        setHasRun(false);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    if (!currentScenario) return;

    setLoading(true);
    try {
      await deleteScenario(currentScenario.id);
      setCurrentScenario(null);
      setScenarioName('');
      setScenarioDescription('');
      setScenarioType(SCENARIO_TYPES.FAILURE);
      setSeverity(SEVERITY_LEVELS.CRITICAL);
      setRootAssetId('');
      setResults([]);
      setImpactTree(null);
      setComparison(null);
      setHasRun(false);
      fetchScenarios();
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
        totalAffected: 0,
        worstHealth: 100,
        averageHealth: 100,
        maxDepth: 0,
        totalHealthLoss: 0,
      };
    }

    const predictedHealths = results.map(r => r.predicted_health);
    const deltas = results.map(r => r.delta_health);

    return {
      totalAffected: results.length,
      worstHealth: Math.min(...predictedHealths),
      averageHealth: predictedHealths.reduce((a, b) => a + b, 0) / predictedHealths.length,
      maxDepth: Math.max(...results.map(r => r.propagation_depth)),
      totalHealthLoss: deltas.reduce((a, b) => a + b, 0),
    };
  }, [results]);

  return (
    <div className="scenario-studio">
      <div className="studio-header">
        <h2>Scenario Studio</h2>
        <p className="subtitle">Simulate failures and recoveries without affecting live data</p>
      </div>

      <div className="studio-content">
        {/* Left Panel - Scenario Builder */}
        <div className="panel builder-panel">
          <h3>Scenario Builder</h3>
          
          <div className="form-group">
            <label>Scenario Name</label>
            <input
              type="text"
              value={scenarioName}
              onChange={(e) => setScenarioName(e.target.value)}
              placeholder="e.g., Transformer A Failure"
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              value={scenarioDescription}
              onChange={(e) => setScenarioDescription(e.target.value)}
              placeholder="Describe the scenario..."
              rows={3}
            />
          </div>

          <div className="form-group">
            <label>Root Asset</label>
            <select
              value={rootAssetId}
              onChange={(e) => setRootAssetId(e.target.value)}
            >
              <option value="">-- Select Asset --</option>
              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.name} ({asset.asset_type})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Scenario Type</label>
            <select
              value={scenarioType}
              onChange={(e) => setScenarioType(e.target.value)}
            >
              <option value={SCENARIO_TYPES.FAILURE}>Failure</option>
              <option value={SCENARIO_TYPES.RECOVERY}>Recovery</option>
              <option value={SCENARIO_TYPES.MAINTENANCE}>Maintenance</option>
              <option value={SCENARIO_TYPES.CUSTOM}>Custom</option>
            </select>
          </div>

          <div className="form-group">
            <label>Severity</label>
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
            >
              <option value={SEVERITY_LEVELS.WARNING}>WARNING</option>
              <option value={SEVERITY_LEVELS.CRITICAL}>CRITICAL</option>
            </select>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            className="run-button"
            onClick={handleRunSimulation}
            disabled={loading}
          >
            {loading ? 'Running...' : 'Run Simulation'}
          </button>

          {currentScenario && (
            <button
              className="delete-button"
              onClick={handleDelete}
              disabled={loading}
            >
              Delete Scenario
            </button>
          )}

          <div className="saved-scenarios">
            <h4>Recent Scenarios</h4>
            <ul>
              {scenarios.slice(0, 5).map((s) => (
                <li
                  key={s.id}
                  className={currentScenario?.id === s.id ? 'active' : ''}
                  onClick={() => handleSelectScenario(s.id)}
                >
                  <span className="scenario-name">{s.name}</span>
                  <span className={`status-badge ${s.status}`}>
                    {s.status}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Center Panel - Impact Results */}
        <div className="panel results-panel">
          <h3>Impact Results</h3>
          
          {!hasRun ? (
            <div className="empty-state">
              <p>Run a simulation to see impact results</p>
            </div>
          ) : results.length > 0 ? (
            <>
              <ScenarioImpactTree tree={impactTree} />
              
              <div className="results-table">
                <table>
                  <thead>
                    <tr>
                      <th>Asset</th>
                      <th>Current</th>
                      <th>Predicted</th>
                      <th>Difference</th>
                      <th>Depth</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((result) => (
                      <tr key={result.id}>
                        <td>
                          <span className="asset-name">{result.asset_name}</span>
                          <span className="asset-type">{result.asset_type}</span>
                        </td>
                        <td>
                          <span
                            className="health-badge"
                            style={{ backgroundColor: getHealthColor(result.current_health) }}
                          >
                            {result.current_health.toFixed(0)}
                          </span>
                        </td>
                        <td>
                          <span
                            className="health-badge"
                            style={{ backgroundColor: getHealthColor(result.predicted_health) }}
                          >
                            {result.predicted_health.toFixed(0)}
                          </span>
                        </td>
                        <td>
                          <span
                            className="delta"
                            style={{ color: getDeltaColor(result.delta_health) }}
                          >
                            {formatDelta(result.delta_health)}
                          </span>
                        </td>
                        <td>
                          <span className="depth">{result.propagation_depth}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <p>No affected assets</p>
            </div>
          )}
        </div>

        {/* Right Panel - Statistics */}
        <div className="panel stats-panel">
          <h3>Statistics</h3>
          
          <div className="stat-card">
            <span className="stat-label">Worst Asset</span>
            <span
              className="stat-value health-badge"
              style={{ backgroundColor: getHealthColor(stats.worstHealth) }}
            >
              {stats.worstHealth.toFixed(0)}
            </span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Average Health</span>
            <span
              className="stat-value"
              style={{ color: getHealthColor(stats.averageHealth) }}
            >
              {stats.averageHealth.toFixed(1)}
            </span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Affected Assets</span>
            <span className="stat-value">{stats.totalAffected}</span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Max Depth</span>
            <span className="stat-value">{stats.maxDepth}</span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Health Loss</span>
            <span
              className="stat-value"
              style={{ color: getDeltaColor(stats.totalHealthLoss) }}
            >
              {formatDelta(stats.totalHealthLoss)}
            </span>
          </div>

          {comparison && (
            <div className="comparison-section">
              <h4>Root Asset Comparison</h4>
              <div className="comparison-grid">
                <span>Current:</span>
                <span style={{ color: getHealthColor(comparison.current_health) }}>
                  {comparison.current_health.toFixed(0)}
                </span>
                <span>Predicted:</span>
                <span style={{ color: getDeltaColor(comparison.delta) }}>
                  {(comparison.current_health + comparison.delta).toFixed(0)}
                </span>
                <span>Delta:</span>
                <span style={{ color: getDeltaColor(comparison.delta) }}>
                  {formatDelta(comparison.delta)}
                </span>
              </div>
            </div>
          )}

          <div className="info-section">
            <h4>How It Works</h4>
            <ul>
              <li>Simulation uses virtual events</li>
              <li>No writes to live events table</li>
              <li>Uses existing relationship graph</li>
              <li>Maximum propagation depth: 3</li>
              <li>Results are sandbox-only</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

// Need to import listScenarios
import { listScenarios } from '../api/scenarios';

export default ScenarioStudio;