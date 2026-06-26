/**
 * Scene, Camera, and Timeline Controller Tests
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { CesiumProvider } from '../../src/cesium/CesiumContext';
import { SceneController } from '../../src/cesium/SceneController';
import { CameraController } from '../../src/cesium/CameraController';
import { TimelineController } from '../../src/cesium/TimelineController';

function TestWrapper({ children }: { children: React.ReactNode }) {
  return <CesiumProvider>{children}</CesiumProvider>;
}

describe('SceneController', () => {
  it('should render without crashing', () => {
    render(
      <TestWrapper>
        <SceneController />
      </TestWrapper>
    );
    
    expect(screen.getByText('View Mode')).toBeInTheDocument();
    expect(screen.getByText('Layers')).toBeInTheDocument();
    expect(screen.getByText('Scene Options')).toBeInTheDocument();
  });

  it('should display layer list', () => {
    render(
      <TestWrapper>
        <SceneController />
      </TestWrapper>
    );
    
    expect(screen.getByText('Assets')).toBeInTheDocument();
    expect(screen.getByText('Sensors')).toBeInTheDocument();
    expect(screen.getByText('Topology')).toBeInTheDocument();
  });

  it('should have 3D and 2D mode buttons', () => {
    render(
      <TestWrapper>
        <SceneController />
      </TestWrapper>
    );
    
    expect(screen.getByText('3D Globe')).toBeInTheDocument();
    expect(screen.getByText('2D Map')).toBeInTheDocument();
  });

  it('should have scene options', () => {
    render(
      <TestWrapper>
        <SceneController />
      </TestWrapper>
    );
    
    expect(screen.getByText('Lighting')).toBeInTheDocument();
    expect(screen.getByText('Atmosphere')).toBeInTheDocument();
    expect(screen.getByText('Fog')).toBeInTheDocument();
  });
});

describe('CameraController', () => {
  it('should render without crashing', () => {
    render(
      <TestWrapper>
        <CameraController />
      </TestWrapper>
    );
    
    expect(screen.getByText('NA')).toBeInTheDocument();
    expect(screen.getByText('EU')).toBeInTheDocument();
  });

  it('should display zoom controls', () => {
    render(
      <TestWrapper>
        <CameraController />
      </TestWrapper>
    );
    
    // Zoom buttons should be present
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('should display position info', () => {
    render(
      <TestWrapper>
        <CameraController />
      </TestWrapper>
    );
    
    expect(screen.getByText(/Lon:/)).toBeInTheDocument();
    expect(screen.getByText(/Lat:/)).toBeInTheDocument();
    expect(screen.getByText(/Alt:/)).toBeInTheDocument();
  });

  it('should have preset buttons', () => {
    render(
      <TestWrapper>
        <CameraController />
      </TestWrapper>
    );
    
    expect(screen.getByText('AS')).toBeInTheDocument();
    expect(screen.getByText('AU')).toBeInTheDocument();
  });
});

describe('TimelineController', () => {
  const mockEvents = [
    { id: 'e1', timestamp: new Date('2024-01-15T10:30:00'), type: 'node_failed' as const, entityId: 'asset-1' },
    { id: 'e2', timestamp: new Date('2024-01-15T10:35:00'), type: 'route_changed' as const, entityId: 'route-1' },
    { id: 'e3', timestamp: new Date('2024-01-15T10:40:00'), type: 'node_recovered' as const, entityId: 'asset-1' },
  ];

  it('should render without crashing', () => {
    render(
      <TestWrapper>
        <TimelineController events={mockEvents} />
      </TestWrapper>
    );
    
    expect(screen.getByText('3 / 3')).toBeInTheDocument();
  });

  it('should display play controls', () => {
    render(
      <TestWrapper>
        <TimelineController events={mockEvents} />
      </TestWrapper>
    );
    
    // Play button
    const playButton = screen.getByTitle('Play');
    expect(playButton).toBeInTheDocument();
  });

  it('should display speed controls', () => {
    render(
      <TestWrapper>
        <TimelineController events={mockEvents} />
      </TestWrapper>
    );
    
    expect(screen.getByText('1x')).toBeInTheDocument();
    expect(screen.getByText('2x')).toBeInTheDocument();
  });

  it('should display current event info', () => {
    render(
      <TestWrapper>
        <TimelineController events={mockEvents} />
      </TestWrapper>
    );
    
    expect(screen.getByText('node_failed')).toBeInTheDocument();
    expect(screen.getByText('asset-1')).toBeInTheDocument();
  });

  it('should handle empty events', () => {
    render(
      <TestWrapper>
        <TimelineController events={[]} />
      </TestWrapper>
    );
    
    expect(screen.getByText('0 / 0')).toBeInTheDocument();
  });

  it('should have step controls', () => {
    render(
      <TestWrapper>
        <TimelineController events={mockEvents} />
      </TestWrapper>
    );
    
    expect(screen.getByTitle('Step Backward')).toBeInTheDocument();
    expect(screen.getByTitle('Step Forward')).toBeInTheDocument();
    expect(screen.getByTitle('Stop')).toBeInTheDocument();
  });
});
