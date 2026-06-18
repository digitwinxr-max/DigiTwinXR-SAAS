/**
 * Agent Workbench Page
 * 
 * AI Agent Framework with human approval workflow.
 * Agents propose - humans approve - execution follows.
 */

import React, { useState, useEffect } from 'react';
import { AgentList } from '../components/AgentList';
import { TaskQueue } from '../components/TaskQueue';
import { ApprovalPanel } from '../components/ApprovalPanel';
import { ExecutionHistory } from '../components/ExecutionHistory';
import {
  getAgents,
  getPendingTasks,
  createTask,
  approveTask,
  rejectTask,
  executeTask,
  getHistory
} from '../api/agent';
import './AgentWorkbench.css';

export function AgentWorkbench() {
  // State
  const [agents, setAgents] = useState([]);
  const [pendingTasks, setPendingTasks] = useState([]);
  const [history, setHistory] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [activeTab, setActiveTab] = useState('queue');
  const [loading, setLoading] = useState(false);

  // Load data on mount
  useEffect(() => {
    loadAgents();
    loadPendingTasks();
    loadHistory();
  }, []);

  const loadAgents = async () => {
    try {
      const response = await getAgents();
      setAgents(response.agents || []);
    } catch (error) {
      console.error('Failed to load agents:', error);
    }
  };

  const loadPendingTasks = async () => {
    try {
      const response = await getPendingTasks();
      setPendingTasks(response.tasks || []);
    } catch (error) {
      console.error('Failed to load pending tasks:', error);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await getHistory();
      setHistory(response.tasks || []);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const handleCreateTask = async () => {
    if (!selectedAgent) {
      alert('Please select an agent first');
      return;
    }

    setLoading(true);
    try {
      await createTask({
        agent_id: selectedAgent.id,
        task_type: 'diagnose',
        requested_by: 'operator',
        context_data: {
          entity_type: 'asset',
          entity_id: 'demo-asset',
          description: 'Analyze system health'
        }
      });
      
      // Reload tasks
      await loadPendingTasks();
      await loadHistory();
    } catch (error) {
      console.error('Failed to create task:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (taskId) => {
    setLoading(true);
    try {
      await approveTask(taskId, {
        approved_by: 'supervisor'
      });
      
      // Reload tasks
      await loadPendingTasks();
      await loadHistory();
      setSelectedTask(null);
    } catch (error) {
      console.error('Failed to approve task:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async (taskId) => {
    const reason = prompt('Enter rejection reason:');
    if (reason === null) return;
    
    setLoading(true);
    try {
      await rejectTask(taskId, {
        rejected_by: 'supervisor',
        reason: reason
      });
      
      // Reload tasks
      await loadPendingTasks();
      await loadHistory();
      setSelectedTask(null);
    } catch (error) {
      console.error('Failed to reject task:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async (taskId) => {
    setLoading(true);
    try {
      await executeTask(taskId, {
        executed_by: 'operator'
      });
      
      // Reload tasks
      await loadPendingTasks();
      await loadHistory();
      setSelectedTask(null);
    } catch (error) {
      console.error('Failed to execute task:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectTask = (task) => {
    setSelectedTask(task);
  };

  return (
    <div className="agent-workbench">
      {/* Header */}
      <header className="workbench-header">
        <div className="header-left">
          <h1>🤖 Agent Workbench</h1>
          <span className="approval-badge">Human Approval Required</span>
        </div>
        <div className="header-right">
          <button 
            className="create-task-btn"
            onClick={handleCreateTask}
            disabled={!selectedAgent || loading}
          >
            + Create Task
          </button>
        </div>
      </header>

      <div className="workbench-layout">
        {/* Left Panel - Agents */}
        <aside className="workbench-sidebar left-panel">
          <AgentList
            agents={agents}
            selectedAgent={selectedAgent}
            onSelectAgent={setSelectedAgent}
          />
        </aside>

        {/* Center Panel - Tasks */}
        <main className="workbench-main">
          <div className="tabs">
            <button 
              className={`tab ${activeTab === 'queue' ? 'active' : ''}`}
              onClick={() => setActiveTab('queue')}
            >
              Approval Queue ({pendingTasks.length})
            </button>
            <button 
              className={`tab ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              History ({history.length})
            </button>
          </div>

          <div className="center-content">
            {activeTab === 'queue' ? (
              <TaskQueue
                tasks={pendingTasks}
                onSelectTask={handleSelectTask}
                onApprove={handleApprove}
                onReject={handleReject}
              />
            ) : (
              <ExecutionHistory
                history={history}
                onSelectTask={handleSelectTask}
              />
            )}
          </div>
        </main>

        {/* Right Panel - Details */}
        <aside className="workbench-sidebar right-panel">
          <ApprovalPanel
            task={selectedTask}
            onApprove={handleApprove}
            onReject={handleReject}
            onExecute={handleExecute}
            onClose={() => setSelectedTask(null)}
          />
        </aside>
      </div>
    </div>
  );
}

export default AgentWorkbench;
