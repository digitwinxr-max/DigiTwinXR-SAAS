import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import NetworkHealth from './NetworkHealth';
import * as api from '../api/networkHealth';
import * as assetsApi from '../api/assets';

vi.mock('../api/networkHealth', () => ({
  getHealthTree: vi.fn(),
  getContributors: vi.fn(),
  getHealthColor: vi.fn((score) => {
    if (score >= 80) return '#22c55e';
    if (score >= 40) return '#f97316';
    return '#ef4444';
  }),
  getRelationshipInfo: vi.fn((type) => {
    const info = {
      contains: { label: 'Contains', weight: 0.5 },
      feeds: { label: 'Feeds', weight: 0.7 },
      controls: { label: 'Controls', weight: 0.6 },
      connected_to: { label: 'Connected To', weight: 0.3 },
      monitors: { label: 'Monitors', weight: 0.0 },
    };
    return info[type] || { label: type, weight: 0 };
  }),
}));

vi.mock('../api/assets', () => ({
  getAssets: vi.fn(),
}));

const mockAssets = [
  { id: 'asset-1', name: 'Substation Alpha', asset_type: 'substation' },
  { id: 'asset-2', name: 'Building A', asset_type: 'building' },
  { id: 'asset-3', name: 'Equipment A', asset_type: 'equipment' },
];

const mockHealthTree = {
  asset_id: 'asset-1',
  asset_name: 'Substation Alpha',
  asset_type: 'substation',
  health_score: 72,
  health_status: 'DEGRADED',
  local_penalty: 20,
  dependency_penalty: 8.0,
  total_penalty: 28,
  contributors: [
    {
      asset_id: 'asset-3',
      asset_name: 'Equipment A',
      health_score: 20,
      health_status: 'CRITICAL',
      penalty: 8.0,
      depth: 2,
      relationship_type: 'feeds',
    },
  ],
  children: [
    {
      asset_id: 'asset-2',
      asset_name: 'Building A',
      asset_type: 'building',
      health_score: 72,
      health_status: 'DEGRADED',
      local_penalty: 0,
      dependency_penalty: 0,
      total_penalty: 0,
      children: [],
    },
  ],
  depth: 0,
  max_depth: 3,
};

const mockContributors = {
  asset_id: 'asset-1',
  asset_name: 'Substation Alpha',
  current_health_score: 72,
  total_dependency_penalty: 8.0,
  contributors: [
    {
      asset_id: 'asset-3',
      asset_name: 'Equipment A',
      health_score: 20,
      health_status: 'CRITICAL',
      penalty: 8.0,
      depth: 2,
      relationship_type: 'feeds',
    },
  ],
  count: 1,
};

function renderComponent() {
  return render(<NetworkHealth />);
}

