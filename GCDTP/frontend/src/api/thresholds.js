const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export async function getThresholds(params = {}) {
  const searchParams = new URLSearchParams();
  if (params.sensor_id) searchParams.append('sensor_id', params.sensor_id);
  if (params.is_active !== undefined) searchParams.append('is_active', params.is_active);
  if (params.limit) searchParams.append('limit', params.limit);
  
  const response = await fetch(`${API_BASE_URL}/thresholds?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch thresholds');
  return response.json();
}

export async function getThreshold(id) {
  const response = await fetch(`${API_BASE_URL}/thresholds/${id}`);
  if (!response.ok) throw new Error('Failed to fetch threshold');
  return response.json();
}

export async function createThreshold(ruleData) {
  const response = await fetch(`${API_BASE_URL}/thresholds`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(ruleData),
  });
  if (!response.ok) throw new Error('Failed to create threshold');
  return response.json();
}

export async function updateThreshold(id, ruleData) {
  const response = await fetch(`${API_BASE_URL}/thresholds/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(ruleData),
  });
  if (!response.ok) throw new Error('Failed to update threshold');
  return response.json();
}

export async function deleteThreshold(id) {
  const response = await fetch(`${API_BASE_URL}/thresholds/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete threshold');
  return true;
}

export async function getThresholdsBySensor(sensorId) {
  const response = await fetch(`${API_BASE_URL}/thresholds/sensor/${sensorId}`);
  if (!response.ok) throw new Error('Failed to fetch thresholds');
  return response.json();
}

export async function evaluateMeasurement(measurementData) {
  const response = await fetch(`${API_BASE_URL}/thresholds/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(measurementData),
  });
  if (!response.ok) throw new Error('Failed to evaluate measurement');
  return response.json();
}