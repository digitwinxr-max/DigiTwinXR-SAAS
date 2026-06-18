/**
 * Root Cause Analysis API
 * 
 * API client for Root Cause Analysis Engine.
 * READ ONLY - NO automation, NO work orders.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

// Analyze asset
export async function analyzeAsset(assetId, params = {}) {
  const searchParams = new URLSearchParams({
    analysis_type: params.analysis_type || 'failure',
    event_id: params.event_id || '',
    time_window_hours: params.time_window_hours || 24
  });
  
  // Remove empty event_id
  if (!params.event_id) {
    searchParams.delete('event_id');
  }

  const response = await fetch(
    `${API_BASE_URL}/root-cause/analyze/${assetId}?${searchParams}`,
    { method: 'POST' }
  );
  
  if (!response.ok) throw new Error('Failed to analyze asset');
  return response.json();
}

// Get analysis by ID
export async function getAnalysis(analysisId) {
  const response = await fetch(`${API_BASE_URL}/root-cause/${analysisId}`);
  if (!response.ok) throw new Error('Failed to get analysis');
  return response.json();
}

// Get analyses for asset
export async function getAnalysesForAsset(assetId, limit = 10) {
  const response = await fetch(
    `${API_BASE_URL}/root-cause/asset/${assetId}?limit=${limit}`
  );
  if (!response.ok) throw new Error('Failed to get analyses');
  return response.json();
}

// Analyze event
export async function analyzeEvent(eventId, assetId) {
  const response = await fetch(
    `${API_BASE_URL}/root-cause/event/${eventId}?asset_id=${assetId}`,
    { method: 'GET' }
  );
  if (!response.ok) throw new Error('Failed to analyze event');
  return response.json();
}

// Get factors for analysis
export async function getFactors(analysisId) {
  const response = await fetch(`${API_BASE_URL}/root-cause/factors/${analysisId}`);
  if (!response.ok) throw new Error('Failed to get factors');
  return response.json();
}

// Get chains for analysis
export async function getChains(analysisId) {
  const response = await fetch(`${API_BASE_URL}/root-cause/chains/${analysisId}`);
  if (!response.ok) throw new Error('Failed to get chains');
  return response.json();
}

// Get high confidence analyses
export async function getHighConfidenceAnalyses(threshold = 0.7) {
  const response = await fetch(
    `${API_BASE_URL}/root-cause/high-confidence?threshold=${threshold}`
  );
  if (!response.ok) throw new Error('Failed to get high confidence analyses');
  return response.json();
}

// Get analysis history
export async function getAnalysisHistory(limit = 20) {
  const response = await fetch(
    `${API_BASE_URL}/root-cause/history?limit=${limit}`
  );
  if (!response.ok) throw new Error('Failed to get history');
  return response.json();
}

export default {
  analyzeAsset,
  getAnalysis,
  getAnalysesForAsset,
  analyzeEvent,
  getFactors,
  getChains,
  getHighConfidenceAnalyses,
  getAnalysisHistory
};
