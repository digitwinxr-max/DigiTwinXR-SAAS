const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export async function getHealthSummary() {
  const response = await fetch(`${API_BASE_URL}/health/summary`);
  if (!response.ok) throw new Error('Failed to fetch health summary');
  return response.json();
}

export async function getAllAssetHealth(params = {}) {
  const searchParams = new URLSearchParams();
  if (params.status) searchParams.append('status', params.status);
  if (params.limit) searchParams.append('limit', params.limit);
  
  const response = await fetch(`${API_BASE_URL}/health/assets?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch asset health');
  return response.json();
}

export async function getAssetHealth(assetId) {
  const response = await fetch(`${API_BASE_URL}/health/assets/${assetId}`);
  if (!response.ok) {
    if (response.status === 404) return null;
    throw new Error('Failed to fetch asset health');
  }
  return response.json();
}

export async function recalculateAssetHealth(assetId) {
  const response = await fetch(`${API_BASE_URL}/health/recalculate/${assetId}`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to recalculate health');
  return response.json();
}

export async function recalculateAllHealth() {
  const response = await fetch(`${API_BASE_URL}/health/recalculate-all`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to recalculate all health');
  return response.json();
}