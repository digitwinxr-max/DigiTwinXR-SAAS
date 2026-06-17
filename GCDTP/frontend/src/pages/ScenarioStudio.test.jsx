import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ScenarioStudio from './ScenarioStudio';
import * as api from '../api/scenarios';
import * as assetsApi from '../api/assets';

vi.mock('../api/scenarios', () => ({
  createScenario: vi.fn(),
  runScenario: vi.fn(),
  getScenario: vi.fn(),
  getResults: vi.fn(),
  getImpactTree: vi.fn(),
  compareScenario: vi.fn(),
  deleteScenario: vi.fn(),
  listScenarios: vi.fn(),
  getHealthColor: vi.fn((score) => {
    if (score >= 80) return '#22c55e';
    if (score >= 40) return '#f97316';
    return '#ef4444';
  }),
  getDeltaColor: vi.fn((delta) => {
    if (delta >= 0) return '#22c55e';
    return '#ef4444';
  }),
  formatDelta: vi.fn((delta) => delta >= 0 ? `+${delta}` : `${delta}`),
  SCENARIO_TYPES: {
    FAILURE: 'failure',
    RECOVERY: 'recovery',
    MAINTENANCE: 'maintenance',
    CUSTOM: 'custom',
  },
  SEVERITY_LEVELS: {
    WARNING: 'WARNING',
    CRITICAL: 'CRITICAL',
  },
}));

vi.mock('../api/assets', () => ({
  getAssets: vi.fn(),
}));

const mockAssets = [
  { id: 'asset-1', name: 'Transformer A', asset_type: 'transformer' },
  { id: 'asset-2', name: 'Building A', asset_type: 'building' },
];

const mockScenario = {
  id: 'scenario-1',
  name: 'Test Scenario',
  description: 'Test description',
  scenario_type: 'failure',
  root_asset_id: 'asset-1',
  severity: 'CRITICAL',
  status: 'completed',
  created_at: '2026-06-17T10:00:00Z',
  result_count: 3,
};

const mockResults = {
  items: [
    {
      id: 'result-1',
      scenario_id: 'scenario-1',
      asset_id: 'asset-1',
      asset_name: 'Transformer A',
      asset_type: 'transformer',
      predicted_health: 80,
      current_health: 100,
      delta_health: -20,
      propagation_depth: 0,
      relationship_path: 'root',
    },
    {
      id: 'result-2',
      scenario_id: 'scenario-1',
      asset_id: 'asset-2',
      asset_name: 'Building A',
      asset_type: 'building',
      predicted_health: 90,
      current_health: 100,
      delta_health: -10,
      propagation_depth: 1,
      relationship_path: 'feeds',
    },
  ],
  total: 2,
};

const mockImpactTree = {
  asset_id: 'asset-1',
  asset_name: 'Transformer A',
  asset_type: 'transformer',
  current_health: 100,
  predicted_health: 80,
  delta_health: -20,
  propagation_depth: 0,
  relationship_type: 'root',
  children: [
    {
      asset_id: 'asset-2',
      asset_name: 'Building A',
      asset_type: 'building',
      current_health: 100,
      predicted_health: 90,
      delta_health: -10,
      propagation_depth: 1,
      relationship_type: 'feeds',
      children: [],
    },
  ],
};

const mockComparison = {
  current_health: 100,
  predicted_health: 80,
  delta: -20,
};

function renderComponent() {
  return render(<ScenarioStudio />);
}

describe('ScenarioStudio Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
    api.listScenarios.mockResolvedValueOnce({ items: [] });
  });

  it('renders builder panel', async () => {
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Scenario Builder/i)).toBeInTheDocument();
    });
  });

  it('renders results panel', async () => {
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Impact Results/i)).toBeInTheDocument();
    });
  });

  it('renders statistics panel', async () => {
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Statistics/i)).toBeInTheDocument();
    });
  });

  it('renders form fields', async () => {
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByLabelText(/Scenario Name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Description/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Root Asset/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Scenario Type/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Severity/i)).toBeInTheDocument();
    });
  });

  it('shows empty state when no simulation run', async () => {
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Run a simulation/i)).toBeInTheDocument();
    });
  });

  it('displays run simulation button', async () => {
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Run Simulation/i })).toBeInTheDocument();
    });
  });
});

