import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RecoveryStudio from './RecoveryStudio';
import * as api from '../api/recovery';

vi.mock('../api/recovery', () => ({
  createRecovery: vi.fn(),
  runRecovery: vi.fn(),
  getRecovery: vi.fn(),
  getResults: vi.fn(),
  compareRecovery: vi.fn(),
  getRecoveryTree: vi.fn(),
  deleteRecovery: vi.fn(),
  listRecoveries: vi.fn(),
  getHealthColor: vi.fn((score) => {
    if (score >= 80) return '#22c55e';
    if (score >= 40) return '#f97316';
    return '#ef4444';
  }),
  getRiskColor: vi.fn((risk) => {
    const colors = {
      NONE: '#22c55e',
      LOW: '#84cc16',
      MEDIUM: '#eab308',
      HIGH: '#f97316',
      CRITICAL: '#ef4444',
    };
    return colors[risk] || '#6b7280';
  }),
  formatImprovement: vi.fn((imp) => imp >= 0 ? `+${imp}` : `${imp}`),
  RECOVERY_TYPES: {
    MANUAL: 'manual',
    AUTOMATIC: 'automatic',
    STAGED: 'staged',
    REROUTE: 'reroute',
  },
}));

const mockRecovery = {
  id: 'recovery-1',
  scenario_id: 'scenario-1',
  strategy_name: 'Test Recovery',
  recovery_type: 'manual',
  estimated_duration_minutes: 60,
  recovery_order: 1,
  created_at: '2026-06-17T10:00:00Z',
  result_count: 3,
};

const mockResults = {
  items: [
    {
      id: 'result-1',
      recovery_simulation_id: 'recovery-1',
      asset_id: 'asset-1',
      asset_name: 'Transformer A',
      asset_type: 'transformer',
      before_health: 60,
      after_health: 80,
      improvement: 20,
      recovery_depth: 0,
      remaining_risk: 'LOW',
    },
    {
      id: 'result-2',
      recovery_simulation_id: 'recovery-1',
      asset_id: 'asset-2',
      asset_name: 'Building A',
      asset_type: 'building',
      before_health: 70,
      after_health: 90,
      improvement: 20,
      recovery_depth: 1,
      remaining_risk: 'NONE',
    },
  ],
  total: 2,
};

const mockRecoveryTree = {
  asset_id: 'asset-1',
  asset_name: 'Transformer A',
  asset_type: 'transformer',
  before_health: 60,
  after_health: 80,
  improvement: 20,
  recovery_depth: 0,
  remaining_risk: 'LOW',
  children: [
    {
      asset_id: 'asset-2',
      asset_name: 'Building A',
      asset_type: 'building',
      before_health: 70,
      after_health: 90,
      improvement: 20,
      recovery_depth: 1,
      remaining_risk: 'NONE',
      children: [],
    },
  ],
};

const mockComparison = {
  recovery_id: 'recovery-1',
  strategy_name: 'Test Recovery',
  before_health: 65,
  after_health: 85,
  improvement: 20,
  remaining_critical: 0,
};

function renderComponent(props = {}) {
  return render(<RecoveryStudio {...props} />);
}

describe('RecoveryStudio Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.listRecoveries.mockResolvedValueOnce({ items: [] });
  });

  it('renders builder panel', async () => {
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      expect(screen.getByText(/Recovery Builder/i)).toBeInTheDocument();
    });
  });

  it('renders results panel', async () => {
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      expect(screen.getByText(/Recovery Results/i)).toBeInTheDocument();
    });
  });

  it('renders statistics panel', async () => {
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      expect(screen.getByText(/Statistics/i)).toBeInTheDocument();
    });
  });

  it('renders form fields', async () => {
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      expect(screen.getByLabelText(/Strategy Name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Recovery Type/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Estimated Duration/i)).toBeInTheDocument();
    });
  });

  it('shows empty state when no recovery run', async () => {
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      expect(screen.getByText(/Run a recovery simulation/i)).toBeInTheDocument();
    });
  });

  it('displays run recovery button', async () => {
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Run Recovery/i })).toBeInTheDocument();
    });
  });

  it('shows warning when no scenario selected', async () => {
    renderComponent({});
    
    await waitFor(() => {
      expect(screen.getByText(/Select a scenario first/i)).toBeInTheDocument();
    });
  });
});

