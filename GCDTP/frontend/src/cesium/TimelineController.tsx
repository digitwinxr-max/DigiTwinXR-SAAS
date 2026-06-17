/**
 * Timeline Controller
 * 
 * Timeline controls for 3D visualization playback.
 * Integrates with ADR-0025 Timeline Engine.
 * Part of the dual-view architecture (Leaflet 2D + Cesium 3D).
 */

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useCesium } from './CesiumContext';

// Timeline event for replay
export interface TimelineEvent {
  id: string;
  timestamp: Date;
  type: 'node_failed' | 'node_recovered' | 'route_changed' | 'flow_changed' | 'other';
  entityId: string;
  data?: Record<string, any>;
}

interface TimelineControllerProps {
  events: TimelineEvent[];
  onEventClick?: (event: TimelineEvent) => void;
  onPlaybackComplete?: () => void;
}

// Playback speeds
const PLAYBACK_SPEEDS = [
  { label: '0.25x', value: 0.25 },
  { label: '0.5x', value: 0.5 },
  { label: '1x', value: 1.0 },
  { label: '2x', value: 2.0 },
  { label: '10x', value: 10.0 },
  { label: '100x', value: 100.0 },
];

export function TimelineController({
  events,
  onEventClick,
  onPlaybackComplete,
}: TimelineControllerProps): JSX.Element {
  const { 
    playTimeline, 
    pauseTimeline, 
    seekTimeline, 
    setTimelineSpeed,
    timeline,
  } = useCesium();

  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentSpeed, setCurrentSpeed] = useState(1.0);
  const [currentTime, setCurrentTime] = useState<Date | null>(null);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Get current event
  const currentEvent = events[currentIndex] || null;

  // Calculate progress
  const progress = events.length > 0 
    ? ((currentIndex + 1) / events.length) * 100 
    : 0;

  // Start playback
  const handlePlay = useCallback(() => {
    setIsPlaying(true);
    playTimeline();
    
    // Calculate interval based on speed
    const baseInterval = 1000; // 1 second per event at 1x
    const interval = baseInterval / currentSpeed;
    
    intervalRef.current = setInterval(() => {
      setCurrentIndex(prev => {
        if (prev >= events.length - 1) {
          handlePause();
          onPlaybackComplete?.();
          return prev;
        }
        return prev + 1;
      });
    }, interval);
  }, [events.length, currentSpeed, playTimeline, onPlaybackComplete]);

  // Pause playback
  const handlePause = useCallback(() => {
    setIsPlaying(false);
    pauseTimeline();
    
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, [pauseTimeline]);

  // Stop playback
  const handleStop = useCallback(() => {
    handlePause();
    setCurrentIndex(0);
    setCurrentTime(null);
    seekTimeline(events[0]?.timestamp || new Date());
  }, [handlePause, events, seekTimeline]);

  // Seek to position
  const handleSeek = useCallback((index: number) => {
    setCurrentIndex(index);
    if (events[index]) {
      setCurrentTime(events[index].timestamp);
      seekTimeline(events[index].timestamp);
    }
  }, [events, seekTimeline]);

  // Change speed
  const handleSpeedChange = useCallback((speed: number) => {
    setCurrentSpeed(speed);
    setTimelineSpeed(speed);
    
    // Restart interval with new speed if playing
    if (isPlaying) {
      handlePause();
      setTimeout(() => handlePlay(), 0);
    }
  }, [isPlaying, handlePause, handlePlay, setTimelineSpeed]);

  // Step forward
  const handleStepForward = useCallback(() => {
    if (currentIndex < events.length - 1) {
      handleSeek(currentIndex + 1);
    }
  }, [currentIndex, events.length, handleSeek]);

  // Step backward
  const handleStepBackward = useCallback(() => {
    if (currentIndex > 0) {
      handleSeek(currentIndex - 1);
    }
  }, [currentIndex, handleSeek]);

  // Update current time
  useEffect(() => {
    if (currentEvent) {
      setCurrentTime(currentEvent.timestamp);
    }
  }, [currentEvent]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Format time for display
  const formatTime = (date: Date | null): string => {
    if (!date) return '--:--:--';
    return date.toLocaleTimeString();
  };

  return (
    <div className="timeline-controller">
      {/* Timeline Bar */}
      <div className="timeline-bar">
        <div 
          className="timeline-progress"
          style={{ width: `${progress}%` }}
        />
        
        {/* Event markers */}
        {events.map((event, index) => (
          <div
            key={event.id}
            className={`timeline-marker ${index === currentIndex ? 'active' : ''} ${index < currentIndex ? 'passed' : ''}`}
            style={{ left: `${((index + 1) / events.length) * 100}%` }}
            onClick={() => handleSeek(index)}
            title={`${event.type}: ${event.entityId}`}
          />
        ))}
      </div>

      {/* Controls */}
      <div className="timeline-controls">
        {/* Time Display */}
        <div className="timeline-time">
          <span className="current-time">{formatTime(currentTime)}</span>
          <span className="time-separator">/</span>
          <span className="total-time">
            {events.length > 0 
              ? formatTime(events[events.length - 1].timestamp)
              : '--:--:--'
            }
          </span>
        </div>

        {/* Playback Controls */}
        <div className="playback-controls">
          {/* Step Backward */}
          <button 
            className="control-btn step-back"
            onClick={handleStepBackward}
            disabled={currentIndex === 0}
            title="Step Backward"
          >
            ⏮
          </button>

          {/* Stop */}
          <button 
            className="control-btn stop"
            onClick={handleStop}
            title="Stop"
          >
            ⏹
          </button>

          {/* Play/Pause */}
          <button 
            className="control-btn play-pause"
            onClick={isPlaying ? handlePause : handlePlay}
            disabled={events.length === 0}
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? '⏸' : '▶'}
          </button>

          {/* Step Forward */}
          <button 
            className="control-btn step-forward"
            onClick={handleStepForward}
            disabled={currentIndex >= events.length - 1}
            title="Step Forward"
          >
            ⏭
          </button>
        </div>

        {/* Speed Control */}
        <div className="speed-controls">
          {PLAYBACK_SPEEDS.map(speed => (
            <button
              key={speed.value}
              className={`speed-btn ${currentSpeed === speed.value ? 'active' : ''}`}
              onClick={() => handleSpeedChange(speed.value)}
            >
              {speed.label}
            </button>
          ))}
        </div>

        {/* Event Counter */}
        <div className="event-counter">
          {currentIndex + 1} / {events.length}
        </div>
      </div>

      {/* Current Event Info */}
      {currentEvent && (
        <div className="current-event-info">
          <span className="event-type">{currentEvent.type}</span>
          <span className="event-entity">{currentEvent.entityId}</span>
          <button 
            className="event-detail-btn"
            onClick={() => onEventClick?.(currentEvent)}
          >
            Details
          </button>
        </div>
      )}
    </div>
  );
}

// Hook for timeline integration
export function useTimelineIntegration() {
  const { playTimeline, pauseTimeline, seekTimeline, setTimelineSpeed } = useCesium();

  const play = useCallback(() => {
    playTimeline();
  }, [playTimeline]);

  const pause = useCallback(() => {
    pauseTimeline();
  }, [pauseTimeline]);

  const seek = useCallback((time: Date) => {
    seekTimeline(time);
  }, [seekTimeline]);

  const setSpeed = useCallback((speed: number) => {
    setTimelineSpeed(speed);
  }, [setTimelineSpeed]);

  return {
    play,
    pause,
    seek,
    setSpeed,
  };
}

export default TimelineController;
