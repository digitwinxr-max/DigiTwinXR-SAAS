/**
 * Tests for Digital Logbook Components
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock logbook API
jest.mock('../api/logbook', () => ({
  listEntries: jest.fn(),
  searchEntries: jest.fn(),
  createEntry: jest.fn(),
  getSummary: jest.fn()
}));

// Import after mock
import { DigitalLogbook } from '../pages/DigitalLogbook';
import { LogbookEntryCard } from '../components/LogbookEntryCard';
import * as logbookApi from '../api/logbook';

describe('DigitalLogbook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock API responses
    logbookApi.listEntries.mockResolvedValue({
      total: 2,
      entries: [
        {
          id: 'entry-1',
          title: 'Test Observation',
          entry_type: 'observation',
          severity: 'info',
          content: 'This is a test observation',
          author: 'Operator 1',
          timestamp: '2024-01-01T10:00:00Z'
        },
        {
          id: 'entry-2',
          title: 'Critical Incident',
          entry_type: 'incident',
          severity: 'critical',
          content: 'A critical incident occurred',
          author: 'Operator 2',
          timestamp: '2024-01-01T12:00:00Z'
        }
      ],
      limit: 50,
      offset: 0
    });
    
    logbookApi.getSummary.mockResolvedValue({
      total_entries: 100,
      by_severity: { info: 60, warning: 30, critical: 10 },
      by_type: { observation: 40, incident: 20 }
    });
  });

  it('renders the Digital Logbook page', () => {
    render(<DigitalLogbook />);
    
    expect(screen.getByText('Digital Logbook')).toBeInTheDocument();
  });

  it('renders filters', () => {
    render(<DigitalLogbook />);
    
    expect(screen.getByText('Filters')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Search entries...')).toBeInTheDocument();
  });

  it('renders entry list', async () => {
    render(<DigitalLogbook />);
    
    await waitFor(() => {
      expect(screen.getByText('Entries (2)')).toBeInTheDocument();
    });
  });

  it('renders new entry button', () => {
    render(<DigitalLogbook />);
    
    expect(screen.getByText('+ New Entry')).toBeInTheDocument();
  });

  it('loads entries on mount', async () => {
    render(<DigitalLogbook />);
    
    await waitFor(() => {
      expect(logbookApi.listEntries).toHaveBeenCalled();
    });
  });

  it('loads summary on mount', async () => {
    render(<DigitalLogbook />);
    
    await waitFor(() => {
      expect(logbookApi.getSummary).toHaveBeenCalled();
    });
  });

  it('shows severity colors in summary', async () => {
    render(<DigitalLogbook />);
    
    await waitFor(() => {
      expect(screen.getByText('Info: 60')).toBeInTheDocument();
      expect(screen.getByText('Warning: 30')).toBeInTheDocument();
      expect(screen.getByText('Critical: 10')).toBeInTheDocument();
    });
  });

  it('opens new entry modal', () => {
    render(<DigitalLogbook />);
    
    fireEvent.click(screen.getByText('+ New Entry'));
    
    expect(screen.getByText('New Logbook Entry')).toBeInTheDocument();
  });

  it('closes new entry modal', () => {
    render(<DigitalLogbook />);
    
    fireEvent.click(screen.getByText('+ New Entry'));
    fireEvent.click(screen.getByText('×'));
    
    expect(screen.queryByText('New Logbook Entry')).not.toBeInTheDocument();
  });
});

describe('LogbookEntryCard', () => {
  const mockEntry = {
    id: 'entry-1',
    title: 'Test Observation',
    entry_type: 'observation',
    severity: 'info',
    content: 'This is a test observation with some content',
    author: 'Operator 1',
    timestamp: '2024-01-01T10:00:00Z',
    entity_type: 'asset',
    entity_id: 'asset-001',
    timeline_snapshot_id: null
  };

  it('renders entry title', () => {
    render(<LogbookEntryCard entry={mockEntry} />);
    
    expect(screen.getByText('Test Observation')).toBeInTheDocument();
  });

  it('renders entry type badge', () => {
    render(<LogbookEntryCard entry={mockEntry} />);
    
    expect(screen.getByText('observation')).toBeInTheDocument();
  });

  it('renders severity badge', () => {
    render(<LogbookEntryCard entry={mockEntry} />);
    
    expect(screen.getByText('info')).toBeInTheDocument();
  });

  it('renders author', () => {
    render(<LogbookEntryCard entry={mockEntry} />);
    
    expect(screen.getByText('Operator 1')).toBeInTheDocument();
  });

  it('renders timestamp', () => {
    render(<LogbookEntryCard entry={mockEntry} />);
    
    // Should display formatted timestamp
    expect(screen.getByText(/2024/)).toBeInTheDocument();
  });

  it('renders content preview', () => {
    render(<LogbookEntryCard entry={mockEntry} />);
    
    expect(screen.getByText(/This is a test observation/)).toBeInTheDocument();
  });

  it('renders entity reference', () => {
    render(<LogbookEntryCard entry={mockEntry} />);
    
    expect(screen.getByText('asset/asset-001')).toBeInTheDocument();
  });

  it('shows timeline indicator when present', () => {
    const entryWithTimeline = {
      ...mockEntry,
      timeline_snapshot_id: 'snap-123'
    };
    
    render(<LogbookEntryCard entry={entryWithTimeline} />);
    
    expect(screen.getByText('⏱️')).toBeInTheDocument();
  });

  it('handles click', () => {
    const onClick = jest.fn();
    render(<LogbookEntryCard entry={mockEntry} onClick={onClick} />);
    
    fireEvent.click(screen.getByText('Test Observation'));
    
    expect(onClick).toHaveBeenCalled();
  });

  it('shows selected state', () => {
    render(<LogbookEntryCard entry={mockEntry} isSelected={true} />);
    
    expect(screen.getByText('Test Observation').closest('.logbook-entry-card')).toHaveClass('selected');
  });

  it('truncates long content', () => {
    const longContent = 'A'.repeat(200);
    const entryWithLongContent = {
      ...mockEntry,
      content: longContent
    };
    
    render(<LogbookEntryCard entry={entryWithLongContent} />);
    
    // Should truncate with ellipsis
    expect(screen.getByText(/\.\.\.$/)).toBeInTheDocument();
  });
});

describe('Severity Colors', () => {
  it('shows correct color for info severity', () => {
    const entry = {
      id: '1',
      title: 'Info Entry',
      entry_type: 'observation',
      severity: 'info',
      content: 'Content',
      author: 'Test',
      timestamp: '2024-01-01T00:00:00Z'
    };
    
    render(<LogbookEntryCard entry={entry} />);
    
    const badge = screen.getByText('info');
    expect(badge).toHaveStyle({ backgroundColor: '#2196F3' });
  });

  it('shows correct color for warning severity', () => {
    const entry = {
      id: '1',
      title: 'Warning Entry',
      entry_type: 'observation',
      severity: 'warning',
      content: 'Content',
      author: 'Test',
      timestamp: '2024-01-01T00:00:00Z'
    };
    
    render(<LogbookEntryCard entry={entry} />);
    
    const badge = screen.getByText('warning');
    expect(badge).toHaveStyle({ backgroundColor: '#FF9800' });
  });

  it('shows correct color for critical severity', () => {
    const entry = {
      id: '1',
      title: 'Critical Entry',
      entry_type: 'incident',
      severity: 'critical',
      content: 'Content',
      author: 'Test',
      timestamp: '2024-01-01T00:00:00Z'
    };
    
    render(<LogbookEntryCard entry={entry} />);
    
    const badge = screen.getByText('critical');
    expect(badge).toHaveStyle({ backgroundColor: '#F44336' });
  });
});

describe('Entry Types', () => {
  const types = [
    { type: 'observation', icon: '👁' },
    { type: 'incident', icon: '🚨' },
    { type: 'maintenance', icon: '🔧' },
    { type: 'inspection', icon: '🔍' },
    { type: 'investigation', icon: '📋' },
    { type: 'annotation', icon: '📝' }
  ];

  types.forEach(({ type, icon }) => {
    it(`renders ${type} type icon`, () => {
      const entry = {
        id: '1',
        title: 'Test Entry',
        entry_type: type,
        severity: 'info',
        content: 'Content',
        author: 'Test',
        timestamp: '2024-01-01T00:00:00Z'
      };
      
      render(<LogbookEntryCard entry={entry} />);
      
      expect(screen.getByText(`${icon} ${type}`)).toBeInTheDocument();
    });
  });
});
