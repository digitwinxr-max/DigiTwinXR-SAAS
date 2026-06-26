/**
 * Cognitive Chat Component
 * 
 * Main chat interface for Cognitive Twin.
 */

import React, { useState } from 'react';

export function CognitiveChat({ session, onSendQuestion }) {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim()) {
      onSendQuestion(question);
      setQuestion('');
    }
  };

  return (
    <div className="cognitive-chat">
      <div className="chat-header">
        <h3>Cognitive Twin</h3>
        <span className="session-name">{session?.name || 'New Session'}</span>
      </div>

      <div className="chat-messages">
        <div className="welcome-message">
          <p>Ask me anything about your digital twin. I can explain:</p>
          <ul>
            <li>Why something happened (Root Cause Analysis)</li>
            <li>What might happen (Predictions)</li>
            <li>How things are connected (Dependencies)</li>
            <li>What happened over time (Timeline)</li>
          </ul>
          <p className="disclaimer">⚠️ Advisory only - I explain, I don't act.</p>
        </div>
      </div>

      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask the Cognitive Twin..."
          disabled={!session}
        />
        <button type="submit" disabled={!session || !question.trim()}>
          Send
        </button>
      </form>

      <style>{`
        .cognitive-chat {
          display: flex;
          flex-direction: column;
          height: 100%;
          background-color: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .chat-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border-bottom: 1px solid #e0e0e0;
        }

        .chat-header h3 {
          margin: 0;
          font-size: 1rem;
        }

        .session-name {
          font-size: 0.75rem;
          color: #666;
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
        }

        .welcome-message {
          background-color: #f5f5f5;
          padding: 1rem;
          border-radius: 8px;
        }

        .welcome-message p {
          margin: 0 0 0.5rem 0;
          font-size: 0.875rem;
        }

        .welcome-message ul {
          margin: 0 0 1rem 1.5rem;
          font-size: 0.875rem;
        }

        .welcome-message li {
          margin-bottom: 0.25rem;
        }

        .disclaimer {
          color: #666;
          font-size: 0.75rem;
          font-style: italic;
        }

        .chat-input {
          display: flex;
          gap: 0.5rem;
          padding: 1rem;
          border-top: 1px solid #e0e0e0;
        }

        .chat-input input {
          flex: 1;
          padding: 0.75rem;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          font-size: 0.875rem;
        }

        .chat-input input:focus {
          outline: none;
          border-color: #1976d2;
        }

        .chat-input button {
          padding: 0.75rem 1.5rem;
          background-color: #1976d2;
          color: white;
          border: none;
          border-radius: 4px;
          font-weight: bold;
          cursor: pointer;
        }

        .chat-input button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
}

export default CognitiveChat;
