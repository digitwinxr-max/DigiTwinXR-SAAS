/**
 * RAG Chat Component
 * 
 * Chat interface for RAG-powered conversations.
 */

import React, { useState, useRef, useEffect } from 'react';
import { ConfidenceBadge } from './ConfidenceBadge';

export function RAGChat({ messages, onQuery, loading, selectedQuery }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load selected query
  useEffect(() => {
    if (selectedQuery) {
      setInput(selectedQuery);
    }
  }, [selectedQuery]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onQuery(input.trim());
      setInput('');
    }
  };

  const quickQuestions = [
    'Why is this asset degraded?',
    'What events affected this system?',
    'Show timeline of changes',
    'Which SOP applies here?'
  ];

  const formatTime = (date) => {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="rag-chat">
      {/* Chat Header */}
      <div className="chat-header">
        <h3>RAG Workbench</h3>
        <span className="read-only-badge">READ ONLY</span>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-state">
            <div className="welcome-icon">🔍</div>
            <h4>Retrieval-Augmented Generation</h4>
            <p>Ask questions about your digital twin system.</p>
            <p className="note">Context is retrieved from all platform engines.</p>
            
            <div className="quick-questions">
              <p>Sample questions:</p>
              {quickQuestions.map((question, idx) => (
                <button
                  key={idx}
                  className="quick-question-btn"
                  onClick={() => {
                    setInput(question);
                  }}
                  disabled={loading}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-header">
                  <span className="role">
                    {msg.role === 'user' ? '👤 You' : '🤖 RAG'}
                  </span>
                  {msg.timestamp && (
                    <span className="time">{formatTime(msg.timestamp)}</span>
                  )}
                </div>
                
                <div className="message-content">
                  <p>{msg.message || msg.answer}</p>
                  
                  {msg.role === 'assistant' && msg.confidence !== undefined && (
                    <ConfidenceBadge confidence={msg.confidence} />
                  )}
                  
                  {msg.role === 'assistant' && msg.chunks_used !== undefined && (
                    <span className="chunks-info">
                      {msg.chunks_used} context chunks used
                    </span>
                  )}
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="loading">
                <div className="spinner"></div>
                <span>Retrieving context...</span>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input">
        <form onSubmit={handleSubmit}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your system..."
            disabled={loading}
            rows={2}
          />
          <button type="submit" disabled={!input.trim() || loading}>
            {loading ? 'Processing...' : 'Ask'}
          </button>
        </form>
      </div>

      <style>{`
        .rag-chat {
          display: flex;
          flex-direction: column;
          height: 100%;
        }

        .chat-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background-color: #fff;
          border-bottom: 1px solid #e0e0e0;
        }

        .chat-header h3 {
          margin: 0;
          font-size: 1rem;
        }

        .read-only-badge {
          padding: 0.25rem 0.5rem;
          background-color: #e8f5e9;
          color: #2e7d32;
          border-radius: 4px;
          font-size: 0.625rem;
          font-weight: bold;
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
          background-color: #fafafa;
        }

        .welcome-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          text-align: center;
        }

        .welcome-icon {
          font-size: 4rem;
          margin-bottom: 1rem;
        }

        .welcome-state h4 {
          margin: 0 0 0.5rem 0;
          color: #333;
        }

        .welcome-state p {
          margin: 0.25rem 0;
          color: #666;
          font-size: 0.875rem;
        }

        .welcome-state .note {
          color: #2196f3;
          font-weight: bold;
        }

        .quick-questions {
          margin-top: 2rem;
          width: 100%;
          max-width: 400px;
        }

        .quick-questions p {
          margin-bottom: 0.5rem;
        }

        .quick-question-btn {
          display: block;
          width: 100%;
          padding: 0.5rem 1rem;
          margin: 0.5rem 0;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          background-color: #fff;
          cursor: pointer;
          font-size: 0.875rem;
          text-align: left;
          transition: all 0.15s;
        }

        .quick-question-btn:hover:not(:disabled) {
          border-color: #2196f3;
          background-color: #e3f2fd;
        }

        .message {
          margin-bottom: 1rem;
          max-width: 85%;
        }

        .message.user {
          margin-left: auto;
        }

        .message.assistant {
          margin-right: auto;
        }

        .message-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.25rem;
          padding: 0 0.5rem;
        }

        .role {
          font-size: 0.75rem;
          font-weight: bold;
          color: #666;
        }

        .message.user .role {
          color: #2196f3;
        }

        .message.assistant .role {
          color: #4caf50;
        }

        .time {
          font-size: 0.625rem;
          color: #999;
        }

        .message-content {
          padding: 0.75rem 1rem;
          border-radius: 12px;
        }

        .message.user .message-content {
          background-color: #2196f3;
          color: white;
          border-bottom-right-radius: 4px;
        }

        .message.assistant .message-content {
          background-color: #fff;
          border: 1px solid #e0e0e0;
          border-bottom-left-radius: 4px;
        }

        .message-content p {
          margin: 0;
          line-height: 1.5;
        }

        .chunks-info {
          display: block;
          margin-top: 0.5rem;
          font-size: 0.75rem;
          color: #666;
          font-style: italic;
        }

        .loading {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 1rem;
          color: #666;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid #e0e0e0;
          border-top-color: #2196f3;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .chat-input {
          padding: 1rem;
          background-color: #fff;
          border-top: 1px solid #e0e0e0;
        }

        .chat-input form {
          display: flex;
          gap: 0.5rem;
        }

        .chat-input textarea {
          flex: 1;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.875rem;
          resize: none;
        }

        .chat-input textarea:focus {
          outline: none;
          border-color: #2196f3;
        }

        .chat-input button {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 4px;
          background-color: #2196f3;
          color: white;
          cursor: pointer;
          font-weight: bold;
        }

        .chat-input button:disabled {
          background-color: #bdbdbd;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
}

export default RAGChat;
