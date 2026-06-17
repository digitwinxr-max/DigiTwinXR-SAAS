const API_BASE = '/api';

export async function getAssets(skip = 0, limit = 100) {
  const response = await fetch(`${API_BASE}/assets?skip=${skip}&limit=${limit}`);
  if (!response.ok) throw new Error('Failed to fetch assets');
  return response.json();
}

export async function getAsset(id) {
  const response = await fetch(`${API_BASE}/assets/${id}`);
  if (!response.ok) throw new Error('Failed to fetch asset');
  return response.json();
}

export async function createAsset(data) {
  const response = await fetch(`${API_BASE}/assets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create asset');
  return response.json();
}

export async function updateAsset(id, data) {
  const response = await fetch(`${API_BASE}/assets/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update asset');
  return response.json();
}

export async function deleteAsset(id) {
  const response = await fetch(`${API_BASE}/assets/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete asset');
}
