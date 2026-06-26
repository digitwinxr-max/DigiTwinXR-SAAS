/**
 * Resilience Analysis API Client
 * 
 * Endpoints for resilience analysis and recommendations.
 */

const API_BASE = '/api';


/**
 * Analyze a single asset's resilience
 * @param {string} assetId - Asset UUID
 * @param {boolean} forceRefresh - Force re-analysis
 * @returns {Promise<Object>} Analysis response
 */
export async function analyzeAsset(assetId, forceRefresh = false) {
  const response = await fetch(`${API_BASE}/resilience/analyze/${assetId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ force_refresh: forceRefresh }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to analyze asset');
  }
  
  return response.json();
}


/**
 * Analyze the entire network
 * @param {boolean} forceRefresh - Force re-analysis
 * @returns {Promise<Object>} Network resilience response
 */
export async function analyzeNetwork(forceRefresh = false) {
  const response = await fetch(`${API_BASE}/resilience/analyze-network`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ force_refresh: forceRefresh }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to analyze network');
  }
  
  return response.json();
}


/**
 * Get existing analysis for an asset
 * @param {string} assetId - Asset UUID
 * @returns {Promise<Object>} Analysis response
 */
export async function getAssetResilience(assetId) {
  const response = await fetch(`${API_BASE}/resilience/asset/${assetId}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get asset resilience');
  }
  
  return response.json();
}


/**
 * Get top critical assets
 * @param {number} limit - Maximum number of assets
 * @returns {Promise<Object>} Top critical assets response
 */
export async function getTopCriticalAssets(limit = 10) {
  const response = await fetch(`${API_BASE}/resilience/top-critical?limit=${limit}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get critical assets');
  }
  
  return response.json();
}


/**
 * Get network resilience metrics
 * @returns {Promise<Object>} Network resilience response
 */
export async function getNetworkResilience() {
  const response = await fetch(`${API_BASE}/resilience/network`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get network resilience');
  }
  
  return response.json();
}


/**
 * Get recommendations for an analysis
 * @param {string} analysisId - Analysis UUID
 * @param {string} priority - Optional priority filter
 * @returns {Promise<Array>} List of recommendations
 */
export async function getRecommendations(analysisId, priority = null) {
  const url = priority 
    ? `${API_BASE}/resilience/recommendations/${analysisId}?priority=${priority}`
    : `${API_BASE}/resilience/recommendations/${analysisId}`;
    
  const response = await fetch(url);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get recommendations');
  }
  
  return response.json();
}


/**
 * Get color for criticality score
 * @param {number} score - Criticality score (0-100)
 * @returns {string} Hex color code
 */
export function getCriticalityColor(score) {
  if (score < 40) return '#22c55e';  // Green
  if (score < 70) return '#f97316';  // Orange
  return '#ef4444';  // Red
}


/**
 * Get color for resilience score
 * @param {number} score - Resilience score (0-100)
 * @returns {string} Hex color code
 */
export function getResilienceColor(score) {
  if (score >= 70) return '#22c55e';  // Green - Good
  if (score >= 40) return '#eab308';  // Yellow - Moderate
  return '#ef4444';  // Red - Poor
}


/**
 * Get color for priority
 * @param {string} priority - Priority level
 * @returns {string} Hex color code
 */
export function getPriorityColor(priority) {
  const colors = {
    'LOW': '#22c55e',
    'MEDIUM': '#eab308',
    'HIGH': '#f97316',
    'CRITICAL': '#ef4444',
  };
  return colors[priority] || '#6b7280';
}


/**
 * Get criticality level label
 * @param {number} score - Criticality score
 * @returns {string} Level label
 */
export function getCriticalityLevel(score) {
  if (score >= 70) return 'HIGH';
  if (score >= 40) return 'MEDIUM';
  return 'LOW';
}


/**
 * Get resilience level label
 * @param {number} score - Resilience score
 * @returns {string} Level label
 */
export function getResilienceLevel(score) {
  if (score >= 70) return 'GOOD';
  if (score >= 40) return 'MODERATE';
  return 'POOR';
}


/**
 * Format recommendation type for display
 * @param {string} type - Recommendation type
 * @returns {string} Formatted type
 */
export function formatRecommendationType(type) {
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}


// Recommendation types for reference
export const RECOMMENDATION_TYPES = {
  REDUNDANCY: 'redundancy',
  MONITORING: 'monitoring',
  BACKUP: 'backup',
  FAILOVER: 'failover',
  MAINTENANCE: 'maintenance',
  DIVERSIFICATION: 'diversification',
  RECONFIGURATION: 'reconfiguration',
  EARLY_WARNING: 'early_warning',
};


// Priority levels
export const PRIORITIES = {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
  CRITICAL: 'CRITICAL',
};
