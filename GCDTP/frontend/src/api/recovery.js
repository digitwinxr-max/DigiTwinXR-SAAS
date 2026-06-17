/**
 * API client for Recovery Simulation Engine
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';


/**
 * Recovery types
 */
export const RECOVERY_TYPES = {
  MANUAL: 'manual',
  AUTOMATIC: 'automatic',
  STAGED: 'staged',
  REROUTE: 'reroute',
};


/**
 * Risk levels
 */
export const RISK_LEVELS = {
  NONE: 'NONE',
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
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
 * Get risk color
 * @param {string} risk - Risk level
 * @returns {string} Hex color
 */
export function getRiskColor(risk) {
  const colors = {
    NONE: '#22c55e',
    LOW: '#84cc16',
    MEDIUM: '#eab308',
    HIGH: '#f97316',
    CRITICAL: '#ef4444',
  };
  return colors[risk] || '#6b7280';
}


/**
 * Get recovery type info
 * @param {string} type - Recovery type
 * @returns {Object} Type info
 */
export function getRecoveryTypeInfo(type) {
  const info = {
    manual: { label: 'Manual', recovery: 20, description: 'Manual intervention' },
    automatic: { label: 'Automatic', recovery: 30, description: 'Automated recovery' },
    staged: { label: 'Staged', recovery: 15, description: 'Per-depth recovery' },
    reroute: { label: 'Reroute', recovery: 25, description: 'Alternative paths' },
  };
  return info[type] || { label: type, recovery: 0, description: '' };
}


/**
 * Format improvement value
 * @param {number} improvement - Improvement value
 * @returns {string} Formatted string
 */
export function formatImprovement(improvement) {
  const prefix = improvement >= 0 ? '+' : '';
  return `${prefix}${improvement.toFixed(1)}`;
}


/**
 * Create a new recovery simulation
 * @param {Object} data - Recovery data
 * @returns {Promise<Object>} Created recovery
 */
export async function createRecovery(data) {
  const response = await fetch(`${API_BASE_URL}/recovery`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to create recovery: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get a specific recovery
 * @param {string} recoveryId - Recovery ID
 * @returns {Promise<Object>} Recovery
 */
export async function getRecovery(recoveryId) {
  const response = await fetch(`${API_BASE_URL}/recovery/${recoveryId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get recovery: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * List all recoveries
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Recoveries list
 */
export async function listRecoveries(params = {}) {
  const searchParams = new URLSearchParams();
  
  if (params.scenario_id) searchParams.append('scenario_id', params.scenario_id);
  if (params.skip) searchParams.append('skip', params.skip);
  if (params.limit) searchParams.append('limit', params.limit);
  
  const response = await fetch(
    `${API_BASE_URL}/recovery?${searchParams.toString()}`
  );
  
  if (!response.ok) {
    throw new Error(`Failed to list recoveries: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Delete a recovery
 * @param {string} recoveryId - Recovery ID
 * @returns {Promise<void>}
 */
export async function deleteRecovery(recoveryId) {
  const response = await fetch(`${API_BASE_URL}/recovery/${recoveryId}`, {
    method: 'DELETE',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to delete recovery: ${response.statusText}`);
  }
}


/**
 * Run a recovery simulation
 * @param {string} recoveryId - Recovery ID
 * @returns {Promise<Object>} Simulation results
 */
export async function runRecovery(recoveryId) {
  const response = await fetch(`${API_BASE_URL}/recovery/${recoveryId}/run`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to run recovery: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get results for a recovery
 * @param {string} recoveryId - Recovery ID
 * @returns {Promise<Object>} Results
 */
export async function getResults(recoveryId) {
  const response = await fetch(`${API_BASE_URL}/recovery/${recoveryId}/results`);
  
  if (!response.ok) {
    throw new Error(`Failed to get results: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get recovery tree
 * @param {string} recoveryId - Recovery ID
 * @returns {Promise<Object>} Recovery tree
 */
export async function getRecoveryTree(recoveryId) {
  const response = await fetch(`${API_BASE_URL}/recovery/${recoveryId}/tree`);
  
  if (!response.ok) {
    throw new Error(`Failed to get recovery tree: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Compare recovery results
 * @param {string} recoveryId - Recovery ID
 * @returns {Promise<Object>} Comparison
 */
export async function compareRecovery(recoveryId) {
  const response = await fetch(`${API_BASE_URL}/recovery/${recoveryId}/compare`);
  
  if (!response.ok) {
    throw new Error(`Failed to compare recovery: ${response.statusText}`);
  }
  
  return response.json();
}


export default {
  createRecovery,
  getRecovery,
  listRecoveries,
  deleteRecovery,
  runRecovery,
  getResults,
  getRecoveryTree,
  compareRecovery,
  getHealthColor,
  getRiskColor,
  getRecoveryTypeInfo,
  formatImprovement,
  RECOVERY_TYPES,
  RISK_LEVELS,
};