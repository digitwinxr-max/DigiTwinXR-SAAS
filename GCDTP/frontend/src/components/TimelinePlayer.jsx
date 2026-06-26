/**
 * Timeline Player Component
 * 
 * Provides playback controls for timeline replay.
 * Timeline Replay is read-only.
 */

import React from 'react';

export function TimelinePlayer({
  isPlaying,
  currentFrame,
  totalFrames,
  playbackSpeed,
  onPlay,
  onPause,
  onStepForward,
  onStepBackward,
  onJumpToTime,
  onSliderChange,
  onSpeedChange,
  frames = []
}) {
  const currentTimestamp = frames[currentFrame]?.timestamp;
  
  return (
    <div className="timeline-player">
      <h3>Playback Controls</h3>
      
      {/* Timestamp Display */}
      <div className="timestamp-display">
        {currentTimestamp ? (
          <>
            <span className="timestamp-date">
              {new Date(currentTimestamp).toLocaleDateString()}
            </span>
            <span className="timestamp-time">
              {new Date(currentTimestamp).toLocaleTimeString()}
            </span>
          </>
        ) : (
          <span className="no-timestamp">No frame selected</span>
        )}
      </div>
      
      {/* Main Controls */}
      <div className="main-controls">
        <button
          className="control-btn"
          onClick={onStepBackward}
          disabled={currentFrame <= 0}
          title="Step Backward"
        >
          ⏮
        </button>
        
        {isPlaying ? (
          <button
            className="control-btn play-btn"
            onClick={onPause}
            title="Pause"
          >
            ⏸
          </button>
        ) : (
          <button
            className="control-btn play-btn"
            onClick={onPlay}
            disabled={currentFrame >= totalFrames - 1}
            title="Play"
          >
            ▶
          </button>
        )}
        
        <button
          className="control-btn"
          onClick={onStepForward}
          disabled={currentFrame >= totalFrames - 1}
          title="Step Forward"
        >
          ⏭
        </button>
      </div>
      
      {/* Frame Slider */}
      <div className="slider-container">
        <input
          type="range"
          className="frame-slider"
          min="0"
          max={totalFrames - 1}
          value={currentFrame}
          onChange={(e) => onSliderChange(e.target.value)}
          disabled={totalFrames === 0}
        />
        <div className="slider-labels">
          <span>0</span>
          <span>{totalFrames}</span>
        </div>
      </div>
      
      {/* Speed Controls */}
      <div className="speed-controls">
        <span className="speed-label">Speed:</span>
        <div className="speed-buttons">
          {[1, 2, 5, 10].map(speed => (
            <button
              key={speed}
              className={`speed-btn ${playbackSpeed === speed ? 'active' : ''}`}
              onClick={() => onSpeedChange(speed)}
            >
              {speed}x
            </button>
          ))}
        </div>
      </div>
      
      {/* Frame Counter */}
      <div className="frame-counter">
        <span>Frame</span>
        <span className="current-frame">{currentFrame + 1}</span>
        <span>of</span>
        <span className="total-frames">{totalFrames}</span>
      </div>
      
      {/* Jump to Time */}
      <div className="jump-controls">
        <h4>Jump To</h4>
        <div className="jump-buttons">
          <button
            className="jump-btn"
            onClick={() => onJumpToTime?.('start')}
            title="Jump to Start"
          >
            ⏮ Start
          </button>
          <button
            className="jump-btn"
            onClick={() => onJumpToTime?.('end')}
            title="Jump to End"
          >
            End ⏭
          </button>
        </div>
      </div>
      
      <style>{`
        .timeline-player {
          padding: 1rem;
          background-color: #fafafa;
          border-radius: 8px;
          border: 1px solid #e0e0e0;
        }
        
        .timeline-player h3 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
          color: #333;
        }
        
        .timestamp-display {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 1rem;
          background-color: #fff;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          margin-bottom: 1rem;
        }
        
        .timestamp-date {
          font-size: 0.875rem;
          color: #666;
        }
        
        .timestamp-time {
          font-size: 1.5rem;
          font-weight: bold;
          color: #333;
        }
        
        .no-timestamp {
          font-size: 0.875rem;
          color: #999;
        }
        
        .main-controls {
          display: flex;
          justify-content: center;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }
        
        .control-btn {
          width: 48px;
          height: 48px;
          border: none;
          border-radius: 50%;
          background-color: #e0e0e0;
          color: #333;
          font-size: 1.25rem;
          cursor: pointer;
          transition: all 0.15s;
        }
        
        .control-btn:hover:not(:disabled) {
          background-color: #bdbdbd;
        }
        
        .control-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .play-btn {
          width: 64px;
          height: 64px;
          font-size: 1.5rem;
          background-color: #2196f3;
          color: #fff;
        }
        
        .play-btn:hover:not(:disabled) {
          background-color: #1976d2;
        }
        
        .slider-container {
          margin-bottom: 1rem;
        }
        
        .frame-slider {
          width: 100%;
          height: 8px;
          border-radius: 4px;
          background: #e0e0e0;
          appearance: none;
          cursor: pointer;
        }
        
        .frame-slider::-webkit-slider-thumb {
          appearance: none;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: #2196f3;
          cursor: pointer;
        }
        
        .frame-slider::-moz-range-thumb {
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: #2196f3;
          cursor: pointer;
          border: none;
        }
        
        .slider-labels {
          display: flex;
          justify-content: space-between;
          font-size: 0.75rem;
          color: #666;
          margin-top: 0.25rem;
        }
        
        .speed-controls {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }
        
        .speed-label {
          font-size: 0.75rem;
          color: #666;
        }
        
        .speed-buttons {
          display: flex;
          gap: 0.25rem;
        }
        
        .speed-btn {
          padding: 0.25rem 0.5rem;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          background-color: #fff;
          color: #333;
          font-size: 0.75rem;
          cursor: pointer;
        }
        
        .speed-btn:hover {
          background-color: #f5f5f5;
        }
        
        .speed-btn.active {
          background-color: #2196f3;
          color: #fff;
          border-color: #2196f3;
        }
        
        .frame-counter {
          display: flex;
          justify-content: center;
          align-items: baseline;
          gap: 0.5rem;
          margin-bottom: 1rem;
          font-size: 0.875rem;
          color: #666;
        }
        
        .current-frame {
          font-size: 1.5rem;
          font-weight: bold;
          color: #2196f3;
        }
        
        .total-frames {
          font-weight: bold;
        }
        
        .jump-controls {
          border-top: 1px solid #e0e0e0;
          padding-top: 1rem;
        }
        
        .jump-controls h4 {
          margin: 0 0 0.5rem 0;
          font-size: 0.875rem;
          color: #666;
        }
        
        .jump-buttons {
          display: flex;
          gap: 0.5rem;
        }
        
        .jump-btn {
          flex: 1;
          padding: 0.5rem;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          background-color: #fff;
          color: #333;
          font-size: 0.75rem;
          cursor: pointer;
        }
        
        .jump-btn:hover {
          background-color: #f5f5f5;
        }
      `}</style>
    </div>
  );
}

export default TimelinePlayer;
