/**
 * RAG Engine API
 * 
 * Provides API functions for RAG (Retrieval-Augmented Generation).
 * This is read-only - NO operational writes.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Query API
export async function queryRAG(request) {
  const response = await fetch(`${API_BASE_URL}/rag/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  
  if (!response.ok) {
    throw new Error('Failed to query RAG');
  }
  
  return response.json();
}

// History API
export async function getHistory(sessionId) {
  const response = await fetch(`${API_BASE_URL}/rag/history/${sessionId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get history');
  }
  
  return response.json();
}

// Sources API
export async function getSources(queryId) {
  const response = await fetch(`${API_BASE_URL}/rag/sources/${queryId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get sources');
  }
  
  return response.json();
}

// Context API
export async function getContext(queryId) {
  const response = await fetch(`${API_BASE_URL}/rag/context/${queryId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get context');
  }
  
  return response.json();
}

// Models API
export async function getModels() {
  const response = await fetch(`${API_BASE_URL}/rag/models`);
  
  if (!response.ok) {
    throw new Error('Failed to get models');
  }
  
  return response.json();
}

// Retrieve Context API
export async function retrieveContext(options = {}) {
  const params = new URLSearchParams();
  
  if (options.entity_type) params.append('entity_type', options.entity_type);
  if (options.entity_id) params.append('entity_id', options.entity_id);
  if (options.query) params.append('query', options.query);
  if (options.include_semantic !== undefined) params.append('include_semantic', options.include_semantic);
  if (options.include_health !== undefined) params.append('include_health', options.include_health);
  if (options.include_events !== undefined) params.append('include_events', options.include_events);
  if (options.include_timeline !== undefined) params.append('include_timeline', options.include_timeline);
  if (options.include_logbook !== undefined) params.append('include_logbook', options.include_logbook);
  if (options.include_knowledge !== undefined) params.append('include_knowledge', options.include_knowledge);
  
  const response = await fetch(`${API_BASE_URL}/rag/retrieve?${params}`);
  
  if (!response.ok) {
    throw new Error('Failed to retrieve context');
  }
  
  return response.json();
}

// Export all API functions
export default {
  queryRAG,
  getHistory,
  getSources,
  getContext,
  getModels,
  retrieveContext
};