describe('Recovery Builder', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.listRecoveries.mockResolvedValueOnce({ items: [] });
  });

  it('can enter strategy name', async () => {
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      const input = screen.getByLabelText(/Strategy Name/i);
      fireEvent.change(input, { target: { value: 'My Recovery' } });
      expect(input.value).toBe('My Recovery');
    });
  });

  it('can select recovery type', async () => {
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      const select = screen.getByLabelText(/Recovery Type/i);
      expect(select.value).toBe('manual');
      
      fireEvent.change(select, { target: { value: 'automatic' } });
      expect(select.value).toBe('automatic');
    });
  });

  it('can enter duration', async () => {
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      const input = screen.getByLabelText(/Estimated Duration/i);
      fireEvent.change(input, { target: { value: '120' } });
      expect(input.value).toBe('120');
    });
  });

  it('shows error when name is empty', async () => {
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      fireEvent.click(screen.getByRole('button', { name: /Run Recovery/i }));
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Please enter a strategy name/i)).toBeInTheDocument();
    });
  });
});

describe('Recovery Run', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.listRecoveries.mockResolvedValueOnce({ items: [] });
  });

  it('runs recovery successfully', async () => {
    api.createRecovery.mockResolvedValueOnce(mockRecovery);
    api.runRecovery.mockResolvedValueOnce({});
    api.getResults.mockResolvedValueOnce(mockResults);
    api.getRecoveryTree.mockResolvedValueOnce(mockRecoveryTree);
    api.compareRecovery.mockResolvedValueOnce(mockComparison);
    api.listRecoveries.mockResolvedValueOnce({ items: [mockRecovery] });
    
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      fireEvent.change(screen.getByLabelText(/Strategy Name/i), { target: { value: 'Test' } });
    });
    
    await waitFor(() => {
      fireEvent.click(screen.getByRole('button', { name: /Run Recovery/i }));
    });
    
    await waitFor(() => {
      expect(api.createRecovery).toHaveBeenCalled();
      expect(api.runRecovery).toHaveBeenCalled();
    });
  });

  it('displays results after run', async () => {
    api.createRecovery.mockResolvedValueOnce(mockRecovery);
    api.runRecovery.mockResolvedValueOnce({});
    api.getResults.mockResolvedValueOnce(mockResults);
    api.getRecoveryTree.mockResolvedValueOnce(mockRecoveryTree);
    api.compareRecovery.mockResolvedValueOnce(mockComparison);
    api.listRecoveries.mockResolvedValueOnce({ items: [mockRecovery] });
    
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      fireEvent.change(screen.getByLabelText(/Strategy Name/i), { target: { value: 'Test' } });
    });
    
    await waitFor(() => {
      fireEvent.click(screen.getByRole('button', { name: /Run Recovery/i }));
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Transformer A/i)).toBeInTheDocument();
    });
  });
});

describe('Statistics Display', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.listRecoveries.mockResolvedValueOnce({ items: [] });
  });

  it('displays statistics section', async () => {
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      expect(screen.getByText(/Worst Recovery/i)).toBeInTheDocument();
      expect(screen.getByText(/Best Recovery/i)).toBeInTheDocument();
      expect(screen.getByText(/Average Improvement/i)).toBeInTheDocument();
    });
  });

  it('displays recovery types info', async () => {
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      expect(screen.getByText(/Recovery Types/i)).toBeInTheDocument();
      expect(screen.getByText(/Manual/i)).toBeInTheDocument();
      expect(screen.getByText(/Automatic/i)).toBeInTheDocument();
    });
  });
});

describe('Back Button', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.listRecoveries.mockResolvedValueOnce({ items: [] });
  });

  it('renders back button when onBack provided', async () => {
    const onBack = vi.fn();
    renderComponent({ scenarioId: 'scenario-1', onBack });
    
    await waitFor(() => {
      expect(screen.getByText(/← Back to Scenarios/i)).toBeInTheDocument();
    });
  });

  it('does not render back button when onBack not provided', async () => {
    renderComponent({ scenarioId: 'scenario-1' });
    
    await waitFor(() => {
      expect(screen.queryByText(/← Back to Scenarios/i)).not.toBeInTheDocument();
    });
  });
});