/**
 * Knowledge Repository API
 * 
 * Provides API functions for knowledge repository operations.
 * This is metadata only - NO AI, NO embeddings.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Document API
export async function createDocument(data) {
  const response = await fetch(`${API_BASE_URL}/knowledge/documents`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error('Failed to create document');
  }
  
  return response.json();
}

export async function listDocuments(options = {}) {
  const params = new URLSearchParams();
  
  if (options.category) params.append('category', options.category);
  if (options.document_type) params.append('document_type', options.document_type);
  if (options.limit) params.append('limit', options.limit);
  if (options.offset) params.append('offset', options.offset);
  
  const response = await fetch(`${API_BASE_URL}/knowledge/documents?${params}`);
  
  if (!response.ok) {
    throw new Error('Failed to list documents');
  }
  
  return response.json();
}

export async function getDocument(docId) {
  const response = await fetch(`${API_BASE_URL}/knowledge/document/${docId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get document');
  }
  
  return response.json();
}

export async function deleteDocument(docId) {
  const response = await fetch(`${API_BASE_URL}/knowledge/document/${docId}`, {
    method: 'DELETE'
  });
  
  if (!response.ok) {
    throw new Error('Failed to delete document');
  }
  
  return response.json();
}

// Reference API
export async function createReference(data) {
  const response = await fetch(`${API_BASE_URL}/knowledge/references`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error('Failed to create reference');
  }
  
  return response.json();
}

export async function getReferences(docId) {
  const response = await fetch(`${API_BASE_URL}/knowledge/references/${docId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get references');
  }
  
  return response.json();
}

// Search API
export async function searchDocuments(options = {}) {
  const params = new URLSearchParams();
  
  if (options.query) params.append('query', options.query);
  if (options.category) params.append('category', options.category);
  if (options.document_type) params.append('document_type', options.document_type);
  if (options.tags) params.append('tags', options.tags.join(','));
  if (options.author) params.append('author', options.author);
  if (options.limit) params.append('limit', options.limit);
  if (options.offset) params.append('offset', options.offset);
  
  const response = await fetch(`${API_BASE_URL}/knowledge/search?${params}`);
  
  if (!response.ok) {
    throw new Error('Failed to search documents');
  }
  
  return response.json();
}

// Category API
export async function getCategories() {
  const response = await fetch(`${API_BASE_URL}/knowledge/categories`);
  
  if (!response.ok) {
    throw new Error('Failed to get categories');
  }
  
  return response.json();
}

// Graph API
export async function getKnowledgeGraph(limit = 100) {
  const response = await fetch(`${API_BASE_URL}/knowledge/graph?limit=${limit}`);
  
  if (!response.ok) {
    throw new Error('Failed to get knowledge graph');
  }
  
  return response.json();
}

// Related Documents API
export async function getRelatedDocuments(docId) {
  const response = await fetch(`${API_BASE_URL}/knowledge/related/${docId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get related documents');
  }
  
  return response.json();
}

// Export all API functions
export default {
  createDocument,
  listDocuments,
  getDocument,
  deleteDocument,
  createReference,
  getReferences,
  searchDocuments,
  getCategories,
  getKnowledgeGraph,
  getRelatedDocuments
};
