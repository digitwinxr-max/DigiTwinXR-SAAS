/**
 * Cesium Context Tests
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { CesiumProvider, useCesium } from '../../src/cesium/CesiumContext';

// Test component that uses Cesium context
function TestConsumer() {
  const {
    viewer,
    isInitialized,
    isLoading,
    error,
    initializeViewer,
    destroyViewer,
    flyTo,
    zoomIn,
    zoomOut,
    resetCamera,
    addEntity,
    removeEntity,
    selectEntity,
    playTimeline,
    pauseTimeline,
  } = useCesium();

  return (
    <div>
      <span data-testid="is-initialized">{isInitialized.toString()}</span>
      <span data-testid="is-loading">{isLoading.toString()}</span>
      <span data-testid="error">{error || 'none'}</span>
      <button onClick={() => initializeViewer('test-container')}>Initialize</button>
      <button onClick={destroyViewer}>Destroy</button>
      <button onClick={() => flyTo({ x: 0, y: 0, z: 1000000 })}>FlyTo</button>
      <button onClick={zoomIn}>Zoom In</button>
      <button onClick={zoomOut}>Zoom Out</button>
      <button onClick={resetCamera}>Reset</button>
      <button onClick={() => addEntity({ id: 'test-entity', position: { x: 0, y: 0, z: 0 } })}>Add Entity</button>
      <button onClick={() => removeEntity('test-entity')}>Remove Entity</button>
      <button onClick={() => selectEntity({ id: 'test-entity' })}>Select</button>
      <button onClick={playTimeline}>Play</button>
      <button onClick={pauseTimeline}>Pause</button>
    </div>
  );
}

describe('CesiumContext', () => {
  it('should render without crashing', () => {
    render(
      <CesiumProvider>
        <TestConsumer />
      </CesiumProvider>
    );
    
    expect(screen.getByTestId('is-initialized')).toBeInTheDocument();
  });

  it('should initialize with default values', () => {
    render(
      <CesiumProvider>
        <TestConsumer />
      </CesiumProvider>
    );

    expect(screen.getByTestId('is-initialized').textContent).toBe('false');
    expect(screen.getByTestId('is-loading').textContent).toBe('false');
    expect(screen.getByTestId('error').textContent).toBe('none');
  });

  it('should throw error when useCesium is used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      render(<TestConsumer />);
    }).toThrow('useCesium must be used within a CesiumProvider');

    consoleSpy.mockRestore();
  });

  it('should initialize viewer when initializeViewer is called', async () => {
    render(
      <CesiumProvider>
        <TestConsumer />
      </CesiumProvider>
    );

    const initButton = screen.getByText('Initialize');
    initButton.click();

    await waitFor(() => {
      expect(screen.getByTestId('is-initialized').textContent).toBe('true');
    });
  });

  it('should destroy viewer when destroyViewer is called', async () => {
    render(
      <CesiumProvider>
        <TestConsumer />
      </CesiumProvider>
    );

    // First initialize
    const initButton = screen.getByText('Initialize');
    initButton.click();

    await waitFor(() => {
      expect(screen.getByTestId('is-initialized').textContent).toBe('true');
    });

    // Then destroy
    const destroyButton = screen.getByText('Destroy');
    destroyButton.click();

    expect(screen.getByTestId('is-initialized').textContent).toBe('false');
  });
});

describe('CesiumViewer State', () => {
  it('should manage viewer state correctly', async () => {
    render(
      <CesiumProvider>
        <TestConsumer />
      </CesiumProvider>
    );

    const initButton = screen.getByText('Initialize');
    initButton.click();

    await waitFor(() => {
      expect(screen.getByTestId('is-loading').textContent).toBe('true');
    });
  });
});

describe('Timeline State', () => {
  it('should manage timeline state', async () => {
    render(
      <CesiumProvider>
        <TestConsumer />
      </CesiumProvider>
    );

    const playButton = screen.getByText('Play');
    playButton.click();

    const pauseButton = screen.getByText('Pause');
    pauseButton.click();
  });
});
