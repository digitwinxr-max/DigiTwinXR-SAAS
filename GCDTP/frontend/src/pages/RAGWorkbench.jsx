/**
 * RAG Workbench Page
 * 
 * Retrieval-Augmented Generation interface.
 * This is read-only - NO operational writes.
 */

import React, { useState, useEffect } from 'react';
import { RAGChat } from '../components/RAGChat';
import { RAGSources } from '../components/RAGSources';
import { RAGContextPanel } from '../components/RAGContextPanel';
import { queryRAG, getModels } from '../api/rag';
import './RAGWorkbench.css';

export function RAGWorkbench() {
  // Messages state
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Context state
  const [currentContext, setCurrentContext] = useState(null);
  const [selectedQuery, setSelectedQuery] = useState(null);
  
  // Models state
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('template');
  
  // History state
  const [history, setHistory] = useState([]);

  // Load available models
  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const result = await getModels();
      setModels(result.available_models || []);
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  };

  const handleQuery = async (query) => {
    setLoading(true);
    try {
      const response = await queryRAG({
        query: query,
        session_id: 'default',
        model: selectedModel,
        entity_type: 'asset',
        entity_id: 'context'
      });
      
      // Add user message
      setMessages(prev => [
        ...prev,
        {
          id: `user-${Date.now()}`,
          role: 'user',
          message: query,
          timestamp: new Date()
        }
      ]);
      
      // Add assistant message
      setMessages(prev => [
        ...prev,
        {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          message: response.answer,
          timestamp: new Date(),
          confidence: response.confidence,
          model_name: response.model_name,
          chunks_used: response.sources?.length || 0
        }
      ]);
      
      // Update context
      setCurrentContext({
        ...response,
        sources: response.sources || []
      });
      
      // Add to history
      setHistory(prev => [
        {
          query_id: response.query_id,
          query: query,
          timestamp: new Date()
        },
        ...prev.slice(0, 9)
      ]);
      
    } catch (error) {
      console.error('Failed to query:', error);
    } finally {
      setLoading(false);
      setSelectedQuery(null);
    }
  };

  const handleHistoryClick = (item) => {
    setSelectedQuery(item.query);
  };

  const handleSourceClick = (source) => {
    console.log('Source clicked:', source);
  };

  return (
    <div className="rag-workbench">
      {/* Header */}
      <header className="workbench-header">
        <div className="header-left">
          <h1>🔍 RAG Workbench</h1>
          <span className="read-only-badge">READ ONLY</span>
        </div>
        <div className="header-right">
          <label>Model:</label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            {models.map(model => (
              <option 
                key={model.name} 
                value={model.name}
                disabled={model.status !== 'available'}
              >
                {model.name} {model.status === 'future' ? '(Future)' : ''}
              </option>
            ))}
          </select>
        </div>
      </header>

      <div className="workbench-layout">
        {/* Left Panel - History */}
        <aside className="workbench-sidebar left-panel">
          <div className="history-section">
            <h3>History</h3>
            {history.length === 0 ? (
              <p className="empty-history">No queries yet</p>
            ) : (
              <div className="history-list">
                {history.map((item, idx) => (
                  <div
                    key={idx}
                    className="history-item"
                    onClick={() => handleHistoryClick(item)}
                  >
                    <span className="history-query">{item.query}</span>
                    <span className="history-time">
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className="models-section">
            <h3>Available Models</h3>
            <div className="models-list">
              {models.map(model => (
                <div 
                  key={model.name} 
                  className={`model-item ${model.status}`}
                >
                  <span className="model-name">{model.name}</span>
                  <span className="model-status">
                    {model.status === 'available' ? '✓' : '○'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* Center Panel - Chat */}
        <main className="workbench-main">
          <RAGChat
            messages={messages}
            onQuery={handleQuery}
            loading={loading}
            selectedQuery={selectedQuery}
          />
        </main>

        {/* Right Panel - Sources & Context */}
        <aside className="workbench-sidebar right-panel">
          <div className="tabs">
            <button className="tab active">Sources</button>
            <button className="tab">Context</button>
          </div>
          
          <div className="panel-content">
            <RAGSources
              sources={currentContext?.sources || []}
              onSourceClick={handleSourceClick}
            />
          </div>
        </aside>
      </div>
    </div>
  );
}

export default RAGWorkbench;
