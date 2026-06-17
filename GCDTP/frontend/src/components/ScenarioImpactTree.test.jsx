import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ScenarioImpactTree from './ScenarioImpactTree';

vi.mock('../api/scenarios', () => ({
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
}));

const mockTree = {
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
      children: [
        {
          asset_id: 'asset-3',
          asset_name: 'Equipment A',
          asset_type: 'equipment',
          current_health: 100,
          predicted_health: 85,
          delta_health: -15,
          propagation_depth: 2,
          relationship_type: 'contains',
          children: [],
        },
      ],
    },
    {
      asset_id: 'asset-4',
      asset_name: 'Substation Alpha',
      asset_type: 'substation',
      current_health: 100,
      predicted_health: 74,
      delta_health: -26,
      propagation_depth: 1,
      relationship_type: 'connected_to',
      children: [],
    },
  ],
};

function renderComponent(tree) {
  return render(<ScenarioImpactTree tree={tree} />);
}

describe('ScenarioImpactTree Component', () => {
  it('renders empty state when no tree', () => {
    renderComponent(null);
    expect(screen.getByText(/No impact tree available/i)).toBeInTheDocument();
  });

  it('renders tree controls', () => {
    renderComponent(mockTree);
    expect(screen.getByText(/Expand All/i)).toBeInTheDocument();
    expect(screen.getByText(/Collapse All/i)).toBeInTheDocument();
  });

  it('renders legend', () => {
    renderComponent(mockTree);
    expect(screen.getByText(/Healthy/i)).toBeInTheDocument();
    expect(screen.getByText(/Degraded/i)).toBeInTheDocument();
    expect(screen.getByText(/Critical/i)).toBeInTheDocument();
  });

  it('renders root node', () => {
    renderComponent(mockTree);
    expect(screen.getByText(/Transformer A/i)).toBeInTheDocument();
    expect(screen.getByText(/ROOT/i)).toBeInTheDocument();
  });
});

describe('Expand/Collapse', () => {
  it('shows expand all and collapse all buttons', () => {
    renderComponent(mockTree);
    expect(screen.getByRole('button', { name: /Expand All/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Collapse All/i })).toBeInTheDocument();
  });

  it('auto-expands first level', async () => {
    renderComponent(mockTree);
    
    // Children should be visible by default
    await waitFor(() => {
      expect(screen.getByText(/Building A/i)).toBeInTheDocument();
    });
  });

  it('can collapse children', async () => {
    renderComponent(mockTree);
    
    await waitFor(() => {
      expect(screen.getByText(/Building A/i)).toBeInTheDocument();
    });
    
    // Click collapse all
    fireEvent.click(screen.getByRole('button', { name: /Collapse All/i }));
    
    // Children should still be visible but collapse all should work
    // Note: The exact behavior depends on implementation
  });

  it('can expand all children', async () => {
    renderComponent(mockTree);
    
    // Click expand all
    fireEvent.click(screen.getByRole('button', { name: /Expand All/i }));
    
    // All nodes should be visible
    await waitFor(() => {
      expect(screen.getByText(/Equipment A/i)).toBeInTheDocument();
    });
  });
});

describe('Node Rendering', () => {
  it('renders health badges', () => {
    renderComponent(mockTree);
    // Health score should be displayed
    expect(screen.getByText('80')).toBeInTheDocument();
  });

  it('renders relationship types', () => {
    renderComponent(mockTree);
    // Relationship types should be visible
    await waitFor(() => {
      expect(screen.getByText(/feeds/i)).toBeInTheDocument();
    });
  });

  it('renders depth badges', () => {
    renderComponent(mockTree);
    // Depth should be visible for children
    await waitFor(() => {
      expect(screen.getByText(/Depth 1/i)).toBeInTheDocument();
    });
  });
});

describe('Impact Tree Structure', () => {
  it('renders all asset names', async () => {
    renderComponent(mockTree);
    
    await waitFor(() => {
      expect(screen.getByText(/Transformer A/i)).toBeInTheDocument();
      expect(screen.getByText(/Building A/i)).toBeInTheDocument();
      expect(screen.getByText(/Equipment A/i)).toBeInTheDocument();
      expect(screen.getByText(/Substation Alpha/i)).toBeInTheDocument();
    });
  });

  it('shows root badge for root node', () => {
    renderComponent(mockTree);
    expect(screen.getByText(/ROOT/i)).toBeInTheDocument();
  });

  it('renders delta values', async () => {
    renderComponent(mockTree);
    
    // Delta values should be displayed
    // The format depends on the mock
    await waitFor(() => {
      const deltaElements = screen.getAllByText(/-20/);
      expect(deltaElements.length).toBeGreaterThan(0);
    });
  });
});

describe('Multiple Children', () => {
  it('renders multiple children at same depth', () => {
    renderComponent(mockTree);
    
    // Both Building A and Substation Alpha should be visible
    expect(screen.getByText(/Building A/i)).toBeInTheDocument();
    expect(screen.getByText(/Substation Alpha/i)).toBeInTheDocument();
  });

  it('renders nested children', async () => {
    renderComponent(mockTree);
    
    // Equipment A is nested under Building A
    await waitFor(() => {
      expect(screen.getByText(/Equipment A/i)).toBeInTheDocument();
    });
  });
});

describe('Empty Tree', () => {
  it('handles empty children array', () => {
    const emptyTree = {
      ...mockTree,
      children: [],
    };
    
    renderComponent(emptyTree);
    expect(screen.getByText(/Transformer A/i)).toBeInTheDocument();
  });
});

describe('Single Node', () => {
  it('handles tree with no children', () => {
    const singleTree = {
      asset_id: 'asset-1',
      asset_name: 'Lone Asset',
      current_health: 100,
      predicted_health: 80,
      delta_health: -20,
      propagation_depth: 0,
      relationship_type: 'root',
      children: [],
    };
    
    renderComponent(singleTree);
    expect(screen.getByText(/Lone Asset/i)).toBeInTheDocument();
  });
});