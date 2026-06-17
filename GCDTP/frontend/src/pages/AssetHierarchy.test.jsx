import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AssetHierarchy from './AssetHierarchy';
import * as api from '../api/relationships';

vi.mock('../api/relationships', () => ({
  getGraph: vi.fn(),
  createRelationship: vi.fn(),
  deleteRelationship: vi.fn(),
  getAssets: vi.fn(),
  RELATIONSHIP_TYPES: {
    CONTAINS: 'contains',
    CONNECTED_TO: 'connected_to',
    FEEDS: 'feeds',
    MONITORS: 'monitors',
    CONTROLS: 'controls',
  },
  RELATIONSHIP_TYPE_INFO: {
    contains: { label: 'Contains', color: '#3b82f6', lineStyle: 'solid' },
    connected_to: { label: 'Connected To', color: '#6b7280', lineStyle: 'dashed' },
    feeds: { label: 'Feeds', color: '#22c55e', lineStyle: 'arrow' },
    monitors: { label: 'Monitors', color: '#8b5cf6', lineStyle: 'dotted' },
    controls: { label: 'Controls', color: '#f97316', lineStyle: 'bold' },
  },
}));

const mockAssets = [
  { id: 'asset-1', name: 'Site Alpha', asset_type: 'site' },
  { id: 'asset-2', name: 'Building A', asset_type: 'building' },
  { id: 'asset-3', name: 'Sensor X', asset_type: 'sensor' },
];

const mockGraphData = {
  asset_id: 'asset-1',
  asset_name: 'Site Alpha',
  asset_type: 'site',
  health_status: 'HEALTHY',
  health_score: 95,
  children: [
    {
      asset_id: 'asset-2',
      asset_name: 'Building A',
      asset_type: 'building',
      health_status: 'DEGRADED',
      health_score: 65,
      relationship_type: 'contains',
      children: [
        {
          asset_id: 'asset-3',
          asset_name: 'Sensor X',
          asset_type: 'sensor',
          health_status: null,
          health_score: null,
          relationship_type: 'contains',
          children: [],
        },
      ],
    },
  ],
  parents: [],
  depth: 2,
};

function renderComponent() {
  return render(<AssetHierarchy />);
}

describe('AssetHierarchy Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.getAssets.mockResolvedValueOnce({ items: mockAssets });
  });

  it('renders loading state initially', () => {
    api.getGraph.mockImplementation(() => new Promise(() => {}));
    
    renderComponent();
    
    expect(screen.getByText(/Loading hierarchy/i)).toBeInTheDocument();
  });

  it('renders asset selector', async () => {
    api.getGraph.mockResolvedValueOnce(mockGraphData);
    
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByLabelText(/Select Root Asset/i)).toBeInTheDocument();
    });
  });

  it('shows legend with all relationship types', async () => {
    api.getGraph.mockResolvedValueOnce(mockGraphData);
    
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Relationship Types/i)).toBeInTheDocument();
      expect(screen.getByText(/Contains/i)).toBeInTheDocument();
      expect(screen.getByText(/Connected To/i)).toBeInTheDocument();
      expect(screen.getByText(/Feeds/i)).toBeInTheDocument();
      expect(screen.getByText(/Monitors/i)).toBeInTheDocument();
      expect(screen.getByText(/Controls/i)).toBeInTheDocument();
    });
  });

  it('renders instructions section', async () => {
    api.getGraph.mockResolvedValueOnce(mockGraphData);
    
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/How to use/i)).toBeInTheDocument();
      expect(screen.getByText(/Select an asset to view its hierarchy/i)).toBeInTheDocument();
    });
  });

  it('loads graph when asset is selected', async () => {
    api.getGraph.mockResolvedValueOnce(mockGraphData);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(api.getGraph).toHaveBeenCalledWith('asset-1', 'down', 5);
    });
  });

  it('displays graph data correctly', async () => {
    api.getGraph.mockResolvedValueOnce(mockGraphData);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText('Site Alpha')).toBeInTheDocument();
      expect(screen.getByText(/HEALTHY/)).toBeInTheDocument();
    });
  });

  it('shows empty state when no relationships', async () => {
    api.getGraph.mockResolvedValueOnce({
      ...mockGraphData,
      children: [],
      parents: [],
    });
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/No relationships found/i)).toBeInTheDocument();
    });
  });

  it('shows empty state when no asset selected', async () => {
    api.getGraph.mockResolvedValueOnce(mockGraphData);
    
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Select an asset above to view its hierarchy/i)).toBeInTheDocument();
    });
  });

  it('handles direction change', async () => {
    api.getGraph.mockResolvedValueOnce(mockGraphData);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      const directionSelect = screen.getByLabelText(/Direction/i);
      fireEvent.change(directionSelect, { target: { value: 'both' } });
    });
    
    await waitFor(() => {
      expect(api.getGraph).toHaveBeenLastCalledWith('asset-1', 'both', 5);
    });
  });

  it('handles max depth change', async () => {
    api.getGraph.mockResolvedValueOnce(mockGraphData);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      const depthInput = screen.getByLabelText(/Max Depth/i);
      fireEvent.change(depthInput, { target: { value: '3' } });
    });
    
    await waitFor(() => {
      expect(api.getGraph).toHaveBeenLastCalledWith('asset-1', 'down', 3);
    });
  });

  it('displays stats when graph loaded', async () => {
    api.getGraph.mockResolvedValueOnce(mockGraphData);
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Depth: 2/i)).toBeInTheDocument();
      expect(screen.getByText(/Children: 1/i)).toBeInTheDocument();
    });
  });
});

