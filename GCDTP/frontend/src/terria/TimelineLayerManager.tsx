/**
 * Timeline Layer Manager
 * Connects to ADR-0025 Operational Timeline Engine
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { CatalogItem, TimeEnabledLayer, TimeInterval } from './terria_types';

interface TimelineContextValue {
  timeEnabledLayers: TimeEnabledLayer[];
  currentTime: string | null;
  isPlaying: boolean;
  playbackSpeed: number;
  addTimeEnabledLayer: (layerId: string) => void;
  removeTimeEnabledLayer: (layerId: string) => void;
  setCurrentTime: (time: string) => void;
  setIsPlaying: (playing: boolean) => void;
  setPlaybackSpeed: (speed: number) => void;
  getTimeIntervals: (layerId: string) => TimeInterval[];
}

const TimelineContext = createContext<TimelineContextValue | undefined>(undefined);

interface TimelineProviderProps {
  children: ReactNode;
  autoConnect?: boolean;
}

export function TimelineProvider({ children, autoConnect = true }: TimelineProviderProps) {
  const [timeEnabledLayers, setTimeEnabledLayers] = useState<TimeEnabledLayer[]>([]);
  const [currentTime, setCurrentTime] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  // Auto-advance time when playing
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setCurrentTime(prev => {
        if (!prev) return null;
        // Advance time by playback speed (simplified)
        const date = new Date(prev);
        date.setMinutes(date.getMinutes() + playbackSpeed);
        return date.toISOString();
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isPlaying, playbackSpeed]);

  const addTimeEnabledLayer = (layerId: string) => {
    setTimeEnabledLayers(prev => {
      if (prev.some(l => l.layerId === layerId)) return prev;
      return [...prev, { layerId, currentTime, timeMultiplier: 1 }];
    });
  };

  const removeTimeEnabledLayer = (layerId: string) => {
    setTimeEnabledLayers(prev => prev.filter(l => l.layerId !== layerId));
  };

  const getTimeIntervals = (layerId: string): TimeInterval[] => {
    const layer = timeEnabledLayers.find(l => l.layerId === layerId);
    return layer?.availableIntervals || [];
  };

  const value: TimelineContextValue = {
    timeEnabledLayers,
    currentTime,
    isPlaying,
    playbackSpeed,
    addTimeEnabledLayer,
    removeTimeEnabledLayer,
    setCurrentTime,
    setIsPlaying,
    setPlaybackSpeed,
    getTimeIntervals
  };

  return (
    <TimelineContext.Provider value={value}>
      {children}
    </TimelineContext.Provider>
  );
}

export function useTimelineLayer() {
  const context = useContext(TimelineContext);
  if (!context) {
    throw new Error('useTimelineLayer must be used within a TimelineProvider');
  }
  return context;
}

// Timeline controls
export function TimelineControls() {
  const { 
    currentTime, 
    setCurrentTime, 
    isPlaying, 
    setIsPlaying,
    playbackSpeed,
    setPlaybackSpeed 
  } = useTimelineLayer();

  return (
    <div className="timeline-controls">
      <button 
        className="control-btn"
        onClick={() => setIsPlaying(!isPlaying)}
      >
        {isPlaying ? '⏸' : '▶'}
      </button>
      
      <input
        type="datetime-local"
        value={currentTime?.slice(0, 16) || ''}
        onChange={(e) => setCurrentTime(new Date(e.target.value).toISOString())}
        className="time-input"
      />
      
      <select 
        value={playbackSpeed}
        onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
        className="speed-select"
      >
        <option value={0.5}>0.5x</option>
        <option value={1}>1x</option>
        <option value={2}>2x</option>
        <option value={5}>5x</option>
        <option value={10}>10x</option>
      </select>
    </div>
  );
}

// Time-enabled layer item
interface TimeLayerItemProps {
  layerId: string;
  onRemove?: () => void;
}

export function TimeLayerItem({ layerId, onRemove }: TimeLayerItemProps) {
  const { 
    currentTime, 
    setCurrentTime,
    getTimeIntervals 
  } = useTimelineLayer();
  
  const intervals = getTimeIntervals(layerId);

  return (
    <div className="time-layer-item">
      <span className="layer-id">{layerId}</span>
      <span className="current-time">{currentTime || 'No time set'}</span>
      {intervals.length > 0 && (
        <span className="interval-count">{intervals.length} intervals</span>
      )}
      {onRemove && (
        <button onClick={onRemove} className="remove-btn">×</button>
      )}
    </div>
  );
}

// Timeline slider
interface TimelineSliderProps {
  min: string;
  max: string;
  step?: number;
  onChange?: (value: string) => void;
}

export function TimelineSlider({ min, max, step = 1, onChange }: TimelineSliderProps) {
  const { currentTime, setCurrentTime } = useTimelineLayer();
  
  const minDate = new Date(min).getTime();
  const maxDate = new Date(max).getTime();
  const currentDate = currentTime ? new Date(currentTime).getTime() : minDate;
  
  const percentage = ((currentDate - minDate) / (maxDate - minDate)) * 100;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number(e.target.value);
    const date = new Date(minDate + (value * step));
    setCurrentTime(date.toISOString());
    onChange?.(date.toISOString());
  };

  return (
    <div className="timeline-slider">
      <span className="time-label">{min}</span>
      <input
        type="range"
        min={0}
        max={Math.floor((maxDate - minDate) / (step * 1000))}
        value={Math.floor((currentDate - minDate) / (step * 1000))}
        onChange={handleChange}
        className="slider"
      />
      <span className="time-label">{max}</span>
    </div>
  );
}

// Connect to Timeline Engine (ADR-0025)
export function useTimelineEngine() {
  const { currentTime, setCurrentTime, setIsPlaying } = useTimelineLayer();

  // Get events from Timeline Engine
  const getTimelineEvents = async (startTime: string, endTime: string) => {
    // Placeholder - connects to ADR-0025 Timeline Engine
    return [];
  };

  // Register layer with Timeline Engine
  const registerLayerWithTimeline = async (layerId: string, config: any) => {
    // Placeholder - registers with ADR-0025 Timeline Engine
    console.log('Registering layer with Timeline Engine:', layerId);
  };

  return {
    currentTime,
    setCurrentTime,
    isPlaying: isPlaying,
    play: () => setIsPlaying(true),
    pause: () => setIsPlaying(false),
    getTimelineEvents,
    registerLayerWithTimeline
  };
}
