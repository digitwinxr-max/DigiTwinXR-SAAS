/**
 * Copilot Chat Component
 * 
 * Conversation window for copilot interaction.
 */

import React, { useState, useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';

export function CopilotChat({ session, messages, onQuery, loading, contextEntity }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onQuery(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const quickQuestions = [
    'What is the health status?',
    'Show me active events',
    'Summarize the timeline',
    'What documents are related?'
  ];

  return (
    <div className="copilot-chat">
      {/* Chat Header */}
      <div className="chat-header">
        <h3>
          {session ? session.session_name : 'New Conversation'}
        </h3>
        {contextEntity && (
          <span className="context-indicator">
            Context: {contextEntity.type}/{contextEntity.id}
          </span>
        )}
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-state">
            <div className="welcome-icon">🧠</div>
            <h4>Welcome to Cognitive Copilot</h4>
            <p>This AI assistant provides explanations and context.</p>
            <p className="read-only-note">READ ONLY - No actions will be performed.</p>
            
            <div className="quick-questions">
              <p>Quick questions:</p>
              {quickQuestions.map((question, idx) => (
                <button
                  key={idx}
                  className="quick-question-btn"
                  onClick={() => onQuery(question)}
                  disabled={loading}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
              />
            ))}
            {loading && (
              <div className="loading-indicator">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span>Thinking...</span>
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
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about the system..."
            disabled={loading}
            rows={2}
          />
          <button type="submit" disabled={!input.trim() || loading}>
            {loading ? 'Thinking...' : 'Send'}
          </button>
        </form>
      </div>

      <style>{`
        .copilot-chat {
          display: flex;
          flex-direction: column;
          height: 100%;
        }

        .chat-header {
          padding: 1rem;
          background-color: #fff;
          border-bottom: 1px solid #e0e0e0;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .chat-header h3 {
          margin: 0;
          font-size: 1rem;
          color: #333;
        }

        .context-indicator {
          font-size: 0.75rem;
          color: #666;
          padding: 0.25rem 0.5rem;
          background-color: #f5f5f5;
          border-radius: 4px;
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
          color: #666;
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
          font-size: 0.875rem;
        }

        .read-only-note {
          color: #2e7d32;
          font-weight: bold;
          margin-top: 0.5rem !important;
        }

        .quick-questions {
          margin-top: 2rem;
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
          color: #333;
          cursor: pointer;
          font-size: 0.875rem;
          text-align: left;
          transition: all 0.15s;
        }

        .quick-question-btn:hover:not(:disabled) {
          border-color: #2196f3;
          background-color: #e3f2fd;
        }

        .quick-question-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .loading-indicator {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 1rem;
          color: #666;
          font-size: 0.875rem;
        }

        .typing-indicator {
          display: flex;
          gap: 0.25rem;
        }

        .typing-indicator span {
          width: 8px;
          height: 8px;
          background-color: #2196f3;
          border-radius: 50%;
          animation: typing 1.4s infinite;
        }

        .typing-indicator span:nth-child(2) {
          animation-delay: 0.2s;
        }

        .typing-indicator span:nth-child(3) {
          animation-delay: 0.4s;
        }

        @keyframes typing {
          0%, 60%, 100% {
            transform: translateY(0);
          }
          30% {
            transform: translateY(-4px);
          }
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
          font-family: inherit;
          resize: none;
        }

        .chat-input textarea:focus {
          outline: none;
          border-color: #2196f3;
        }

        .chat-input textarea:disabled {
          background-color: #f5f5f5;
        }

        .chat-input button {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 4px;
          background-color: #2196f3;
          color: white;
          cursor: pointer;
          font-size: 0.875rem;
          font-weight: bold;
        }

        .chat-input button:hover:not(:disabled) {
          background-color: #1976d2;
        }

        .chat-input button:disabled {
          background-color: #bdbdbd;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
}

export default CopilotChat;
