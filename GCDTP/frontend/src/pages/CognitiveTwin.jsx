/**
 * Cognitive Twin Page
 * 
 * Convergence layer - aggregates context from all platform engines.
 * ADVISORY ONLY - explains, does not act.
 */

import React, { useState, useEffect } from 'react';
import { CognitiveChat } from '../components/CognitiveChat';
import { InsightGraph } from '../components/InsightGraph';
import { ContextSources } from '../components/ContextSources';
import { ExplanationPanel } from '../components/ExplanationPanel';
import { SessionHistory } from '../components/SessionHistory';
import {
  createSession,
  getSessions,
  askQuestion,
  getGraph
} from '../api/cognitive';
import './CognitiveTwin.css';

export function CognitiveTwin() {
  // State
  const [session, setSession] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [currentQuery, setCurrentQuery] = useState(null);
  const [loading, setLoading] = useState(false);

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const data = await getSessions(10);
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const handleCreateSession = async () => {
    setLoading(true);
    try {
      const newSession = await createSession({
        name: `Session ${sessions.length + 1}`,
        description: 'Cognitive Twin session'
      });
      setSession(newSession);
      await loadSessions();
    } catch (error) {
      console.error('Failed to create session:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendQuestion = async (question) => {
    if (!session) {
      await handleCreateSession();
    }

    setLoading(true);
    try {
      const result = await askQuestion(session?.id, { question });
      setCurrentQuery(result);
    } catch (error) {
      console.error('Failed to ask question:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSession = async (selectedSession) => {
    setSession(selectedSession);
    setCurrentQuery(null);
  };

  return (
    <div className="cognitive-twin">
      {/* Header */}
      <header className="page-header">
        <h1>🧠 Cognitive Twin</h1>
        <div className="header-badges">
          <span className="engine-badge">Convergence Layer</span>
          <span className="advisory-badge">ADVISORY ONLY</span>
        </div>
      </header>

      <div className="page-layout">
        {/* Left Panel - Sessions */}
        <aside className="left-panel">
          <SessionHistory 
            sessions={sessions}
            onSelectSession={handleSelectSession}
          />
          
          <button 
            className="new-session-btn"
            onClick={handleCreateSession}
            disabled={loading}
          >
            + New Session
          </button>
        </aside>

        {/* Center Panel - Chat & Results */}
        <main className="center-panel">
          <CognitiveChat 
            session={session}
            onSendQuestion={handleSendQuestion}
          />

          {currentQuery && (
            <div className="results-section">
              {/* Answer */}
              <div className="answer-card">
                <h3>Answer</h3>
                <p>{currentQuery.query?.answer}</p>
              </div>

              {/* Explanation */}
              <ExplanationPanel 
                explanation={currentQuery.query?.explanation}
                confidence={currentQuery.query?.confidence}
              />

              {/* Two Column */}
              <div className="two-column">
                {/* Context Sources */}
                <ContextSources context={currentQuery.context} />

                {/* Insight Graph */}
                <InsightGraph graph={currentQuery.graph} />
              </div>
            </div>
          )}
        </main>

        {/* Right Panel - Info */}
        <aside className="right-panel">
          <div className="info-panel">
            <h3>Cognitive Twin</h3>
            
            <div className="info-section">
              <h4>What I Explain</h4>
              <ul>
                <li>🔍 Why things happened (RCA)</li>
                <li>🔮 What might happen (Predictions)</li>
                <li>💚 Current health status</li>
                <li>📅 Historical patterns</li>
                <li>🔗 Dependencies</li>
                <li>📚 Knowledge context</li>
              </ul>
            </div>

            <div className="info-section">
              <h4>Context Sources</h4>
              <div className="source-tags">
                <span>Semantic</span>
                <span>Timeline</span>
                <span>Logbook</span>
                <span>Knowledge</span>
                <span>RAG</span>
                <span>Predictive</span>
                <span>Root Cause</span>
                <span>Agent</span>
                <span>Health</span>
                <span>Events</span>
              </div>
            </div>

            <div className="info-section">
              <h4>What I Do NOT Do</h4>
              <ul className="not-list">
                <li>❌ Change health</li>
                <li>❌ Modify events</li>
                <li>❌ Create work orders</li>
                <li>❌ Execute agents</li>
                <li>❌ Send notifications</li>
                <li>❌ Perform automation</li>
              </ul>
            </div>

            <div className="info-section">
              <h4>Confidence Score</h4>
              <p className="confidence-info">
                Based on context coverage, source diversity, and relevance.
                Higher confidence = more sources available.
              </p>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default CognitiveTwin;
