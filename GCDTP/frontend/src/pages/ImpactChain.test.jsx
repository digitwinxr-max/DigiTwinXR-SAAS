import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ImpactChain from './ImpactChain';
import * as api from '../api/propagation';
import * as assetsApi from '../api/assets';

vi.mock('../api/propagation', () => ({
  getImpactChain: vi.fn(),
  getAssetImpacts: vi.fn(),
  PROPAGATION_TYPE_INFO: {
    child_failure: { label: 'Child Failure', color: '#ef4444', description: 'Child failure propagated' },
    upstream_failure: { label: 'Upstream Failure', color: '#f97316', description: 'Upstream failure' },
    downstream_failure: { label: 'Downstream Failure', color: '#eab308', description: 'Downstream failure' },
    dependency_impact: { label: 'Dependency Impact', color: '#8b5cf6', description: 'Dependency impact' },
  },
  getSeverityColor: vi.fn((severity) => severity === 'WARNING' ? '#eab308' : '#ef4444'),
}));

vi.mock('../api/assets', () => ({
  getAssets: vi.fn(),
}));

const mockAssets = [
  { id: 'asset-1', name: 'Transformer A', asset_type: 'transformer' },
  { id: 'asset-2', name: 'Gaborone HQ', asset_type: 'building' },
  { id: 'asset-3', name: 'Backup Facility', asset_type: 'facility' },
];

const mockChainData = {
  asset_id: 'asset-1',
  chains: [
    {
      source_event_id: 'event-1',
      source_asset_name: 'Transformer A',
      source_severity: 'CRITICAL',
      root_event_message: 'Overload detected',
      chain: [
        {
          asset_id: 'asset-2',
          asset_name: 'Gaborone HQ',
          asset_type: 'building',
          severity: 'CRITICAL',
          depth: 1,
          relationship_type: 'feeds',
          propagation_type: 'downstream_failure',
          children: [
            {
              asset_id: 'asset-3',
              asset_name: 'Backup Facility',
              asset_type: 'facility',
              severity: 'WARNING',
              depth: 2,
              relationship_type: 'connected_to',
              propagation_type: 'dependency_impact',
              children: [],
            },
          ],
        },
      ],
      total_affected: 2,
    },
  ],
  total_chains: 1,
};

const mockImpacts = [
  {
    id: 'prop-1',
    source_event_id: 'event-1',
    source_asset_id: 'asset-1',
    source_asset_name: 'Transformer A',
    affected_asset_id: 'asset-2',
    affected_asset_name: 'Gaborone HQ',
    propagation_type: 'downstream_failure',
    severity: 'CRITICAL',
    depth: 1,
    event_message: 'Overload detected',
    created_at: '2026-06-16T10:00:00Z',
  },
];

function renderComponent() {
  return render(<ImpactChain />);
}