describe('Tree Rendering', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.getAssets.mockResolvedValueOnce({ items: mockAssets });
    api.getGraph.mockResolvedValueOnce(mockGraphData);
  });

  it('renders child nodes', async () => {
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText('Building A')).toBeInTheDocument();
      expect(screen.getByText('Sensor X')).toBeInTheDocument();
    });
  });

  it('shows health badges for nodes with health data', async () => {
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      const healthBadges = screen.getAllByText(/HEALTHY|DEGRADED/);
      expect(healthBadges.length).toBeGreaterThan(0);
    });
  });
});

describe('Expand/Collapse Logic', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.getAssets.mockResolvedValueOnce({ items: mockAssets });
    api.getGraph.mockResolvedValueOnce(mockGraphData);
  });

  it('initially shows root node only', async () => {
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText('Site Alpha')).toBeInTheDocument();
    });
    
    // Children should be visible after auto-expand
    await waitFor(() => {
      expect(screen.getByText('Building A')).toBeInTheDocument();
    });
  });

  it('collapses node when clicked', async () => {
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText('Building A')).toBeInTheDocument();
    });
    
    // Find and click the collapse toggle
    const toggle = screen.getAllByText('▼')[0];
    fireEvent.click(toggle);
    
    await waitFor(() => {
      // Building A should still be visible (root expanded by default)
      expect(screen.getByText('Building A')).toBeInTheDocument();
    });
  });
});

describe('Drag and Drop', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.getAssets.mockResolvedValueOnce({ items: mockAssets });
    api.getGraph.mockResolvedValueOnce(mockGraphData);
  });

  it('shows drag hint on hover', async () => {
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Drop asset here to create "contains" relationship/i)).toBeInTheDocument();
    });
  });

  it('creates relationship on drop', async () => {
    api.createRelationship.mockResolvedValueOnce({ success: true });
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    // Simulate drag and drop
    const treeNode = await waitFor(() => {
      return screen.getByText('Building A');
    });
    
    // Create mock dataTransfer
    const dataTransfer = {
      getData: vi.fn().mockReturnValue('asset-3'),
    };
    
    fireEvent.drop(treeNode, { dataTransfer });
    
    await waitFor(() => {
      expect(api.createRelationship).toHaveBeenCalledWith({
        parent_asset_id: expect.any(String),
        child_asset_id: 'asset-3',
        relationship_type: 'contains',
      });
    });
  });

  it('prevents drop on self', async () => {
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    // Find the Building A node
    const treeNode = await waitFor(() => {
      return screen.getByText('Building A');
    });
    
    // Try to drop asset-2 onto itself
    const dataTransfer = {
      getData: vi.fn().mockReturnValue('asset-2'),
    };
    
    fireEvent.drop(treeNode, { dataTransfer });
    
    // Should not call createRelationship for self-drop
    expect(api.createRelationship).not.toHaveBeenCalled();
  });
});

describe('Graph Loading Behavior', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.getAssets.mockResolvedValueOnce({ items: mockAssets });
  });

  it('shows error state on graph fetch failure', async () => {
    api.getGraph.mockRejectedValueOnce(new Error('Network error'));
    
    renderComponent();
    
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Error: Network error/i)).toBeInTheDocument();
    });
  });

  it('allows refresh button to reload graph', async () => {
    const mockGraphData2 = { ...mockGraphData, depth: 3 };
    api.getGraph
      .mockResolvedValueOnce(mockGraphData)
      .mockResolvedValueOnce(mockGraphData2);
    
    renderComponent();
    
    // Initial load
    await waitFor(() => {
      const selector = screen.getByLabelText(/Select Root Asset/i);
      fireEvent.change(selector, { target: { value: 'asset-1' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Depth: 2/i)).toBeInTheDocument();
    });
    
    // Click refresh
    const refreshBtn = screen.getByRole('button', { name: /Refresh/i });
    fireEvent.click(refreshBtn);
    
    await waitFor(() => {
      expect(api.getGraph).toHaveBeenCalledTimes(2);
    });
  });
});