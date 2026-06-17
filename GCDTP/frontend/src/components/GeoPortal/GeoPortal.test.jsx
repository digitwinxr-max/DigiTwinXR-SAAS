import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import GeoPortal from './GeoPortal';

vi.mock('../../hooks/useEventBus', () => ({
  useEventBus: vi.fn(() => ({
    subscribe: vi.fn(() => vi.fn()),
    publish: vi.fn(),
  })),
  useEventSubscription: vi.fn(),
  EVENTS: {
    EVENT_CREATED: 'event.created',
    EVENT_RESOLVED: 'event.resolved',
    HEALTH_UPDATED: 'health.updated',
    ASSET_UPDATED: 'asset.updated',
  },
}));

const mockGeoJSON = {
  type: 'FeatureCollection',
  features: [
    {
      id: 'asset-1',
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [24.0, -22.0] },
      properties: { name: 'Asset 1', asset_type: 'sensor', status: 'active' },
    },
    {
      id: 'asset-2',
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [25.0, -23.0] },
      properties: { name: 'Asset 2', asset_type: 'sensor', status: 'active' },
    },
  ],
};

const mockHealthData = {
  items: [
    { asset_id: 'asset-1', health_status: 'HEALTHY', health_score: 100, active_event_count: 0 },
    { asset_id: 'asset-2', health_status: 'DEGRADED', health_score: 60, active_event_count: 2 },
  ],
};

const mockEvents = {
  items: [
    {
      id: 'event-1',
      asset_id: 'asset-2',
      severity: 'WARNING',
      message: 'Warning event',
      timestamp: '2026-06-16T10:00:00Z',
    },
    {
      id: 'event-2',
      asset_id: 'asset-2',
      severity: 'CRITICAL',
      message: 'Critical event',
      timestamp: '2026-06-16T11:00:00Z',
    },
  ],
};

const mockSensorData = {
  items: [{ id: 'sensor-1' }, { id: 'sensor-2' }],
  total: 2,
};

global.fetch = vi.fn();

function renderGeoPortal() {
  return render(
    <BrowserRouter>
      <GeoPortal />
    </BrowserRouter>
  );
}

describe('GeoPortal Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGeoJSON),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockHealthData),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockEvents),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockSensorData),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockSensorData),
      });
  });

  it('renders loading state initially', () => {
    renderGeoPortal();
    expect(screen.getByText(/Loading GeoPortal/i)).toBeInTheDocument();
  });

  it('renders summary cards after loading', async () => {
    renderGeoPortal();
    
    await waitFor(() => {
      expect(screen.getByText(/Active Events/i)).toBeInTheDocument();
    });
    
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText(/Warnings/i)).toBeInTheDocument();
    expect(screen.getByText(/Critical/i)).toBeInTheDocument();
  });

  it('renders layer toggles', async () => {
    renderGeoPortal();
    
    await waitFor(() => {
      expect(screen.getByText(/Layers/i)).toBeInTheDocument();
    });
    
    expect(screen.getByLabelText('Assets')).toBeInTheDocument();
    expect(screen.getByLabelText('Events')).toBeInTheDocument();
    expect(screen.getByLabelText('Sensors')).toBeInTheDocument();
  });

  it('renders legend', async () => {
    renderGeoPortal();
    
    await waitFor(() => {
      expect(screen.getByText(/Legend/i)).toBeInTheDocument();
    });
    
    expect(screen.getByText(/Healthy/i)).toBeInTheDocument();
    expect(screen.getByText(/Degraded/i)).toBeInTheDocument();
    expect(screen.getByText(/Critical/i)).toBeInTheDocument();
  });

  it('has refresh button', async () => {
    renderGeoPortal();
    
    await waitFor(() => {
      expect(screen.getByText(/Refresh Data/i)).toBeInTheDocument();
    });
  });

  it('fetches data from correct endpoints', async () => {
    renderGeoPortal();
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/assets/geojson');
      expect(global.fetch).toHaveBeenCalledWith('/api/health/assets');
      expect(global.fetch).toHaveBeenCalledWith('/api/events/active');
    });
  });

  it('shows error state on fetch failure', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));
    
    renderGeoPortal();
    
    await waitFor(() => {
      expect(screen.getByText(/Error/i)).toBeInTheDocument();
    });
  });
});

describe('GeoPortal Event Handling', () => {
  it('subscribes to event bus events', async () => {
    const { useEventSubscription } = await import('../../hooks/useEventBus');
    
    renderGeoPortal();
    
    await waitFor(() => {
      expect(useEventSubscription).toHaveBeenCalledWith('event.created', expect.any(Function));
      expect(useEventSubscription).toHaveBeenCalledWith('event.resolved', expect.any(Function));
      expect(useEventSubscription).toHaveBeenCalledWith('health.updated', expect.any(Function));
      expect(useEventSubscription).toHaveBeenCalledWith('asset.updated', expect.any(Function));
    });
  });
});

describe('GeoPortal Health Colors', () => {
  it('displays health status correctly', async () => {
    renderGeoPortal();
    
    await waitFor(() => {
      const healthyCount = screen.getByText('1', { selector: '.summary-card.healthy .card-value' });
      expect(healthyCount).toBeInTheDocument();
    });
  });
});

describe('GeoPortal Layer Toggles', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGeoJSON),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockHealthData),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockEvents),
      });
  });

  it('toggles assets layer', async () => {
    renderGeoPortal();
    
    await waitFor(() => {
      expect(screen.getByLabelText('Assets')).toBeChecked();
    });
    
    const assetsToggle = screen.getByLabelText('Assets');
    fireEvent.click(assetsToggle);
    
    expect(assetsToggle).not.toBeChecked();
  });

  it('toggles events layer', async () => {
    renderGeoPortal();
    
    await waitFor(() => {
      expect(screen.getByLabelText('Events')).toBeChecked();
    });
    
    const eventsToggle = screen.getByLabelText('Events');
    fireEvent.click(eventsToggle);
    
    expect(eventsToggle).not.toBeChecked();
  });
});