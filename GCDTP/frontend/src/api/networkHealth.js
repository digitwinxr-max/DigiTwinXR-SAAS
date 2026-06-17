/**
 * API client for Network Health (Dependency-Aware Health)
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';


/**
 * Relationship weights
 */
export const RELATIONSHIP_WEIGHTS = {
  contains: 0.5,
  connected_to: 0.3,
  feeds: 0.7,
  monitors: 0.0,
  controls: 0.6,
};


/**
 * Depth decay factors
 */
export const DEPTH_DECAY = {
  1: 1.0,
  2: 0.5,
  3: 0.25,
};


/**
 * Health status thresholds
 */
export const HEALTH_THRESHOLDS = {
  HEALTHY: { min: 80, max: 100 },
  DEGRADED: { min: 40, max: 79 },
  CRITICAL: { min: 0, max: 39 },
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
 * Get relationship info
 * @param {string} type - Relationship type
 * @returns {Object} Relationship info
 */
export function getRelationshipInfo(type) {
  const info = {
    contains: { label: 'Contains', weight: 0.5 },
    connected_to: { label: 'Connected To', weight: 0.3 },
    feeds: { label: 'Feeds', weight: 0.7 },
    monitors: { label: 'Monitors', weight: 0.0 },
    controls: { label: 'Controls', weight: 0.6 },
  };
  return info[type] || { label: type, weight: 0 };
}


/**
 * Get health tree for an asset
 * @param {string} assetId - Asset ID
 * @param {number} maxDepth - Maximum depth
 * @returns {Promise<Object>} Health tree
 */
export async function getHealthTree(assetId, maxDepth = 3) {
  const response = await fetch(
    `${API_BASE_URL}/health/tree/${assetId}?max_depth=${maxDepth}`
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch health tree: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get health contributors for an asset
 * @param {string} assetId - Asset ID
 * @returns {Promise<Object>} Health contributors
 */
export async function getContributors(assetId) {
  const response = await fetch(
    `${API_BASE_URL}/health/contributors/${assetId}`
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch contributors: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get network-wide health summary
 * @returns {Promise<Object>} Network health
 */
export async function getNetworkHealth() {
  const response = await fetch(`${API_BASE_URL}/health/network`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch network health: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Recalculate network health
 * @returns {Promise<Object>} Recalculation result
 */
export async function recalculateNetworkHealth() {
  const response = await fetch(`${API_BASE_URL}/health/recalculate-network`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to recalculate network health: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get relationship weights info
 * @returns {Promise<Array>} Relationship weights
 */
export async function getRelationshipWeights() {
  const response = await fetch(`${API_BASE_URL}/health/weights`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch weights: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get depth decay info
 * @returns {Promise<Object>} Depth decay
 */
export async function getDepthDecay() {
  const response = await fetch(`${API_BASE_URL}/health/decay`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch decay: ${response.statusText}`);
  }
  
  return response.json();
}


export default {
  getHealthTree,
  getContributors,
  getNetworkHealth,
  recalculateNetworkHealth,
  getRelationshipWeights,
  getDepthDecay,
  getHealthColor,
  getHealthStatus,
  getRelationshipInfo,
  RELATIONSHIP_WEIGHTS,
  DEPTH_DECAY,
  HEALTH_THRESHOLDS,
};