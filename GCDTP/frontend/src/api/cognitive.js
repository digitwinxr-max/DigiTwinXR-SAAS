/**
 * Cognitive Twin API
 * 
 * API client for Cognitive Twin Engine.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

// Create session
export async function createSession(data) {
  const response = await fetch(`${API_BASE_URL}/cognitive/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error('Failed to create session');
  return response.json();
}

// Get sessions
export async function getSessions(limit = 20) {
  const response = await fetch(`${API_BASE_URL}/cognitive/sessions?limit=${limit}`);
  if (!response.ok) throw new Error('Failed to get sessions');
  return response.json();
}

// Get session
export async function getSession(sessionId) {
  const response = await fetch(`${API_BASE_URL}/cognitive/session/${sessionId}`);
  if (!response.ok) throw new Error('Failed to get session');
  return response.json();
}

// Ask question
export async function askQuestion(sessionId, data) {
  const params = new URLSearchParams({ session_id: sessionId });
  const response = await fetch(`${API_BASE_URL}/cognitive/query?${params}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error('Failed to ask question');
  return response.json();
}

// Get history
export async function getHistory(sessionId, limit = 20) {
  const response = await fetch(`${API_BASE_URL}/cognitive/history/${sessionId}?limit=${limit}`);
  if (!response.ok) throw new Error('Failed to get history');
  return response.json();
}

// Get context
export async function getContext(queryId) {
  const response = await fetch(`${API_BASE_URL}/cognitive/context/${queryId}`);
  if (!response.ok) throw new Error('Failed to get context');
  return response.json();
}

// Get insights
export async function getInsights(limit = 20) {
  const response = await fetch(`${API_BASE_URL}/cognitive/insights?limit=${limit}`);
  if (!response.ok) throw new Error('Failed to get insights');
  return response.json();
}

// Get explanations
export async function getExplanations(limit = 20) {
  const response = await fetch(`${API_BASE_URL}/cognitive/explanations?limit=${limit}`);
  if (!response.ok) throw new Error('Failed to get explanations');
  return response.json();
}

// Get confidence
export async function getConfidence(queryId) {
  const response = await fetch(`${API_BASE_URL}/cognitive/confidence/${queryId}`);
  if (!response.ok) throw new Error('Failed to get confidence');
  return response.json();
}

// Get graph
export async function getGraph(queryId) {
  const response = await fetch(`${API_BASE_URL}/cognitive/graph/${queryId}`);
  if (!response.ok) throw new Error('Failed to get graph');
  return response.json();
}

export default {
  createSession,
  getSessions,
  getSession,
  askQuestion,
  getHistory,
  getContext,
  getInsights,
  getExplanations,
  getConfidence,
  getGraph
};
