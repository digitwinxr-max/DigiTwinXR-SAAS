/**
 * API client for Scenario Simulation Engine
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';


/**
 * Scenario types
 */
export const SCENARIO_TYPES = {
  FAILURE: 'failure',
  RECOVERY: 'recovery',
  MAINTENANCE: 'maintenance',
  CUSTOM: 'custom',
};


/**
 * Severity levels
 */
export const SEVERITY_LEVELS = {
  WARNING: 'WARNING',
  CRITICAL: 'CRITICAL',
};


/**
 * Get health color based on score
 * @param {number} score - Health score
 * @returns {string} Hex color
 */
export function getHealthColor(score) {
  if (score >= 80) return '#22c55e'; // HEALTHY - green
  if (score >= 40) return '#f97316'; // DEGRADED - orange
  return '#ef4444'; // CRITICAL - red
}


/**
 * Get health status from score
 * @param {number} score - Health score
 * @returns {string} Health status
 */
export function getHealthStatus(score) {
  if (score >= 80) return 'HEALTHY';
  if (score >= 40) return 'DEGRADED';
  return 'CRITICAL';
}


/**
 * Create a new scenario
 * @param {Object} data - Scenario data
 * @returns {Promise<Object>} Created scenario
 */
export async function createScenario(data) {
  const response = await fetch(`${API_BASE_URL}/scenarios`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to create scenario: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get a specific scenario
 * @param {string} scenarioId - Scenario ID
 * @returns {Promise<Object>} Scenario
 */
export async function getScenario(scenarioId) {
  const response = await fetch(`${API_BASE_URL}/scenarios/${scenarioId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get scenario: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * List all scenarios
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Scenarios list
 */
export async function listScenarios(params = {}) {
  const searchParams = new URLSearchParams();
  
  if (params.skip) searchParams.append('skip', params.skip);
  if (params.limit) searchParams.append('limit', params.limit);
  if (params.status) searchParams.append('status', params.status);
  if (params.scenario_type) searchParams.append('scenario_type', params.scenario_type);
  
  const response = await fetch(
    `${API_BASE_URL}/scenarios?${searchParams.toString()}`
  );
  
  if (!response.ok) {
    throw new Error(`Failed to list scenarios: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Delete a scenario
 * @param {string} scenarioId - Scenario ID
 * @returns {Promise<void>}
 */
export async function deleteScenario(scenarioId) {
  const response = await fetch(`${API_BASE_URL}/scenarios/${scenarioId}`, {
    method: 'DELETE',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to delete scenario: ${response.statusText}`);
  }
}


/**
 * Run a simulation for a scenario
 * @param {string} scenarioId - Scenario ID
 * @returns {Promise<Object>} Simulation results
 */
export async function runScenario(scenarioId) {
  const response = await fetch(`${API_BASE_URL}/scenarios/${scenarioId}/run`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to run simulation: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get results for a scenario
 * @param {string} scenarioId - Scenario ID
 * @returns {Promise<Object>} Results
 */
export async function getResults(scenarioId) {
  const response = await fetch(`${API_BASE_URL}/scenarios/${scenarioId}/results`);
  
  if (!response.ok) {
    throw new Error(`Failed to get results: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get impact tree for a scenario
 * @param {string} scenarioId - Scenario ID
 * @returns {Promise<Object>} Impact tree
 */
export async function getImpactTree(scenarioId) {
  const response = await fetch(`${API_BASE_URL}/scenarios/${scenarioId}/impact-tree`);
  
  if (!response.ok) {
    throw new Error(`Failed to get impact tree: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Compare simulation with live health
 * @param {string} scenarioId - Scenario ID
 * @returns {Promise<Object>} Comparison
 */
export async function compareScenario(scenarioId) {
  const response = await fetch(`${API_BASE_URL}/scenarios/${scenarioId}/compare`);
  
  if (!response.ok) {
    throw new Error(`Failed to compare scenario: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get scenario summary
 * @param {string} scenarioId - Scenario ID
 * @returns {Promise<Object>} Summary
 */
export async function getScenarioSummary(scenarioId) {
  const response = await fetch(`${API_BASE_URL}/scenarios/${scenarioId}/summary`);
  
  if (!response.ok) {
    throw new Error(`Failed to get summary: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get health delta color
 * @param {number} delta - Health delta
 * @returns {string} Hex color
 */
export function getDeltaColor(delta) {
  if (delta >= 0) return '#22c55e'; // Green for no change or improvement
  if (delta >= -20) return '#f97316'; // Orange for moderate
  return '#ef4444'; // Red for severe
}


/**
 * Format delta for display
 * @param {number} delta - Health delta
 * @returns {string} Formatted string
 */
export function formatDelta(delta) {
  const prefix = delta >= 0 ? '+' : '';
  return `${prefix}${delta.toFixed(1)}`;
}


export default {
  createScenario,
  getScenario,
  listScenarios,
  deleteScenario,
  runScenario,
  getResults,
  getImpactTree,
  compareScenario,
  getScenarioSummary,
  getHealthColor,
  getHealthStatus,
  getDeltaColor,
  formatDelta,
  SCENARIO_TYPES,
  SEVERITY_LEVELS,
};