describe('NetworkHealth Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
  });

  it('renders loading state initially', () => {
    api.getHealthTree.mockImplementation(() => new Promise(() => {}));
    
    renderComponent();
    
    expect(screen.getByText(/Loading network health/i)).toBeInTheDocument();
  });

  it('renders asset selector', async () => {
    api.getHealthTree.mockResolvedValueOnce({ ...mockHealthTree, children: [] });
    
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Select Asset/i)).toBeInTheDocument();
    });
  });

  it('shows health status legend', async () => {
    api.getHealthTree.mockResolvedValueOnce({ ...mockHealthTree, children: [] });
    
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Health Status/i)).toBeInTheDocument();
      expect(screen.getByText(/Healthy/i)).toBeInTheDocument();
      expect(screen.getByText(/Degraded/i)).toBeInTheDocument();
      expect(screen.getByText(/Critical/i)).toBeInTheDocument();
    });
  });

  it('shows relationship weights legend', async () => {
    api.getHealthTree.mockResolvedValueOnce({ ...mockHealthTree, children: [] });
    
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Relationship Weights/i)).toBeInTheDocument();
      expect(screen.getByText(/Feeds/i)).toBeInTheDocument();
      expect(screen.getByText(/Controls/i)).toBeInTheDocument();
      expect(screen.getByText(/Contains/i)).toBeInTheDocument();
    });
  });

  it('loads tree when asset is selected', async () => {
    api.getHealthTree.mockResolvedValueOnce(mockHealthTree);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(api.getHealthTree).toHaveBeenCalledWith('asset-1', 3);
    });
  });

  it('displays health tree data', async () => {
    api.getHealthTree.mockResolvedValueOnce(mockHealthTree);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Substation Alpha/i)).toBeInTheDocument();
    });
  });

  it('shows tree view', async () => {
    api.getHealthTree.mockResolvedValueOnce(mockHealthTree);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Health Tree/i)).toBeInTheDocument();
    });
  });

  it('shows contributors view', async () => {
    api.getContributors.mockResolvedValueOnce(mockContributors);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      const viewSelect = screen.getByLabelText(/View/i);
      fireEvent.change(viewSelect, { target: { value: 'contributors' } });
    });
    
    await waitFor(() => {
      expect(api.getContributors).toHaveBeenCalledWith('asset-1');
    });
  });

  it('displays contributors list', async () => {
    api.getContributors.mockResolvedValueOnce(mockContributors);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      const viewSelect = screen.getByLabelText(/View/i);
      fireEvent.change(viewSelect, { target: { value: 'contributors' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Equipment A/i)).toBeInTheDocument();
    });
  });

  it('shows empty state when no children', async () => {
    api.getHealthTree.mockResolvedValueOnce({ ...mockHealthTree, children: [] });
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/No child assets in health tree/i)).toBeInTheDocument();
    });
  });

  it('shows empty state when no contributors', async () => {
    api.getContributors.mockResolvedValueOnce({ ...mockContributors, contributors: [] });
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      const viewSelect = screen.getByLabelText(/View/i);
      fireEvent.change(viewSelect, { target: { value: 'contributors' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/No dependency contributors/i)).toBeInTheDocument();
    });
  });

  it('displays penalty information', async () => {
    api.getHealthTree.mockResolvedValueOnce(mockHealthTree);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Dep: -8/i)).toBeInTheDocument();
    });
  });

  it('handles view mode change', async () => {
    api.getHealthTree.mockResolvedValueOnce(mockHealthTree);
    api.getContributors.mockResolvedValueOnce(mockContributors);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      const viewSelect = screen.getByLabelText(/View/i);
      fireEvent.change(viewSelect, { target: { value: 'contributors' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Contributors/i)).toBeInTheDocument();
    });
  });

  it('handles max depth change', async () => {
    api.getHealthTree.mockResolvedValueOnce(mockHealthTree);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      const depthInput = screen.getByLabelText(/Max Depth/i);
      fireEvent.change(depthInput, { target: { value: '5' } });
    });
    
    await waitFor(() => {
      expect(api.getHealthTree).toHaveBeenLastCalledWith('asset-1', 5);
    });
  });

  it('displays explanation section', async () => {
    api.getHealthTree.mockResolvedValueOnce(mockHealthTree);
    
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/How Health Is Calculated/i)).toBeInTheDocument();
    });
  });

  it('displays penalty formula section', async () => {
    api.getHealthTree.mockResolvedValueOnce(mockHealthTree);
    
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Penalty Formula/i)).toBeInTheDocument();
    });
  });
});

describe('Tree Rendering', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
    api.getHealthTree.mockResolvedValueOnce(mockHealthTree);
  });

  it('renders tree nodes', async () => {
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText('Building A')).toBeInTheDocument();
    });
  });

  it('shows health score badges', async () => {
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      // Health score 72 should be visible
      const badges = screen.getAllByText('72');
      expect(badges.length).toBeGreaterThan(0);
    });
  });
});

describe('Penalty Display', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
  });

  it('displays dependency penalty', async () => {
    api.getHealthTree.mockResolvedValueOnce(mockHealthTree);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Dep: -8\.0/i)).toBeInTheDocument();
    });
  });

  it('displays local penalty', async () => {
    api.getHealthTree.mockResolvedValueOnce(mockHealthTree);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Local: -20/i)).toBeInTheDocument();
    });
  });
});

describe('Contributor Display', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
  });

  it('displays contributor penalties', async () => {
    api.getContributors.mockResolvedValueOnce(mockContributors);
    
    renderComponent();
    
    await waitFor () => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      const viewSelect = screen.getByLabelText(/View/i);
      fireEvent.change(viewSelect, { target: { value: 'contributors' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/-8\.0/i)).toBeInTheDocument();
    });
  });

  it('displays contributor depth', async () => {
    api.getContributors.mockResolvedValueOnce(mockContributors);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      const viewSelect = screen.getByLabelText(/View/i);
      fireEvent.change(viewSelect, { target: { value: 'contributors' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Depth 2/i)).toBeInTheDocument();
    });
  });
});

describe('Error Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assetsApi.getAssets.mockResolvedValueOnce({ items: mockAssets });
  });

  it('shows error state on fetch failure', async () => {
    api.getHealthTree.mockRejectedValueOnce(new Error('Network error'));
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Error: Network error/i)).toBeInTheDocument();
    });
  });
});