describe('ImpactChain Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
  });

  it('renders loading state initially', () => {
    api.getImpactChain.mockImplementation(() => new Promise(() => {}));
    
    renderComponent();
    
    expect(screen.getByText(/Loading impact chain/i)).toBeInTheDocument();
  });

  it('renders asset selector', async () => {
    api.getImpactChain.mockResolvedValueOnce({ chains: [], total_chains: 0 });
    
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByLabelText(/Select Asset/i)).toBeInTheDocument();
    });
  });

  it('shows propagation type legend', async () => {
    api.getImpactChain.mockResolvedValueOnce({ chains: [], total_chains: 0 });
    
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Propagation Types/i)).toBeInTheDocument();
      expect(screen.getByText(/Child Failure/i)).toBeInTheDocument();
      expect(screen.getByText(/Upstream Failure/i)).toBeInTheDocument();
      expect(screen.getByText(/Downstream Failure/i)).toBeInTheDocument();
      expect(screen.getByText(/Dependency Impact/i)).toBeInTheDocument();
    });
  });

  it('shows severity legend', async () => {
    api.getImpactChain.mockResolvedValueOnce({ chains: [], total_chains: 0 });
    
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Severity/i)).toBeInTheDocument();
      expect(screen.getByText(/WARNING/i)).toBeInTheDocument();
      expect(screen.getByText(/CRITICAL/i)).toBeInTheDocument();
    });
  });

  it('loads chain when asset is selected', async () => {
    api.getImpactChain.mockResolvedValueOnce(mockChainData);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(api.getImpactChain).toHaveBeenCalledWith('asset-1', null, 10);
    });
  });

  it('displays chain data correctly', async () => {
    api.getImpactChain.mockResolvedValueOnce(mockChainData);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Source Event: Overload detected/i)).toBeInTheDocument();
    });
  });

  it('displays chain nodes', async () => {
    api.getImpactChain.mockResolvedValueOnce(mockChainData);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText('Gaborone HQ')).toBeInTheDocument();
      expect(screen.getByText('Backup Facility')).toBeInTheDocument();
    });
  });

  it('shows empty state when no chains', async () => {
    api.getImpactChain.mockResolvedValueOnce({ chains: [], total_chains: 0 });
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/No propagation chains found/i)).toBeInTheDocument();
    });
  });

  it('handles view mode change', async () => {
    api.getImpactChain.mockResolvedValueOnce(mockChainData);
    api.getAssetImpacts.mockResolvedValueOnce(mockImpacts);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      const viewSelect = screen.getByLabelText(/View/i);
      fireEvent.change(viewSelect, { target: { value: 'impacts' } });
    });
    
    await waitFor(() => {
      expect(api.getAssetImpacts).toHaveBeenCalledWith('asset-1');
    });
  });

  it('handles max depth change', async () => {
    api.getImpactChain.mockResolvedValueOnce(mockChainData);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      const depthInput = screen.getByLabelText(/Max Depth/i);
      fireEvent.change(depthInput, { target: { value: '5' } });
    });
    
    await waitFor(() => {
      expect(api.getImpactChain).toHaveBeenLastCalledWith('asset-1', null, 5);
    });
  });

  it('displays instructions', async () => {
    api.getImpactChain.mockResolvedValueOnce(mockChainData);
    
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/How to Use/i)).toBeInTheDocument();
    });
  });

  it('displays propagation rules', async () => {
    api.getImpactChain.mockResolvedValueOnce(mockChainData);
    
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Propagation Rules/i)).toBeInTheDocument();
    });
  });
});

describe('Chain Rendering', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
    api.getImpactChain.mockResolvedValueOnce(mockChainData);
  });

  it('renders severity badges', async () => {
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      const badges = screen.getAllByText(/CRITICAL|WARNING/);
      expect(badges.length).toBeGreaterThan(0);
    });
  });

  it('renders depth badges', async () => {
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Depth 1/i)).toBeInTheDocument();
    });
  });
});

describe('Expand/Collapse Logic', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
    api.getImpactChain.mockResolvedValueOnce(mockChainData);
  });

  it('auto-expands first level nodes', async () => {
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      // Should show first level children
      expect(screen.getByText('Gaborone HQ')).toBeInTheDocument();
    });
  });
});

describe('Impacts View', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
  });

  it('displays impacts list', async () => {
    api.getAssetImpacts.mockResolvedValueOnce(mockImpacts);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-2' } });
    });
    
    await waitFor(() => {
      const viewSelect = screen.getByLabelText(/View/i);
      fireEvent.change(viewSelect, { target: { value: 'impacts' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Impacts on This Asset/i)).toBeInTheDocument();
    });
  });

  it('shows impact summary stats', async () => {
    api.getAssetImpacts.mockResolvedValueOnce(mockImpacts);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-2' } });
    });
    
    await waitFor(() => {
      const viewSelect = screen.getByLabelText(/View/i);
      fireEvent.change(viewSelect, { target: { value: 'impacts' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Total: 1/i)).toBeInTheDocument();
      expect(screen.getByText(/Critical: 1/i)).toBeInTheDocument();
    });
  });

  it('shows empty state when no impacts', async () => {
    api.getAssetImpacts.mockResolvedValueOnce([]);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-2' } });
    });
    
    await waitFor(() => {
      const viewSelect = screen.getByLabelText(/View/i);
      fireEvent.change(viewSelect, { target: { value: 'impacts' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/No impacts found/i)).toBeInTheDocument();
    });
  });
});

describe('Error Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
  });

  it('shows error state on fetch failure', async () => {
    api.getImpactChain.mockRejectedValueOnce(new Error('Network error'));
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Error: Network error/i)).toBeInTheDocument();
    });
  });
});