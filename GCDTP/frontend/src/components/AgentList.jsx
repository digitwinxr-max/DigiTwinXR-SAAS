/**
 * Agent List Component
 * 
 * Displays available agents with capabilities.
 */

import React from 'react';

export function AgentList({ agents, selectedAgent, onSelectAgent }) {
  const getAgentIcon = (type) => {
    const icons = {
      diagnostic_agent: '🔍',
      maintenance_agent: '🔧',
      recovery_agent: '🔄',
      knowledge_agent: '📚',
      timeline_agent: '⏱️'
    };
    return icons[type] || '🤖';
  };

  const getTypeLabel = (type) => {
    return type.replace('_agent', '').replace('_', ' ');
  };

  return (
    <div className="agent-list">
      <div className="list-header">
        <h3>Available Agents</h3>
        <span className="count">{agents.length}</span>
      </div>

      <div className="agents">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`agent-item ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
            onClick={() => onSelectAgent(agent)}
          >
            <div className="agent-icon">
              {getAgentIcon(agent.agent_type)}
            </div>
            <div className="agent-info">
              <span className="agent-name">{agent.name}</span>
              <span className="agent-type">{getTypeLabel(agent.agent_type)}</span>
            </div>
            {!agent.enabled && (
              <span className="disabled-badge">Disabled</span>
            )}
          </div>
        ))}
      </div>

      <style>{`
        .agent-list {
          display: flex;
          flex-direction: column;
          height: 100%;
        }

        .list-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border-bottom: 1px solid #e0e0e0;
        }

        .list-header h3 {
          margin: 0;
          font-size: 1rem;
        }

        .count {
          font-size: 0.75rem;
          color: #666;
          background-color: #f5f5f5;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
        }

        .agents {
          flex: 1;
          overflow-y: auto;
          padding: 0.5rem;
        }

        .agent-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          margin-bottom: 0.5rem;
          cursor: pointer;
          transition: all 0.15s;
        }

        .agent-item:hover {
          border-color: #2196f3;
          background-color: #f5f5f5;
        }

        .agent-item.selected {
          border-color: #2196f3;
          background-color: #e3f2fd;
        }

        .agent-icon {
          font-size: 1.5rem;
        }

        .agent-info {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .agent-name {
          font-size: 0.875rem;
          font-weight: 600;
          color: #333;
        }

        .agent-type {
          font-size: 0.75rem;
          color: #666;
          text-transform: capitalize;
        }

        .disabled-badge {
          font-size: 0.625rem;
          padding: 0.125rem 0.375rem;
          background-color: #ffebee;
          color: #c62828;
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
}

export default AgentList;
