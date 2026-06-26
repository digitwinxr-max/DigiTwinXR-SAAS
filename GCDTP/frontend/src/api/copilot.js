/**
 * Cognitive Copilot API
 * 
 * Provides API functions for Cognitive Copilot operations.
 * This is read-only AI context - NO LLM integration yet.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Session API
export async function createSession(sessionName) {
  const response = await fetch(`${API_BASE_URL}/copilot/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_name: sessionName })
  });
  
  if (!response.ok) {
    throw new Error('Failed to create session');
  }
  
  return response.json();
}

export async function getSession(sessionId) {
  const response = await fetch(`${API_BASE_URL}/copilot/session/${sessionId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get session');
  }
  
  return response.json();
}

export async function listSessions() {
  const response = await fetch(`${API_BASE_URL}/copilot/sessions`);
  
  if (!response.ok) {
    throw new Error('Failed to list sessions');
  }
  
  return response.json();
}

// Query API
export async function queryCopilot(sessionId, query, entityType, entityId) {
  const response = await fetch(`${API_BASE_URL}/copilot/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      query: query,
      entity_type: entityType,
      entity_id: entityId
    })
  });
  
  if (!response.ok) {
    throw new Error('Failed to query copilot');
  }
  
  return response.json();
}

// History API
export async function getHistory(sessionId) {
  const response = await fetch(`${API_BASE_URL}/copilot/history/${sessionId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get history');
  }
  
  return response.json();
}

export async function getMessages(sessionId) {
  const response = await fetch(`${API_BASE_URL}/copilot/messages/${sessionId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get messages');
  }
  
  return response.json();
}

// Context API
export async function getContext(entityType, entityId, options = {}) {
  const params = new URLSearchParams({
    entity_type: entityType,
    entity_id: entityId
  });
  
  if (options.asset) params.append('asset', JSON.stringify(options.asset));
  if (options.health) params.append('health', JSON.stringify(options.health));
  
  const response = await fetch(`${API_BASE_URL}/copilot/context/${entityType}/${entityId}?${params}`);
  
  if (!response.ok) {
    throw new Error('Failed to get context');
  }
  
  return response.json();
}

// Summary API
export async function getEntitySummary(entityType, entityId) {
  const response = await fetch(`${API_BASE_URL}/copilot/summary/${entityType}/${entityId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get entity summary');
  }
  
  return response.json();
}

// Export all API functions
export default {
  createSession,
  getSession,
  listSessions,
  queryCopilot,
  getHistory,
  getMessages,
  getContext,
  getEntitySummary
};
