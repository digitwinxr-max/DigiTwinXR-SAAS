/**
 * Logbook API
 * 
 * Provides API functions for digital logbook operations.
 * Entries are append-only - no edits or deletes.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create Entry
export async function createEntry(data) {
  const response = await fetch(`${API_BASE_URL}/logbook`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error('Failed to create entry');
  }
  
  return response.json();
}

// List Entries
export async function listEntries(options = {}) {
  const params = new URLSearchParams();
  
  if (options.entry_type) params.append('entry_type', options.entry_type);
  if (options.severity) params.append('severity', options.severity);
  if (options.author) params.append('author', options.author);
  if (options.limit) params.append('limit', options.limit);
  if (options.offset) params.append('offset', options.offset);
  
  const response = await fetch(`${API_BASE_URL}/logbook?${params}`);
  
  if (!response.ok) {
    throw new Error('Failed to list entries');
  }
  
  return response.json();
}

// Get Entry
export async function getEntry(entryId) {
  const response = await fetch(`${API_BASE_URL}/logbook/${entryId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get entry');
  }
  
  return response.json();
}

// Search Entries
export async function searchEntries(options = {}) {
  const params = new URLSearchParams();
  
  if (options.query) params.append('query', options.query);
  if (options.entry_type) params.append('entry_type', options.entry_type);
  if (options.entity_type) params.append('entity_type', options.entity_type);
  if (options.entity_id) params.append('entity_id', options.entity_id);
  if (options.severity) params.append('severity', options.severity);
  if (options.author) params.append('author', options.author);
  if (options.start_time) params.append('start_time', options.start_time);
  if (options.end_time) params.append('end_time', options.end_time);
  if (options.limit) params.append('limit', options.limit);
  if (options.offset) params.append('offset', options.offset);
  
  const response = await fetch(`${API_BASE_URL}/logbook/search?${params}`);
  
  if (!response.ok) {
    throw new Error('Failed to search entries');
  }
  
  return response.json();
}

// Get Entity History
export async function getEntityHistory(entityType, entityId) {
  const response = await fetch(`${API_BASE_URL}/logbook/entity/${entityType}/${entityId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get entity history');
  }
  
  return response.json();
}

// Get Entry History (with timeline links)
export async function getEntryHistory(entityType, entityId) {
  const response = await fetch(`${API_BASE_URL}/logbook/history/${entityType}/${entityId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get entry history');
  }
  
  return response.json();
}

// Get Entries by Type
export async function getEntriesByType(entryType, options = {}) {
  const params = new URLSearchParams();
  
  if (options.limit) params.append('limit', options.limit);
  if (options.offset) params.append('offset', options.offset);
  
  const response = await fetch(
    `${API_BASE_URL}/logbook/type/${entryType}?${params}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to get entries by type');
  }
  
  return response.json();
}

// Get Entries by Severity
export async function getEntriesBySeverity(severity, options = {}) {
  const params = new URLSearchParams();
  
  if (options.limit) params.append('limit', options.limit);
  if (options.offset) params.append('offset', options.offset);
  
  const response = await fetch(
    `${API_BASE_URL}/logbook/severity/${severity}?${params}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to get entries by severity');
  }
  
  return response.json();
}

// Get Incident History
export async function getIncidentHistory(options = {}) {
  const params = new URLSearchParams();
  
  if (options.start_time) params.append('start_time', options.start_time);
  if (options.end_time) params.append('end_time', options.end_time);
  
  const response = await fetch(`${API_BASE_URL}/logbook/incidents/history?${params}`);
  
  if (!response.ok) {
    throw new Error('Failed to get incident history');
  }
  
  return response.json();
}

// Get Entries by Timeline
export async function getEntriesByTimeline(timelineSnapshotId, options = {}) {
  const params = new URLSearchParams();
  
  if (options.limit) params.append('limit', options.limit);
  if (options.offset) params.append('offset', options.offset);
  
  const response = await fetch(
    `${API_BASE_URL}/logbook/timeline/${timelineSnapshotId}?${params}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to get timeline entries');
  }
  
  return response.json();
}

// Get Summary
export async function getSummary() {
  const response = await fetch(`${API_BASE_URL}/logbook/summary`);
  
  if (!response.ok) {
    throw new Error('Failed to get summary');
  }
  
  return response.json();
}

// Get Entries by Author
export async function getEntriesByAuthor(author, options = {}) {
  const params = new URLSearchParams();
  
  if (options.limit) params.append('limit', options.limit);
  if (options.offset) params.append('offset', options.offset);
  
  const response = await fetch(
    `${API_BASE_URL}/logbook/author/${author}?${params}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to get entries by author');
  }
  
  return response.json();
}

// Export all API functions
export default {
  createEntry,
  listEntries,
  getEntry,
  searchEntries,
  getEntityHistory,
  getEntryHistory,
  getEntriesByType,
  getEntriesBySeverity,
  getIncidentHistory,
  getEntriesByTimeline,
  getSummary,
  getEntriesByAuthor
};
