/**
 * Tests for TimelineReplay Component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock timeline API
jest.mock('../api/timeline', () => ({
  getRange: jest.fn(),
  playback: jest.fn(),
  getSystem: jest.fn()
}));

// Import after mock
import { TimelineReplay } from '../pages/TimelineReplay';
import * as timelineApi from '../api/timeline';

describe('TimelineReplay', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock API responses
    timelineApi.playback.mockResolvedValue({
      start_time: '2024-01-01T00:00:00Z',
      end_time: '2024-01-01T12:00:00Z',
      total_frames: 12,
      frames: [
        {
          timestamp: '2024-01-01T00:00:00Z',
          events: [{ message: 'Event 1', severity: 'WARNING' }],
          states: { asset: { 'asset-1': { name: 'Asset 1' } } }
        },
        {
          timestamp: '2024-01-01T01:00:00Z',
          events: [{ message: 'Event 2', severity: 'CRITICAL' }],
          states: { asset: { 'asset-1': { name: 'Asset 1 Updated' } } }
        }
      ]
    });
  });

  it('renders the TimelineReplay page', () => {
    render(<TimelineReplay />);
    
    expect(screen.getByText('Timeline Replay')).toBeInTheDocument();
  });

  it('renders time range controls', () => {
    render(<TimelineReplay />);
    
    expect(screen.getByText('Time Range')).toBeInTheDocument();
    expect(screen.getByText('Start Time')).toBeInTheDocument();
    expect(screen.getByText('End Time')).toBeInTheDocument();
  });

  it('renders playback controls', () => {
    render(<TimelineReplay />);
    
    expect(screen.getByText('Playback Controls')).toBeInTheDocument();
  });

  it('loads frames on mount', async () => {
    render(<TimelineReplay />);
    
    await waitFor(() => {
      expect(timelineApi.playback).toHaveBeenCalled();
    });
  });

  it('renders frame list after loading', async () => {
    render(<TimelineReplay />);
    
    await waitFor(() => {
      expect(screen.getByText('Timeline Frames')).toBeInTheDocument();
    });
  });

  it('handles play button click', async () => {
    render(<TimelineReplay />);
    
    await waitFor(() => {
      expect(screen.getByText('▶')).toBeInTheDocument();
    });
    
    const playButton = screen.getByTitle('Play');
    fireEvent.click(playButton);
    
    // Play button should now show pause
    await waitFor(() => {
      expect(screen.getByTitle('Pause')).toBeInTheDocument();
    });
  });
});

describe('TimelinePlayer', () => {
  // Import TimelinePlayer for direct testing
  const TimelinePlayer = require('../components/TimelinePlayer').TimelinePlayer;

  it('renders player controls', () => {
    render(
      <TimelinePlayer
        isPlaying={false}
        currentFrame={0}
        totalFrames={10}
        playbackSpeed={1}
        onPlay={() => {}}
        onPause={() => {}}
        onStepForward={() => {}}
        onStepBackward={() => {}}
        onSliderChange={() => {}}
        onSpeedChange={() => {}}
      />
    );
    
    expect(screen.getByText('Playback Controls')).toBeInTheDocument();
    expect(screen.getByText('1x')).toBeInTheDocument();
    expect(screen.getByText('2x')).toBeInTheDocument();
    expect(screen.getByText('5x')).toBeInTheDocument();
    expect(screen.getByText('10x')).toBeInTheDocument();
  });

  it('renders frame counter', () => {
    render(
      <TimelinePlayer
        isPlaying={false}
        currentFrame={0}
        totalFrames={10}
        playbackSpeed={1}
        onPlay={() => {}}
        onPause={() => {}}
        onStepForward={() => {}}
        onStepBackward={() => {}}
        onSliderChange={() => {}}
        onSpeedChange={() => {}}
      />
    );
    
    expect(screen.getByText('Frame')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('of')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
  });

  it('calls onSpeedChange when speed button clicked', () => {
    const onSpeedChange = jest.fn();
    
    render(
      <TimelinePlayer
        isPlaying={false}
        currentFrame={0}
        totalFrames={10}
        playbackSpeed={1}
        onPlay={() => {}}
        onPause={() => {}}
        onStepForward={() => {}}
        onStepBackward={() => {}}
        onSliderChange={() => {}}
        onSpeedChange={onSpeedChange}
      />
    );
    
    fireEvent.click(screen.getByText('2x'));
    
    expect(onSpeedChange).toHaveBeenCalledWith(2);
  });

  it('disables step backward when at first frame', () => {
    render(
      <TimelinePlayer
        isPlaying={false}
        currentFrame={0}
        totalFrames={10}
        playbackSpeed={1}
        onPlay={() => {}}
        onPause={() => {}}
        onStepForward={() => {}}
        onStepBackward={() => {}}
        onSliderChange={() => {}}
        onSpeedChange={() => {}}
      />
    );
    
    const stepBackButton = screen.getByTitle('Step Backward');
    expect(stepBackButton).toBeDisabled();
  });

  it('disables step forward when at last frame', () => {
    render(
      <TimelinePlayer
        isPlaying={false}
        currentFrame={9}
        totalFrames={10}
        playbackSpeed={1}
        onPlay={() => {}}
        onPause={() => {}}
        onStepForward={() => {}}
        onStepBackward={() => {}}
        onSliderChange={() => {}}
        onSpeedChange={() => {}}
      />
    );
    
    const stepForwardButton = screen.getByTitle('Step Forward');
    expect(stepForwardButton).toBeDisabled();
  });
});

describe('Playback Behavior', () => {
  it('updates current frame when slider changes', () => {
    const onSliderChange = jest.fn();
    
    const TimelinePlayer = require('../components/TimelinePlayer').TimelinePlayer;
    
    render(
      <TimelinePlayer
        isPlaying={false}
        currentFrame={5}
        totalFrames={10}
        playbackSpeed={1}
        onPlay={() => {}}
        onPause={() => {}}
        onStepForward={() => {}}
        onStepBackward={() => {}}
        onSliderChange={onSliderChange}
        onSpeedChange={() => {}}
        frames={Array(10).fill({ timestamp: '2024-01-01T00:00:00Z', events: [], states: {} })}
      />
    );
    
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: 7 } });
    
    expect(onSliderChange).toHaveBeenCalledWith(7);
  });

  it('shows correct timestamp for current frame', () => {
    const frames = [
      { timestamp: '2024-01-01T10:00:00Z', events: [], states: {} },
      { timestamp: '2024-01-01T11:00:00Z', events: [], states: {} }
    ];
    
    const TimelinePlayer = require('../components/TimelinePlayer').TimelinePlayer;
    
    render(
      <TimelinePlayer
        isPlaying={false}
        currentFrame={1}
        totalFrames={2}
        playbackSpeed={1}
        onPlay={() => {}}
        onPause={() => {}}
        onStepForward={() => {}}
        onStepBackward={() => {}}
        onSliderChange={() => {}}
        onSpeedChange={() => {}}
        frames={frames}
      />
    );
    
    // Should show the time portion of the timestamp
    expect(screen.getByText(/11:00:00/)).toBeInTheDocument();
  });
});

describe('Speed Controls', () => {
  it('renders all speed options', () => {
    const TimelinePlayer = require('../components/TimelinePlayer').TimelinePlayer;
    
    render(
      <TimelinePlayer
        isPlaying={false}
        currentFrame={0}
        totalFrames={10}
        playbackSpeed={5}
        onPlay={() => {}}
        onPause={() => {}}
        onStepForward={() => {}}
        onStepBackward={() => {}}
        onSliderChange={() => {}}
        onSpeedChange={() => {}}
      />
    );
    
    expect(screen.getByText('1x')).toBeInTheDocument();
    expect(screen.getByText('2x')).toBeInTheDocument();
    expect(screen.getByText('5x')).toBeInTheDocument();
    expect(screen.getByText('10x')).toBeInTheDocument();
  });

  it('shows active speed button', () => {
    const TimelinePlayer = require('../components/TimelinePlayer').TimelinePlayer;
    
    render(
      <TimelinePlayer
        isPlaying={false}
        currentFrame={0}
        totalFrames={10}
        playbackSpeed={5}
        onPlay={() => {}}
        onPause={() => {}}
        onStepForward={() => {}}
        onStepBackward={() => {}}
        onSliderChange={() => {}}
        onSpeedChange={() => {}}
      />
    );
    
    // The active button should have a different class
    const speed5Button = screen.getByText('5x');
    expect(speed5Button.closest('button')).toHaveClass('active');
  });
});
