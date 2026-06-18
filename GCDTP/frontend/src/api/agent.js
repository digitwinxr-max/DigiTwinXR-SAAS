/**
 * Agent API
 * 
 * Provides API functions for Agent Framework.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Agent APIs
export async function getAgents() {
  const response = await fetch(`${API_BASE_URL}/agent/agents`);
  if (!response.ok) throw new Error('Failed to get agents');
  return response.json();
}

export async function getAgent(agentId) {
  const response = await fetch(`${API_BASE_URL}/agent/agent/${agentId}`);
  if (!response.ok) throw new Error('Failed to get agent');
  return response.json();
}

// Task APIs
export async function createTask(data) {
  const response = await fetch(`${API_BASE_URL}/agent/task`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error('Failed to create task');
  return response.json();
}

export async function getTasks(options = {}) {
  const params = new URLSearchParams();
  if (options.agent_id) params.append('agent_id', options.agent_id);
  if (options.status) params.append('status', options.status);
  if (options.limit) params.append('limit', options.limit);
  if (options.offset) params.append('offset', options.offset);
  
  const response = await fetch(`${API_BASE_URL}/agent/tasks?${params}`);
  if (!response.ok) throw new Error('Failed to get tasks');
  return response.json();
}

export async function getTask(taskId) {
  const response = await fetch(`${API_BASE_URL}/agent/task/${taskId}`);
  if (!response.ok) throw new Error('Failed to get task');
  return response.json();
}

export async function approveTask(taskId, data) {
  const response = await fetch(`${API_BASE_URL}/agent/task/${taskId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error('Failed to approve task');
  return response.json();
}

export async function rejectTask(taskId, data) {
  const response = await fetch(`${API_BASE_URL}/agent/task/${taskId}/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error('Failed to reject task');
  return response.json();
}

export async function executeTask(taskId, data) {
  const response = await fetch(`${API_BASE_URL}/agent/task/${taskId}/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error('Failed to execute task');
  return response.json();
}

// Pending and History APIs
export async function getPendingTasks() {
  const response = await fetch(`${API_BASE_URL}/agent/pending`);
  if (!response.ok) throw new Error('Failed to get pending tasks');
  return response.json();
}

export async function getHistory(options = {}) {
  const params = new URLSearchParams();
  if (options.agent_id) params.append('agent_id', options.agent_id);
  if (options.limit) params.append('limit', options.limit);
  if (options.offset) params.append('offset', options.offset);
  
  const response = await fetch(`${API_BASE_URL}/agent/history?${params}`);
  if (!response.ok) throw new Error('Failed to get history');
  return response.json();
}

// Action APIs
export async function createAction(data) {
  const response = await fetch(`${API_BASE_URL}/agent/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error('Failed to create action');
  return response.json();
}

export async function getTaskActions(taskId) {
  const response = await fetch(`${API_BASE_URL}/agent/task/${taskId}/actions`);
  if (!response.ok) throw new Error('Failed to get task actions');
  return response.json();
}

// Stats APIs
export async function getStats() {
  const response = await fetch(`${API_BASE_URL}/agent/stats`);
  if (!response.ok) throw new Error('Failed to get stats');
  return response.json();
}

export default {
  getAgents,
  getAgent,
  createTask,
  getTasks,
  getTask,
  approveTask,
  rejectTask,
  executeTask,
  getPendingTasks,
  getHistory,
  createAction,
  getTaskActions,
  getStats
};