describe('Builder Functionality', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
    api.listScenarios.mockResolvedValueOnce({ items: [] });
  });

  it('can enter scenario name', async () => {
    renderComponent();
    
    await waitFor(() => {
      const input = screen.getByLabelText(/Scenario Name/i);
      fireEvent.change(input, { target: { value: 'My Scenario' } });
      expect(input.value).toBe('My Scenario');
    });
  });

  it('can select root asset', async () => {
    renderComponent();
    
    await waitFor(() => {
      const select = screen.getByLabelText(/Root Asset/i);
      fireEvent.change(select, { target: { value: 'asset-1' } });
    });
  });

  it('can select scenario type', async () => {
    renderComponent();
    
    await waitFor(() => {
      const select = screen.getByLabelText(/Scenario Type/i);
      expect(select.value).toBe('failure');
      
      fireEvent.change(select, { target: { value: 'recovery' } });
      expect(select.value).toBe('recovery');
    });
  });

  it('can select severity', async () => {
    renderComponent();
    
    await waitFor(() => {
      const select = screen.getByLabelText(/Severity/i);
      expect(select.value).toBe('CRITICAL');
      
      fireEvent.change(select, { target: { value: 'WARNING' } });
      expect(select.value).toBe('WARNING');
    });
  });

  it('shows error when name is empty', async () => {
    renderComponent();
    
    await waitFor(() => {
      fireEvent.click(screen.getByRole('button', { name: /Run Simulation/i }));
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Please enter a scenario name/i)).toBeInTheDocument();
    });
  });
});

describe('Simulation Run', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
    api.listScenarios.mockResolvedValueOnce({ items: [] });
  });

  it('runs simulation successfully', async () => {
    api.createScenario.mockResolvedValueOnce(mockScenario);
    api.runScenario.mockResolvedValueOnce({});
    api.getResults.mockResolvedValueOnce(mockResults);
    api.getImpactTree.mockResolvedValueOnce(mockImpactTree);
    api.compareScenario.mockResolvedValueOnce(mockComparison);
    api.listScenarios.mockResolvedValueOnce({ items: [mockScenario] });
    
    renderComponent();
    
    await waitFor(() => {
      fireEvent.change(screen.getByLabelText(/Scenario Name/i), { target: { value: 'Test' } });
    });
    
    await waitFor(() => {
      fireEvent.change(screen.getByLabelText(/Root Asset/i), { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      fireEvent.click(screen.getByRole('button', { name: /Run Simulation/i }));
    });
    
    await waitFor(() => {
      expect(api.createScenario).toHaveBeenCalled();
      expect(api.runScenario).toHaveBeenCalled();
    });
  });

  it('displays results after run', async () => {
    api.createScenario.mockResolvedValueOnce(mockScenario);
    api.runScenario.mockResolvedValueOnce({});
    api.getResults.mockResolvedValueOnce(mockResults);
    api.getImpactTree.mockResolvedValueOnce(mockImpactTree);
    api.compareScenario.mockResolvedValueOnce(mockComparison);
    api.listScenarios.mockResolvedValueOnce({ items: [mockScenario] });
    
    renderComponent();
    
    await waitFor(() => {
      fireEvent.change(screen.getByLabelText(/Scenario Name/i), { target: { value: 'Test' } });
    });
    
    await waitFor(() => {
      fireEvent.change(screen.getByLabelText(/Root Asset/i), { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      fireEvent.click(screen.getByRole('button', { name: /Run Simulation/i }));
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Transformer A/i)).toBeInTheDocument();
    });
  });
});

describe('Statistics Display', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
    api.listScenarios.mockResolvedValueOnce({ items: [] });
  });

  it('displays statistics section', async () => {
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Worst Asset/i)).toBeInTheDocument();
      expect(screen.getByText(/Average Health/i)).toBeInTheDocument();
      expect(screen.getByText(/Affected Assets/i)).toBeInTheDocument();
      expect(screen.getByText(/Max Depth/i)).toBeInTheDocument();
    });
  });

  it('displays how it works section', async () => {
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/How It Works/i)).toBeInTheDocument();
    });
  });
});

describe('Delete Functionality', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
    api.listScenarios.mockResolvedValueOnce({ items: [] });
  });

  it('shows delete button when scenario selected', async () => {
    api.getScenario.mockResolvedValueOnce(mockScenario);
    api.getResults.mockResolvedValueOnce(mockResults);
    api.getImpactTree.mockResolvedValueOnce(mockImpactTree);
    api.compareScenario.mockResolvedValueOnce(mockComparison);
    api.listScenarios.mockResolvedValueOnce({ items: [mockScenario] });
    
    renderComponent();
    
    await waitFor(() => {
      const items = screen.getAllByText(/Test Scenario/);
      if (items.length > 0) {
        fireEvent.click(items[0]);
      }
    });
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Delete Scenario/i })).toBeInTheDocument();
    });
  });
});