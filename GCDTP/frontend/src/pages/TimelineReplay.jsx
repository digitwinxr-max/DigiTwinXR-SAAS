/**
 * Timeline Replay Page
 * 
 * Provides temporal replay capabilities across the platform.
 * Timeline Replay is read-only.
 */

import React, { useState, useEffect } from 'react';
import { TimelinePlayer } from '../components/TimelinePlayer';
import { TimelineOverlay } from '../components/TimelineOverlay';
import {
  getRange,
  playback,
  getSystem
} from '../api/timeline';
import { getEntriesByTimeline } from '../api/logbook';
import './TimelineReplay.css';

export function TimelineReplay() {
  // Time range state
  const [startTime, setStartTime] = useState(getDefaultStartTime());
  const [endTime, setEndTime] = useState(getDefaultEndTime());
  
  // Playback state
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [frames, setFrames] = useState([]);
  
  // Selected frame details
  const [selectedFrame, setSelectedFrame] = useState(null);
  
  // Logbook entries for current frame
  const [logbookEntries, setLogbookEntries] = useState([]);
  
  // Loading state
  const [loading, setLoading] = useState(false);

  // Load frames on mount or time range change
  useEffect(() => {
    loadFrames();
  }, []);

  const loadFrames = async () => {
    setLoading(true);
    try {
      const result = await playback(
        startTime.toISOString(),
        endTime.toISOString(),
        { frame_interval: 60 }
      );
      setFrames(result.frames || []);
    } catch (error) {
      console.error('Failed to load frames:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePlay = () => {
    setIsPlaying(true);
  };

  const handlePause = () => {
    setIsPlaying(false);
  };

  const handleStepForward = () => {
    if (currentFrame < frames.length - 1) {
      setCurrentFrame(currentFrame + 1);
    }
  };

  const handleStepBackward = () => {
    if (currentFrame > 0) {
      setCurrentFrame(currentFrame - 1);
    }
  };

  const handleJumpToTime = (timestamp) => {
    const frameIndex = frames.findIndex(
      f => new Date(f.timestamp).getTime() === new Date(timestamp).getTime()
    );
    if (frameIndex >= 0) {
      setCurrentFrame(frameIndex);
    }
  };

  const handleSliderChange = (value) => {
    setCurrentFrame(parseInt(value, 10));
  };

  const handleFrameSelect = (index) => {
    setCurrentFrame(index);
    setSelectedFrame(frames[index]);
  };

  // Update selected frame when current frame changes
  useEffect(() => {
    if (frames[currentFrame]) {
      setSelectedFrame(frames[currentFrame]);
    }
  }, [currentFrame, frames]);

  // Load logbook entries for current frame
  useEffect(() => {
    if (selectedFrame) {
      loadLogbookEntries();
    }
  }, [selectedFrame]);

  const loadLogbookEntries = async () => {
    if (!selectedFrame?.timestamp) return;
    
    try {
      // Find entries with timeline reference
      const entries = await getEntriesByTimeline(selectedFrame.timestamp);
      setLogbookEntries(entries.entries || []);
    } catch (error) {
      console.error('Failed to load logbook entries:', error);
      setLogbookEntries([]);
    }
  };

  // Playback loop
  useEffect(() => {
    if (!isPlaying) return;
    
    const interval = setInterval(() => {
      setCurrentFrame(prev => {
        if (prev >= frames.length - 1) {
          setIsPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, 1000 / playbackSpeed);
    
    return () => clearInterval(interval);
  }, [isPlaying, playbackSpeed, frames.length]);

  return (
    <div className="timeline-replay">
      {/* Header */}
      <header className="replay-header">
        <h1>Timeline Replay</h1>
        <div className="header-info">
          {frames.length > 0 && (
            <span>
              Frame {currentFrame + 1} of {frames.length}
            </span>
          )}
        </div>
      </header>

      <div className="replay-layout">
        {/* Left Panel - Controls */}
        <aside className="replay-sidebar left-panel">
          <TimeRangeSelector
            startTime={startTime}
            endTime={endTime}
            onStartChange={setStartTime}
            onEndChange={setEndTime}
            onApply={loadFrames}
          />
          
          <TimelinePlayer
            isPlaying={isPlaying}
            currentFrame={currentFrame}
            totalFrames={frames.length}
            playbackSpeed={playbackSpeed}
            onPlay={handlePlay}
            onPause={handlePause}
            onStepForward={handleStepForward}
            onStepBackward={handleStepBackward}
            onJumpToTime={handleJumpToTime}
            onSliderChange={handleSliderChange}
            onSpeedChange={setPlaybackSpeed}
            frames={frames}
          />
        </aside>

        {/* Center Panel - Timeline Frames */}
        <main className="replay-main">
          {loading ? (
            <div className="loading">Loading timeline...</div>
          ) : frames.length === 0 ? (
            <div className="empty-state">
              <p>No timeline frames available</p>
              <p>Adjust the time range and click Apply</p>
            </div>
          ) : (
            <div className="frames-list">
              <h3>Timeline Frames</h3>
              {frames.map((frame, index) => (
                <FrameCard
                  key={index}
                  frame={frame}
                  index={index}
                  isActive={index === currentFrame}
                  isSelected={selectedFrame === frame}
                  onClick={() => handleFrameSelect(index)}
                />
              ))}
            </div>
          )}
        </main>

        {/* Right Panel - Frame Details */}
        <aside className="replay-sidebar right-panel">
          <FrameDetails frame={selectedFrame} logbookEntries={logbookEntries} />
        </aside>
      </div>

      {/* Timeline Overlay */}
      <TimelineOverlay
        frame={selectedFrame}
        isActive={!isPlaying}
      />
    </div>
  );
}

// Time Range Selector Component
function TimeRangeSelector({
  startTime,
  endTime,
  onStartChange,
  onEndChange,
  onApply
}) {
  return (
    <div className="time-range-selector">
      <h3>Time Range</h3>
      
      <div className="range-field">
        <label>Start Time</label>
        <input
          type="datetime-local"
          value={formatDateTimeLocal(startTime)}
          onChange={(e) => onStartChange(new Date(e.target.value))}
        />
      </div>
      
      <div className="range-field">
        <label>End Time</label>
        <input
          type="datetime-local"
          value={formatDateTimeLocal(endTime)}
          onChange={(e) => onEndChange(new Date(e.target.value))}
        />
      </div>
      
      <button onClick={onApply} className="apply-btn">
        Apply Range
      </button>
      
      <div className="quick-ranges">
        <h4>Quick Select</h4>
        <button onClick={() => {
          onStartChange(getDefaultStartTime());
          onEndChange(getDefaultEndTime());
        }}>
          Last 24 Hours
        </button>
        <button onClick={() => {
          onStartChange(getDefaultStartTime());
          onEndChange(getDefaultEndTime());
        }}>
          Last 7 Days
        </button>
        <button onClick={() => {
          onStartChange(getDefaultStartTime());
          onEndChange(getDefaultEndTime());
        }}>
          Last 30 Days
        </button>
      </div>
    </div>
  );
}

// Frame Card Component
function FrameCard({ frame, index, isActive, isSelected, onClick }) {
  const timestamp = new Date(frame.timestamp);
  
  return (
    <div
      className={`frame-card ${isActive ? 'active' : ''} ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="frame-header">
        <span className="frame-index">#{index + 1}</span>
        <span className="frame-time">
          {timestamp.toLocaleString()}
        </span>
      </div>
      
      {frame.events && frame.events.length > 0 && (
        <div className="frame-events">
          {frame.events.slice(0, 3).map((event, idx) => (
            <span
              key={idx}
              className={`event-badge ${event.severity?.toLowerCase() || 'unknown'}`}
            >
              {event.message || 'Event'}
            </span>
          ))}
          {frame.events.length > 3 && (
            <span className="more-events">
              +{frame.events.length - 3} more
            </span>
          )}
        </div>
      )}
      
      <div className="frame-stats">
        <span>{Object.keys(frame.states || {}).length} states</span>
      </div>
    </div>
  );
}

// Frame Details Component
function FrameDetails({ frame, logbookEntries = [] }) {
  if (!frame) {
    return (
      <div className="frame-details">
        <h3>Frame Details</h3>
        <p className="empty-message">Select a frame to view details</p>
      </div>
    );
  }
  
  const timestamp = new Date(frame.timestamp);
  
  return (
    <div className="frame-details">
      <h3>Frame Details</h3>
      
      <div className="detail-section">
        <h4>Timestamp</h4>
        <p>{timestamp.toLocaleString()}</p>
        <p className="timestamp-iso">{timestamp.toISOString()}</p>
      </div>
      
      {/* Logbook Entries */}
      {logbookEntries.length > 0 && (
        <div className="detail-section logbook-entries">
          <h4>📖 Logbook Entries ({logbookEntries.length})</h4>
          {logbookEntries.slice(0, 5).map((entry) => (
            <div key={entry.id} className="logbook-entry-item">
              <span className={`severity ${entry.severity}`}>{entry.severity}</span>
              <p className="entry-title">{entry.title}</p>
              <p className="entry-author">by {entry.author}</p>
            </div>
          ))}
          {logbookEntries.length > 5 && (
            <p className="more-items">+{logbookEntries.length - 5} more entries</p>
          )}
        </div>
      )}
      
      {frame.events && frame.events.length > 0 && (
        <div className="detail-section">
          <h4>Events ({frame.events.length})</h4>
          {frame.events.map((event, idx) => (
            <div key={idx} className="event-detail">
              <span className={`severity ${event.severity?.toLowerCase() || 'unknown'}`}>
                {event.severity}
              </span>
              <p>{event.message}</p>
            </div>
          ))}
        </div>
      )}
      
      {frame.states && Object.keys(frame.states).length > 0 && (
        <div className="detail-section">
          <h4>States</h4>
          {Object.entries(frame.states).map(([type, entities]) => (
            <div key={type} className="state-group">
              <h5>{type}</h5>
              {Object.entries(entities).slice(0, 5).map(([id, state]) => (
                <div key={id} className="state-item">
                  <span className="state-id">{id}</span>
                  <pre>{JSON.stringify(state, null, 2)}</pre>
                </div>
              ))}
              {Object.keys(entities).length > 5 && (
                <p className="more-items">
                  +{Object.keys(entities).length - 5} more
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Helper functions
function getDefaultStartTime() {
  const date = new Date();
  date.setDate(date.getDate() - 1);
  return date;
}

function getDefaultEndTime() {
  return new Date();
}

function formatDateTimeLocal(date) {
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

export default TimelineReplay;
