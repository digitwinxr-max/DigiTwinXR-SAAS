/**
 * API client for Asset Relationships
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';


/**
 * Relationship types
 */
export const RELATIONSHIP_TYPES = {
  CONTAINS: 'contains',
  CONNECTED_TO: 'connected_to',
  FEEDS: 'feeds',
  MONITORS: 'monitors',
  CONTROLS: 'controls',
};


/**
 * Relationship type labels and colors
 */
export const RELATIONSHIP_TYPE_INFO = {
  [RELATIONSHIP_TYPES.CONTAINS]: {
    label: 'Contains',
    color: '#3b82f6',
    lineStyle: 'solid',
  },
  [RELATIONSHIP_TYPES.CONNECTED_TO]: {
    label: 'Connected To',
    color: '#6b7280',
    lineStyle: 'dashed',
  },
  [RELATIONSHIP_TYPES.FEEDS]: {
    label: 'Feeds',
    color: '#22c55e',
    lineStyle: 'arrow',
  },
  [RELATIONSHIP_TYPES.MONITORS]: {
    label: 'Monitors',
    color: '#8b5cf6',
    lineStyle: 'dotted',
  },
  [RELATIONSHIP_TYPES.CONTROLS]: {
    label: 'Controls',
    color: '#f97316',
    lineStyle: 'bold',
  },
};


/**
 * Get all relationships
 * @param {Object} params - Query parameters
 * @param {number} params.skip - Skip count
 * @param {number} params.limit - Limit count
 * @param {string} params.parent_asset_id - Filter by parent
 * @param {string} params.child_asset_id - Filter by child
 * @param {string} params.relationship_type - Filter by type
 * @returns {Promise<Object>} Paginated relationship list
 */
export async function getRelationships(params = {}) {
  const searchParams = new URLSearchParams();
  
  if (params.skip !== undefined) searchParams.set('skip', params.skip);
  if (params.limit !== undefined) searchParams.set('limit', params.limit);
  if (params.parent_asset_id) searchParams.set('parent_asset_id', params.parent_asset_id);
  if (params.child_asset_id) searchParams.set('child_asset_id', params.child_asset_id);
  if (params.relationship_type) searchParams.set('relationship_type', params.relationship_type);
  
  const response = await fetch(`${API_BASE_URL}/relationships?${searchParams}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch relationships: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get a single relationship by ID
 * @param {string} relationshipId - Relationship ID
 * @returns {Promise<Object>} Relationship details
 */
export async function getRelationship(relationshipId) {
  const response = await fetch(`${API_BASE_URL}/relationships/${relationshipId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch relationship: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Create a new relationship
 * @param {Object} data - Relationship data
 * @param {string} data.parent_asset_id - Parent asset ID
 * @param {string} data.child_asset_id - Child asset ID
 * @param {string} data.relationship_type - Relationship type
 * @returns {Promise<Object>} Created relationship
 */
export async function createRelationship(data) {
  const response = await fetch(`${API_BASE_URL}/relationships`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Failed to create relationship: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Delete a relationship
 * @param {string} relationshipId - Relationship ID
 * @returns {Promise<Object>} Delete confirmation
 */
export async function deleteRelationship(relationshipId) {
  const response = await fetch(`${API_BASE_URL}/relationships/${relationshipId}`, {
    method: 'DELETE',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to delete relationship: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get relationship graph for an asset
 * @param {string} assetId - Asset ID
 * @param {string} direction - 'up', 'down', or 'both'
 * @param {number} maxDepth - Maximum graph depth
 * @returns {Promise<Object>} Graph data
 */
export async function getGraph(assetId, direction = 'down', maxDepth = 10) {
  const searchParams = new URLSearchParams();
  searchParams.set('direction', direction);
  searchParams.set('max_depth', maxDepth);
  
  const response = await fetch(
    `${API_BASE_URL}/relationships/graph/${assetId}?${searchParams}`
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch graph: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get children of an asset
 * @param {string} assetId - Asset ID
 * @param {string} relationshipType - Optional type filter
 * @returns {Promise<Array>} List of children
 */
export async function getChildren(assetId, relationshipType = null) {
  const searchParams = new URLSearchParams();
  if (relationshipType) {
    searchParams.set('relationship_type', relationshipType);
  }
  
  const url = relationshipType
    ? `${API_BASE_URL}/relationships/children/${assetId}?${searchParams}`
    : `${API_BASE_URL}/relationships/children/${assetId}`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch children: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get parents of an asset
 * @param {string} assetId - Asset ID
 * @param {string} relationshipType - Optional type filter
 * @returns {Promise<Array>} List of parents
 */
export async function getParents(assetId, relationshipType = null) {
  const searchParams = new URLSearchParams();
  if (relationshipType) {
    searchParams.set('relationship_type', relationshipType);
  }
  
  const url = relationshipType
    ? `${API_BASE_URL}/relationships/parents/${assetId}?${searchParams}`
    : `${API_BASE_URL}/relationships/parents/${assetId}`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch parents: ${response.statusText}`);
  }
  
  return response.json();
}


/**
 * Get available relationship types
 * @returns {Promise<Array>} List of relationship types
 */
export async function getRelationshipTypes() {
  const response = await fetch(`${API_BASE_URL}/relationships/types`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch types: ${response.statusText}`);
  }
  
  return response.json();
}


export default {
  getRelationships,
  getRelationship,
  createRelationship,
  deleteRelationship,
  getGraph,
  getChildren,
  getParents,
  getRelationshipTypes,
  RELATIONSHIP_TYPES,
  RELATIONSHIP_TYPE_INFO,
};