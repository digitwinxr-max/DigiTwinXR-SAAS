const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export async function getMeasurements(params = {}) {
  const searchParams = new URLSearchParams();
  if (params.sensor_id) searchParams.append('sensor_id', params.sensor_id);
  if (params.limit) searchParams.append('limit', params.limit);
  if (params.start_time) searchParams.append('start_time', params.start_time);
  if (params.end_time) searchParams.append('end_time', params.end_time);
  
  const response = await fetch(`${API_BASE_URL}/measurements?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch measurements');
  return response.json();
}

export async function getMeasurement(id) {
  const response = await fetch(`${API_BASE_URL}/measurements/${id}`);
  if (!response.ok) throw new Error('Failed to fetch measurement');
  return response.json();
}

export async function createMeasurement(measurementData) {
  const response = await fetch(`${API_BASE_URL}/measurements`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(measurementData),
  });
  if (!response.ok) throw new Error('Failed to create measurement');
  return response.json();
}

export async function deleteMeasurement(id) {
  const response = await fetch(`${API_BASE_URL}/measurements/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete measurement');
  return true;
}

export async function getMeasurementsBySensor(sensorId, params = {}) {
  const searchParams = new URLSearchParams();
  if (params.limit) searchParams.append('limit', params.limit);
  if (params.start_time) searchParams.append('start_time', params.start_time);
  if (params.end_time) searchParams.append('end_time', params.end_time);
  
  const response = await fetch(`${API_BASE_URL}/measurements/sensor/${sensorId}?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch measurements');
  return response.json();
}
