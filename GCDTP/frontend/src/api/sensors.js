const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export async function getSensors() {
  const response = await fetch(`${API_BASE_URL}/sensors`);
  if (!response.ok) throw new Error('Failed to fetch sensors');
  return response.json();
}

export async function getSensor(id) {
  const response = await fetch(`${API_BASE_URL}/sensors/${id}`);
  if (!response.ok) throw new Error('Failed to fetch sensor');
  return response.json();
}

export async function createSensor(sensorData) {
  const response = await fetch(`${API_BASE_URL}/sensors`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(sensorData),
  });
  if (!response.ok) throw new Error('Failed to create sensor');
  return response.json();
}

export async function updateSensor(id, sensorData) {
  const response = await fetch(`${API_BASE_URL}/sensors/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(sensorData),
  });
  if (!response.ok) throw new Error('Failed to update sensor');
  return response.json();
}

export async function deleteSensor(id) {
  const response = await fetch(`${API_BASE_URL}/sensors/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete sensor');
  return true;
}

export async function getSensorsByAsset(assetId) {
  const response = await fetch(`${API_BASE_URL}/sensors/asset/${assetId}`);
  if (!response.ok) throw new Error('Failed to fetch sensors');
  return response.json();
}
