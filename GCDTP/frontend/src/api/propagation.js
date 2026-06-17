/**
 * API client for Failure Propagation
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';


/**
 * Propagation type constants
 */
export const PROPAGATION_TYPES = {
  CHILD_FAILURE: 'child_failure',
  UPSTREAM_FAILURE: 'upstream_failure',
  DOWNSTREAM_FAILURE: 'downstream_failure',
  DEPENDENCY_IMPACT: 'dependency_impact',
};


/**
 * Propagation type info with labels and colors
 */
export const PROPAGATION_TYPE_INFO = {
  [PROPAGATION_TYPES.CHILD_FAILURE]: {
    label: 'Child Failure',
    color: '#ef4444',
    description: 'Child failure propagated to parent',
  },
  [PROPAGATION_TYPES.UPSTREAM_FAILURE]: {
    label: 'Upstream Failure',
    color: '#f97316',
    description: 'Upstream asset failure',
  },
  [PROPAGATION_TYPES.DOWNSTREAM_FAILURE]: {
    label: 'Downstream Failure',
    color: '#eab308',
    description: 'Downstream asset failure',
  },
  [PROPAGATION_TYPES.DEPENDENCY_IMPACT]: {
    label: 'Dependency Impact',
    color: '#8b5cf6',
    description: 'Dependency failure impact',
  },
};


/**
 * Severity colors
 */
export const SEVERITY_COLORS = {
  WARNING: '#eab308',
  CRITICAL: '#ef4444',
};


/**
 * Get propagation records for an event
 * @param {string} eventId - Event ID
 * @returns {Promise<Object>} Paginated list of propagations
 */
export async function getEventPropagation(eventId) {
  const response = await fetch(`${API_BASE_URL}/propagation/event/${eventId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch event propagation: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get all impacts on an asset
 * @param {string} assetId - Asset ID
 * @returns {Promise<Array>} List of impacts
 */
export async function getAssetImpacts(assetId) {
  const response = await fetch(`${API_BASE_URL}/propagation/asset/${assetId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch asset impacts: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get impact chain for an asset
 * @param {string} assetId - Asset ID
 * @param {string} eventId - Optional event ID
 * @param {number} maxDepth - Maximum depth
 * @returns {Promise<Object>} Impact chain
 */
export async function getImpactChain(assetId, eventId = null, maxDepth = 10) {
  let url = `${API_BASE_URL}/propagation/chain/${assetId}`;
  const params = new URLSearchParams();
  
  if (eventId) {
    params.set('event_id', eventId);
  }
  params.set('max_depth', maxDepth);
  
  url += `?${params}`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch impact chain: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get all propagation impacts
 * @param {Object} params - Query parameters
 * @param {number} params.skip - Skip count
 * @param {number} params.limit - Limit count
 * @param {number} params.min_depth - Minimum depth
 * @param {string} params.severity - Severity filter
 * @returns {Promise<Object>} Paginated list of impacts
 */
export async function getImpacts(params = {}) {
  const searchParams = new URLSearchParams();
  
  if (params.skip !== undefined) searchParams.set('skip', params.skip);
  if (params.limit !== undefined) searchParams.set('limit', params.limit);
  if (params.min_depth !== undefined) searchParams.set('min_depth', params.min_depth);
  if (params.severity) searchParams.set('severity', params.severity);
  
  const response = await fetch(`${API_BASE_URL}/propagation/impacts?${searchParams}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch impacts: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get available propagation types
 * @returns {Promise<Array>} List of propagation types
 */
export async function getPropagationTypes() {
  const response = await fetch(`${API_BASE_URL}/propagation/types`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch propagation types: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Manually trigger propagation for an event
 * @param {string} eventId - Event ID
 * @param {number} maxDepth - Maximum depth
 * @returns {Promise<Object>} Propagation result
 */
export async function manualPropagate(eventId, maxDepth = 3) {
  const response = await fetch(
    `${API_BASE_URL}/propagation/propagate/${eventId}?max_depth=${maxDepth}`,
    { method: 'POST' }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to trigger propagation: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Format propagation type for display
 * @param {string} type - Propagation type
 * @returns {string} Display label
 */
export function formatPropagationType(type) {
  const info = PROPAGATION_TYPE_INFO[type];
  return info ? info.label : type;
}


/**
 * Get color for propagation type
 * @param {string} type - Propagation type
 * @returns {string} Hex color
 */
export function getPropagationColor(type) {
  const info = PROPAGATION_TYPE_INFO[type];
  return info ? info.color : '#6b7280';
}


/**
 * Get color for severity
 * @param {string} severity - Severity level
 * @returns {string} Hex color
 */
export function getSeverityColor(severity) {
  return SEVERITY_COLORS[severity] || '#6b7280';
}


export default {
  getEventPropagation,
  getAssetImpacts,
  getImpactChain,
  getImpacts,
  getPropagationTypes,
  manualPropagate,
  formatPropagationType,
  getPropagationColor,
  getSeverityColor,
  PROPAGATION_TYPES,
  PROPAGATION_TYPE_INFO,
  SEVERITY_COLORS,
};