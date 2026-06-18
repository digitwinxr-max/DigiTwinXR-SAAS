/**
 * Predictive Maintenance API
 * 
 * API client for Predictive Maintenance Engine.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

// Run prediction
export async function runPrediction(assetId, params = {}) {
  const searchParams = new URLSearchParams({
    current_health: params.current_health || 100,
    health_trend: params.health_trend || 0,
    active_events: params.active_events || 0,
    measurement_anomalies: params.measurement_anomalies || 0,
    days_since_maintenance: params.days_since_maintenance || 0,
    asset_type: params.asset_type || 'generic',
    data_quality_score: params.data_quality_score || 0.8
  });

  const response = await fetch(
    `${API_BASE_URL}/predictive/run/${assetId}?${searchParams}`,
    { method: 'POST' }
  );
  
  if (!response.ok) throw new Error('Failed to run prediction');
  return response.json();
}

// Get prediction
export async function getPrediction(assetId) {
  const response = await fetch(`${API_BASE_URL}/predictive/${assetId}`);
  if (!response.ok) throw new Error('Failed to get prediction');
  return response.json();
}

// Get prediction history
export async function getPredictionHistory(assetId, limit = 30) {
  const response = await fetch(
    `${API_BASE_URL}/predictive/history/${assetId}?limit=${limit}`
  );
  if (!response.ok) throw new Error('Failed to get history');
  return response.json();
}

// Get high-risk assets
export async function getHighRiskAssets(limit = 10) {
  const response = await fetch(
    `${API_BASE_URL}/predictive/high-risk?limit=${limit}`
  );
  if (!response.ok) throw new Error('Failed to get high-risk assets');
  return response.json();
}

// Get recommendations
export async function getRecommendations(limit = 20) {
  const response = await fetch(
    `${API_BASE_URL}/predictive/recommendations?limit=${limit}`
  );
  if (!response.ok) throw new Error('Failed to get recommendations');
  return response.json();
}

// Get health timeline
export async function getHealthTimeline(assetId, currentHealth = 100, healthTrend = 0) {
  const response = await fetch(
    `${API_BASE_URL}/predictive/timeline/${assetId}?current_health=${currentHealth}&health_trend=${healthTrend}`
  );
  if (!response.ok) throw new Error('Failed to get timeline');
  return response.json();
}

// Get failure probability
export async function getFailureProbability(assetId, params = {}) {
  const searchParams = new URLSearchParams({
    current_health: params.current_health || 100,
    health_trend: params.health_trend || 0,
    active_events: params.active_events || 0,
    measurement_anomalies: params.measurement_anomalies || 0,
    days_since_maintenance: params.days_since_maintenance || 0
  });

  const response = await fetch(
    `${API_BASE_URL}/predictive/probability/${assetId}?${searchParams}`
  );
  if (!response.ok) throw new Error('Failed to get probability');
  return response.json();
}

export default {
  runPrediction,
  getPrediction,
  getPredictionHistory,
  getHighRiskAssets,
  getRecommendations,
  getHealthTimeline,
  getFailureProbability
};
