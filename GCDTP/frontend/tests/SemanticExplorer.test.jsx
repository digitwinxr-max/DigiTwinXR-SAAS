/**
 * Tests for SemanticExplorer Component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock API
jest.mock('../api/semantic', () => ({
  searchSemantic: jest.fn(),
  getContext: jest.fn(),
  getGraph: jest.fn(),
  listEntities: jest.fn(),
  getTagSummary: jest.fn()
}));

// Import after mock
import { SemanticExplorer } from '../pages/SemanticExplorer';
import * as semanticApi from '../api/semantic';

describe('SemanticExplorer', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock API responses
    semanticApi.getTagSummary.mockResolvedValue({
      tags: [
        { tag_name: 'power', entity_count: 10 },
        { tag_name: 'water', entity_count: 8 },
        { tag_name: 'critical', entity_count: 5 }
      ]
    });
    
    semanticApi.searchSemantic.mockResolvedValue({
      total: 2,
      results: [
        {
          entity: {
            id: 'entity-1',
            name: 'Test Substation',
            entity_type: 'asset',
            category: 'power',
            ontology_class: 'power_grid.substation',
            tags: [{ tag_name: 'voltage', tag_value: '400V' }]
          }
        },
        {
          entity: {
            id: 'entity-2',
            name: 'Test Sensor',
            entity_type: 'sensor',
            category: 'power',
            ontology_class: 'sensor.voltage',
            tags: []
          }
        }
      ]
    });
    
    semanticApi.getContext.mockResolvedValue({
      entity: {
        id: 'entity-1',
        name: 'Test Substation',
        entity_type: 'asset',
        category: 'power',
        ontology_class: 'power_grid.substation',
        tags: [{ tag_name: 'voltage', tag_value: '400V' }]
      },
      sensors: { entities: [], count: 0 },
      events: { entities: [], count: 0 },
      health: { entities: [], count: 0 },
      documents: { entities: [], count: 0 },
      timeline_entries: { entities: [], count: 0 },
      work_orders: { entities: [], count: 0 },
      relationships: []
    });
  });

  it('renders the SemanticExplorer page', () => {
    render(<SemanticExplorer />);
    
    expect(screen.getByText('Semantic Explorer')).toBeInTheDocument();
  });

  it('renders search inputs', () => {
    render(<SemanticExplorer />);
    
    expect(screen.getByPlaceholderText('Search entities...')).toBeInTheDocument();
    expect(screen.getByText('All Types')).toBeInTheDocument();
  });

  it('renders tag summary', async () => {
    render(<SemanticExplorer />);
    
    await waitFor(() => {
      expect(screen.getByText('power')).toBeInTheDocument();
      expect(screen.getByText('water')).toBeInTheDocument();
    });
  });

  it('performs search on button click', async () => {
    render(<SemanticExplorer />);
    
    const searchButton = screen.getByText('Search');
    fireEvent.click(searchButton);
    
    await waitFor(() => {
      expect(semanticApi.searchSemantic).toHaveBeenCalled();
    });
  });

  it('renders search results', async () => {
    render(<SemanticExplorer />);
    
    const searchButton = screen.getByText('Search');
    fireEvent.click(searchButton);
    
    await waitFor(() => {
      expect(screen.getByText('Test Substation')).toBeInTheDocument();
      expect(screen.getByText('Test Sensor')).toBeInTheDocument();
    });
  });

  it('renders entity type badges', async () => {
    render(<SemanticExplorer />);
    
    const searchButton = screen.getByText('Search');
    fireEvent.click(searchButton);
    
    await waitFor(() => {
      const badges = screen.getAllByText(/asset|sensor/i);
      expect(badges.length).toBeGreaterThan(0);
    });
  });

  it('shows context panel when entity is selected', async () => {
    render(<SemanticExplorer />);
    
    const searchButton = screen.getByText('Search');
    fireEvent.click(searchButton);
    
    await waitFor(() => {
      const entityCard = screen.getByText('Test Substation');
      fireEvent.click(entityCard);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Context')).toBeInTheDocument();
    });
  });

  it('filters by entity type', async () => {
    render(<SemanticExplorer />);
    
    const typeSelect = screen.getByRole('combobox');
    fireEvent.change(typeSelect, { target: { value: 'asset' } });
    
    const searchButton = screen.getByText('Search');
    fireEvent.click(searchButton);
    
    await waitFor(() => {
      expect(semanticApi.searchSemantic).toHaveBeenCalledWith(
        expect.objectContaining({ entity_type: 'asset' })
      );
    });
  });

  it('loads graph data', async () => {
    semanticApi.getGraph.mockResolvedValue({
      nodes: [
        { id: '1', name: 'Node 1', entity_type: 'asset' },
        { id: '2', name: 'Node 2', entity_type: 'sensor' }
      ],
      edges: [
        { id: 'e1', source: '1', target: '2', relationship_type: 'observed_by' }
      ]
    });
    
    render(<SemanticExplorer />);
    
    const showGraphButton = screen.getByText('Show Graph');
    fireEvent.click(showGraphButton);
    
    await waitFor(() => {
      expect(semanticApi.getGraph).toHaveBeenCalled();
      expect(screen.getByText('Semantic Graph')).toBeInTheDocument();
    });
  });
});

describe('Search Behavior', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    semanticApi.getTagSummary.mockResolvedValue({ tags: [] });
    semanticApi.searchSemantic.mockResolvedValue({ total: 0, results: [] });
  });

  it('updates search query state', () => {
    render(<SemanticExplorer />);
    
    const searchInput = screen.getByPlaceholderText('Search entities...');
    fireEvent.change(searchInput, { target: { value: 'power' } });
    
    expect(searchInput.value).toBe('power');
  });

  it('calls search with text query', async () => {
    render(<SemanticExplorer />);
    
    const searchInput = screen.getByPlaceholderText('Search entities...');
    fireEvent.change(searchInput, { target: { value: 'power' } });
    
    const searchButton = screen.getByText('Search');
    fireEvent.click(searchButton);
    
    await waitFor(() => {
      expect(semanticApi.searchSemantic).toHaveBeenCalledWith(
        expect.objectContaining({ query: 'power' })
      );
    });
  });
});

describe('Context Rendering', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    semanticApi.getTagSummary.mockResolvedValue({ tags: [] });
    
    semanticApi.searchSemantic.mockResolvedValue({
      total: 1,
      results: [
        {
          entity: {
            id: 'entity-1',
            name: 'Complex Entity',
            entity_type: 'asset',
            category: 'power',
            ontology_class: 'power_grid.substation',
            description: 'A complex power substation',
            tags: [
              { tag_name: 'voltage', tag_value: '400V' },
              { tag_name: 'location', tag_value: 'downtown' }
            ]
          }
        }
      ]
    });
    
    semanticApi.getContext.mockResolvedValue({
      entity: {
        id: 'entity-1',
        name: 'Complex Entity',
        entity_type: 'asset',
        category: 'power',
        ontology_class: 'power_grid.substation',
        description: 'A complex power substation',
        tags: [
          { tag_name: 'voltage', tag_value: '400V' },
          { tag_name: 'location', tag_value: 'downtown' }
        ]
      },
      asset: {
        id: 'asset-related',
        name: 'Related Asset',
        category: 'power',
        ontology_class: 'power_grid.transformer',
        tags: []
      },
      sensors: { 
        entities: [
          { name: 'Voltage Sensor', entity_type: 'sensor' },
          { name: 'Current Sensor', entity_type: 'sensor' }
        ], 
        count: 2 
      },
      events: { entities: [{ name: 'Event 1', entity_type: 'event' }], count: 1 },
      health: { entities: [], count: 0 },
      documents: { entities: [], count: 0 },
      timeline_entries: { entities: [], count: 0 },
      work_orders: { entities: [], count: 0 },
      relationships: [
        { relationship_type: 'observed_by' },
        { relationship_type: 'caused_by' }
      ]
    });
  });

  it('renders entity details in context', async () => {
    render(<SemanticExplorer />);
    
    const searchButton = screen.getByText('Search');
    fireEvent.click(searchButton);
    
    await waitFor(() => {
      const entityCard = screen.getByText('Complex Entity');
      fireEvent.click(entityCard);
    });
    
    await waitFor(() => {
      expect(screen.getByText('A complex power substation')).toBeInTheDocument();
      expect(screen.getByText('Class:')).toBeInTheDocument();
    });
  });

  it('renders related sensors in context', async () => {
    render(<SemanticExplorer />);
    
    const searchButton = screen.getByText('Search');
    fireEvent.click(searchButton);
    
    await waitFor(() => {
      const entityCard = screen.getByText('Complex Entity');
      fireEvent.click(entityCard);
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Sensors \(2\)/)).toBeInTheDocument();
      expect(screen.getByText('Voltage Sensor')).toBeInTheDocument();
    });
  });

  it('renders relationships in context', async () => {
    render(<SemanticExplorer />);
    
    const searchButton = screen.getByText('Search');
    fireEvent.click(searchButton);
    
    await waitFor(() => {
      const entityCard = screen.getByText('Complex Entity');
      fireEvent.click(entityCard);
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Relationships \(2\)/)).toBeInTheDocument();
    });
  });
});
