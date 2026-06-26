/**
 * Cognitive Copilot Page
 * 
 * AI context and explanations for the platform.
 * This is read-only - NO actions, NO modifications.
 */

import React, { useState, useEffect } from 'react';
import { CopilotChat } from '../components/CopilotChat';
import { ContextPanel } from '../components/ContextPanel';
import { SessionList } from '../components/SessionList';
import {
  createSession,
  listSessions,
  queryCopilot,
  getContext
} from '../api/copilot';
import './CognitiveCopilot.css';

export function CognitiveCopilot() {
  // Session state
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  
  // Context state
  const [contextEntity, setContextEntity] = useState(null);
  const [contextData, setContextData] = useState(null);
  
  // Loading state
  const [loading, setLoading] = useState(false);

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const sessionList = await listSessions();
      setSessions(sessionList || []);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const handleCreateSession = async (name) => {
    try {
      const session = await createSession(name || `Session ${sessions.length + 1}`);
      setSessions([session, ...sessions]);
      setCurrentSession(session);
      setMessages([]);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const handleSelectSession = (session) => {
    setCurrentSession(session);
  };

  const handleQuery = async (query) => {
    if (!currentSession) {
      await handleCreateSession();
    }
    
    setLoading(true);
    try {
      const response = await queryCopilot(
        currentSession.id,
        query,
        contextEntity?.type,
        contextEntity?.id
      );
      
      // Add messages
      setMessages(prev => [
        ...prev,
        {
          id: `user-${Date.now()}`,
          role: 'user',
          message: query,
          timestamp: new Date()
        },
        {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          message: response.answer.answer,
          context_used: response.answer.context_used,
          sources: response.answer.sources,
          suggestions: response.answer.suggestions,
          timestamp: new Date()
        }
      ]);
      
      // Update context if provided
      if (response.context) {
        setContextData(response.context);
      }
    } catch (error) {
      console.error('Failed to query:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSetContext = async (type, id) => {
    setContextEntity({ type, id });
    try {
      const context = await getContext(type, id);
      setContextData(context.bundle);
    } catch (error) {
      console.error('Failed to load context:', error);
    }
  };

  const handleClearContext = () => {
    setContextEntity(null);
    setContextData(null);
  };

  return (
    <div className="cognitive-copilot">
      {/* Header */}
      <header className="copilot-header">
        <h1>🧠 Cognitive Copilot</h1>
        <div className="header-info">
          <span className="read-only-badge">READ ONLY</span>
          <span className="ai-note">AI Context Only - No Actions</span>
        </div>
      </header>

      <div className="copilot-layout">
        {/* Left Panel - Sessions */}
        <aside className="copilot-sidebar left-panel">
          <SessionList
            sessions={sessions}
            currentSession={currentSession}
            onSelect={handleSelectSession}
            onCreate={handleCreateSession}
          />
        </aside>

        {/* Center Panel - Chat */}
        <main className="copilot-main">
          <CopilotChat
            session={currentSession}
            messages={messages}
            onQuery={handleQuery}
            loading={loading}
            contextEntity={contextEntity}
          />
        </main>

        {/* Right Panel - Context */}
        <aside className="copilot-sidebar right-panel">
          <ContextPanel
            entity={contextEntity}
            context={contextData}
            onSetContext={handleSetContext}
            onClearContext={handleClearContext}
          />
        </aside>
      </div>
    </div>
  );
}

export default CognitiveCopilot;
