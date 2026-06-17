const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export async function getEvents(params = {}) {
  const searchParams = new URLSearchParams();
  if (params.sensor_id) searchParams.append('sensor_id', params.sensor_id);
  if (params.asset_id) searchParams.append('asset_id', params.asset_id);
  if (params.status) searchParams.append('status', params.status);
  if (params.severity) searchParams.append('severity', params.severity);
  if (params.event_type) searchParams.append('event_type', params.event_type);
  if (params.limit) searchParams.append('limit', params.limit);
  
  const response = await fetch(`${API_BASE_URL}/events?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch events');
  return response.json();
}

export async function getActiveEvents(params = {}) {
  const searchParams = new URLSearchParams();
  if (params.severity) searchParams.append('severity', params.severity);
  if (params.limit) searchParams.append('limit', params.limit);
  
  const response = await fetch(`${API_BASE_URL}/events/active?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch active events');
  return response.json();
}

export async function getEvent(id) {
  const response = await fetch(`${API_BASE_URL}/events/${id}`);
  if (!response.ok) throw new Error('Failed to fetch event');
  return response.json();
}

export async function createEventManual(eventData) {
  const response = await fetch(`${API_BASE_URL}/events/manual`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(eventData),
  });
  if (!response.ok) throw new Error('Failed to create event');
  return response.json();
}

export async function createEventFromEvaluation(evaluation, measurement) {
  const response = await fetch(`${API_BASE_URL}/events/from-evaluation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ evaluation, measurement }),
  });
  if (!response.ok) throw new Error('Failed to create event from evaluation');
  return response.json();
}

export async function resolveEvent(id, resolutionNotes = null) {
  const body = resolutionNotes ? { resolution_notes: resolutionNotes } : {};
  const response = await fetch(`${API_BASE_URL}/events/${id}/resolve`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error('Failed to resolve event');
  return response.json();
}

export async function getEventsBySensor(sensorId) {
  const response = await fetch(`${API_BASE_URL}/events/sensor/${sensorId}`);
  if (!response.ok) throw new Error('Failed to fetch events');
  return response.json();
}

export async function getEventsByAsset(assetId) {
  const response = await fetch(`${API_BASE_URL}/events/asset/${assetId}`);
  if (!response.ok) throw new Error('Failed to fetch events');
  return response.json();
}