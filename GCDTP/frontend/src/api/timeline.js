/**
 * Timeline API
 * 
 * Provides API functions for timeline replay operations.
 * Timeline Replay is read-only.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Frame API
export async function getFrame(timestamp, windowSeconds = 60) {
  const params = new URLSearchParams({
    timestamp: timestamp,
    window_seconds: windowSeconds
  });
  
  const response = await fetch(`${API_BASE_URL}/timeline/frame?${params}`);
  
  if (!response.ok) {
    throw new Error('Failed to get frame');
  }
  
  return response.json();
}

// Range API
export async function getRange(startTime, endTime, options = {}) {
  const params = new URLSearchParams({
    start_time: startTime,
    end_time: endTime
  });
  
  if (options.entity_type) params.append('entity_type', options.entity_type);
  if (options.entity_id) params.append('entity_id', options.entity_id);
  if (options.snapshot_type) params.append('snapshot_type', options.snapshot_type);
  if (options.limit) params.append('limit', options.limit);
  if (options.offset) params.append('offset', options.offset);
  
  const response = await fetch(`${API_BASE_URL}/timeline/range?${params}`);
  
  if (!response.ok) {
    throw new Error('Failed to get range');
  }
  
  return response.json();
}

// Playback API
export async function playback(startTime, endTime, options = {}) {
  const params = new URLSearchParams({
    start_time: startTime,
    end_time: endTime,
    frame_interval: options.frame_interval || 60
  });
  
  if (options.entity_id) params.append('entity_id', options.entity_id);
  if (options.entity_type) params.append('entity_type', options.entity_type);
  
  const response = await fetch(`${API_BASE_URL}/timeline/playback?${params}`);
  
  if (!response.ok) {
    throw new Error('Failed to get playback');
  }
  
  return response.json();
}

// System Timeline API
export async function getSystem(options = {}) {
  const params = new URLSearchParams();
  
  if (options.start_time) params.append('start_time', options.start_time);
  if (options.end_time) params.append('end_time', options.end_time);
  if (options.limit) params.append('limit', options.limit);
  
  const response = await fetch(`${API_BASE_URL}/timeline/system?${params}`);
  
  if (!response.ok) {
    throw new Error('Failed to get system timeline');
  }
  
  return response.json();
}

// Asset Timeline API
export async function getAssetTimeline(assetId, options = {}) {
  const params = new URLSearchParams();
  
  if (options.start_time) params.append('start_time', options.start_time);
  if (options.end_time) params.append('end_time', options.end_time);
  
  const response = await fetch(
    `${API_BASE_URL}/timeline/asset/${assetId}?${params}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to get asset timeline');
  }
  
  return response.json();
}

// Event Timeline API
export async function getEventTimeline(eventId, options = {}) {
  const params = new URLSearchParams();
  
  if (options.start_time) params.append('start_time', options.start_time);
  if (options.end_time) params.append('end_time', options.end_time);
  
  const response = await fetch(
    `${API_BASE_URL}/timeline/event/${eventId}?${params}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to get event timeline');
  }
  
  return response.json();
}

// Health Timeline API
export async function getHealthTimeline(assetId, options = {}) {
  const params = new URLSearchParams();
  
  if (options.start_time) params.append('start_time', options.start_time);
  if (options.end_time) params.append('end_time', options.end_time);
  
  const response = await fetch(
    `${API_BASE_URL}/timeline/health/${assetId}?${params}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to get health timeline');
  }
  
  return response.json();
}

// Create Snapshot API (for internal use)
export async function createSnapshot(data) {
  const response = await fetch(`${API_BASE_URL}/timeline/snapshot`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error('Failed to create snapshot');
  }
  
  return response.json();
}

// Export all API functions
export default {
  getFrame,
  getRange,
  playback,
  getSystem,
  getAssetTimeline,
  getEventTimeline,
  getHealthTimeline,
  createSnapshot
};
