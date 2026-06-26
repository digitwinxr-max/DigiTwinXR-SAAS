/**
 * Temporal Dataset Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { TimeWindow } from './kepler_types';

interface TemporalContextValue {
  timeWindow: TimeWindow | null;
  isPlaying: boolean;
  playbackSpeed: number;
  currentTime: string | null;
  setTimeWindow: (window: TimeWindow | null) => void;
  setIsPlaying: (playing: boolean) => void;
  setPlaybackSpeed: (speed: number) => void;
  setCurrentTime: (time: string) => void;
}

const TemporalContext = createContext<TemporalContextValue | undefined>(undefined);

interface TemporalProviderProps {
  children: ReactNode;
}

export function TemporalProvider({ children }: TemporalProviderProps) {
  const [timeWindow, setTimeWindow] = useState<TimeWindow | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [currentTime, setCurrentTime] = useState<string | null>(null);

  const value: TemporalContextValue = {
    timeWindow,
    isPlaying,
    playbackSpeed,
    currentTime,
    setTimeWindow,
    setIsPlaying,
    setPlaybackSpeed,
    setCurrentTime
  };

  return (
    <TemporalContext.Provider value={value}>
      {children}
    </TemporalContext.Provider>
  );
}

export function useTemporal() {
  const context = useContext(TemporalContext);
  if (!context) {
    throw new Error('useTemporal must be used within a TemporalProvider');
  }
  return context;
}

// Temporal operations
export function useTemporalOperations() {
  const { 
    timeWindow, 
    setTimeWindow, 
    isPlaying, 
    setIsPlaying,
    playbackSpeed,
    setPlaybackSpeed,
    currentTime,
    setCurrentTime
  } = useTemporal();

  const setTimeRange = (start: string, end: string) => {
    setTimeWindow({ start, end });
  };

  const play = () => {
    setIsPlaying(true);
  };

  const pause = () => {
    setIsPlaying(false);
  };

  const stepForward = () => {
    if (!timeWindow) return;
    const current = currentTime || timeWindow.start;
    const nextTime = new Date(current);
    nextTime.setMinutes(nextTime.getMinutes() + (playbackSpeed * 5));
    
    if (nextTime.toISOString() <= timeWindow.end) {
      setCurrentTime(nextTime.toISOString());
    }
  };

  const stepBackward = () => {
    if (!timeWindow) return;
    const current = currentTime || timeWindow.start;
    const prevTime = new Date(current);
    prevTime.setMinutes(prevTime.getMinutes() - (playbackSpeed * 5));
    
    if (prevTime.toISOString() >= timeWindow.start) {
      setCurrentTime(prevTime.toISOString());
    }
  };

  const reset = () => {
    if (timeWindow) {
      setCurrentTime(timeWindow.start);
    }
    setIsPlaying(false);
  };

  return {
    timeWindow,
    isPlaying,
    playbackSpeed,
    currentTime,
    setTimeRange,
    play,
    pause,
    stepForward,
    stepBackward,
    reset,
    setSpeed: setPlaybackSpeed
  };
}

// Timeline synchronization
export function useTimelineSync() {
  const { currentTime, setCurrentTime } = useTemporal();

  const syncWithTimeline = (timelineTime: string) => {
    setCurrentTime(timelineTime);
  };

  const getCurrentTimestamp = () => {
    return currentTime || new Date().toISOString();
  };

  return {
    currentTime,
    syncWithTimeline,
    getCurrentTimestamp
  };
}
