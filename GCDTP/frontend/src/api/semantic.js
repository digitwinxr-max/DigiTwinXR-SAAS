/**
 * Semantic Layer API
 * 
 * Provides API functions for semantic metadata operations.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Entity API
export async function createEntity(data) {
  const response = await fetch(`${API_BASE_URL}/semantic/entities`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error('Failed to create entity');
  }
  
  return response.json();
}

export async function getEntity(entityId) {
  const response = await fetch(`${API_BASE_URL}/semantic/entity/${entityId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get entity');
  }
  
  return response.json();
}

export async function listEntities(params = {}) {
  const queryParams = new URLSearchParams(params).toString();
  const url = `${API_BASE_URL}/semantic/entities${queryParams ? `?${queryParams}` : ''}`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error('Failed to list entities');
  }
  
  return response.json();
}

export async function updateEntity(entityId, data) {
  const response = await fetch(`${API_BASE_URL}/semantic/entity/${entityId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error('Failed to update entity');
  }
  
  return response.json();
}

export async function deleteEntity(entityId) {
  const response = await fetch(`${API_BASE_URL}/semantic/entity/${entityId}`, {
    method: 'DELETE'
  });
  
  if (!response.ok) {
    throw new Error('Failed to delete entity');
  }
  
  return response.json();
}

// Tag API
export async function createTag(data) {
  const response = await fetch(`${API_BASE_URL}/semantic/tags`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error('Failed to create tag');
  }
  
  return response.json();
}

export async function getTags(entityId) {
  const response = await fetch(`${API_BASE_URL}/semantic/tags/${entityId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get tags');
  }
  
  return response.json();
}

export async function deleteTag(tagId) {
  const response = await fetch(`${API_BASE_URL}/semantic/tag/${tagId}`, {
    method: 'DELETE'
  });
  
  if (!response.ok) {
    throw new Error('Failed to delete tag');
  }
  
  return response.json();
}

// Relationship API
export async function createRelationship(data) {
  const response = await fetch(`${API_BASE_URL}/semantic/relationships`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error('Failed to create relationship');
  }
  
  return response.json();
}

export async function getRelationships(entityId) {
  const response = await fetch(`${API_BASE_URL}/semantic/relationships/${entityId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get relationships');
  }
  
  return response.json();
}

export async function deleteRelationship(relationshipId) {
  const response = await fetch(`${API_BASE_URL}/semantic/relationship/${relationshipId}`, {
    method: 'DELETE'
  });
  
  if (!response.ok) {
    throw new Error('Failed to delete relationship');
  }
  
  return response.json();
}

// Search API
export async function searchSemantic(params = {}) {
  const queryParams = new URLSearchParams(params).toString();
  const url = `${API_BASE_URL}/semantic/search${queryParams ? `?${queryParams}` : ''}`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error('Failed to search');
  }
  
  return response.json();
}

// Context API
export async function getContext(entityType, entityId) {
  const response = await fetch(`${API_BASE_URL}/semantic/context/${entityType}/${entityId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get context');
  }
  
  return response.json();
}

// Graph API
export async function getGraph(limit = 500) {
  const response = await fetch(`${API_BASE_URL}/semantic/graph?limit=${limit}`);
  
  if (!response.ok) {
    throw new Error('Failed to get graph');
  }
  
  return response.json();
}

// Tag Summary API
export async function getTagSummary() {
  const response = await fetch(`${API_BASE_URL}/semantic/tags/summary`);
  
  if (!response.ok) {
    throw new Error('Failed to get tag summary');
  }
  
  return response.json();
}

// Export all API functions
export default {
  createEntity,
  getEntity,
  listEntities,
  updateEntity,
  deleteEntity,
  createTag,
  getTags,
  deleteTag,
  createRelationship,
  getRelationships,
  deleteRelationship,
  searchSemantic,
  getContext,
  getGraph,
  getTagSummary
};
