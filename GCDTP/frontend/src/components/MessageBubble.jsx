/**
 * Message Bubble Component
 * 
 * Displays a single chat message.
 */

import React from 'react';

export function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-header">
        <span className="message-role">
          {isUser ? '👤 You' : '🧠 Copilot'}
        </span>
        <span className="message-time">{formatTime(message.timestamp)}</span>
      </div>
      
      <div className="message-content">
        <p>{message.message}</p>
      </div>
      
      {isAssistant && message.context_used && message.context_used.length > 0 && (
        <div className="message-meta">
          <span className="sources">
            Sources: {message.sources?.join(', ') || 'N/A'}
          </span>
        </div>
      )}
      
      {isAssistant && message.suggestions && message.suggestions.length > 0 && (
        <div className="message-suggestions">
          <span className="suggestions-label">Suggestions:</span>
          {message.suggestions.map((suggestion, idx) => (
            <span key={idx} className="suggestion">{suggestion}</span>
          ))}
        </div>
      )}
      
      <style>{`
        .message-bubble {
          margin-bottom: 1rem;
          max-width: 85%;
        }
        
        .message-bubble.user {
          margin-left: auto;
        }
        
        .message-bubble.assistant {
          margin-right: auto;
        }
        
        .message-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.25rem;
          padding: 0 0.5rem;
        }
        
        .message-role {
          font-size: 0.75rem;
          font-weight: bold;
          color: #666;
        }
        
        .message-bubble.user .message-role {
          color: #2196f3;
        }
        
        .message-bubble.assistant .message-role {
          color: #4caf50;
        }
        
        .message-time {
          font-size: 0.625rem;
          color: #999;
        }
        
        .message-content {
          padding: 0.75rem 1rem;
          border-radius: 12px;
          line-height: 1.5;
        }
        
        .message-bubble.user .message-content {
          background-color: #2196f3;
          color: white;
          border-bottom-right-radius: 4px;
        }
        
        .message-bubble.assistant .message-content {
          background-color: #fff;
          color: #333;
          border: 1px solid #e0e0e0;
          border-bottom-left-radius: 4px;
        }
        
        .message-content p {
          margin: 0;
          font-size: 0.875rem;
        }
        
        .message-meta {
          padding: 0.5rem;
          margin-top: 0.25rem;
          font-size: 0.75rem;
          color: #666;
        }
        
        .message-meta .sources {
          font-style: italic;
        }
        
        .message-suggestions {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          padding: 0.5rem;
          margin-top: 0.25rem;
          background-color: #f5f5f5;
          border-radius: 8px;
        }
        
        .suggestions-label {
          font-size: 0.75rem;
          color: #666;
          font-weight: bold;
        }
        
        .suggestion {
          font-size: 0.75rem;
          padding: 0.25rem 0.5rem;
          background-color: #e3f2fd;
          color: #1565c0;
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
}

export default MessageBubble;
