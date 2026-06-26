/**
 * Digital Logbook Page
 * 
 * Immutable operational logbook for storing operator observations,
 * maintenance remarks, incident narratives, and timeline references.
 */

import React, { useState, useEffect } from 'react';
import { LogbookEntryCard } from '../components/LogbookEntryCard';
import {
  listEntries,
  searchEntries,
  createEntry,
  getSummary
} from '../api/logbook';
import './DigitalLogbook.css';

const ENTRY_TYPES = [
  'observation',
  'incident',
  'maintenance',
  'inspection',
  'investigation',
  'annotation'
];

const SEVERITIES = ['info', 'warning', 'critical'];

export function DigitalLogbook() {
  // Filter state
  const [severityFilter, setSeverityFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [searchQuery, setSearchQuery] = useState('');
  
  // Entries state
  const [entries, setEntries] = useState([]);
  const [totalEntries, setTotalEntries] = useState(0);
  
  // Selected entry
  const [selectedEntry, setSelectedEntry] = useState(null);
  
  // Summary state
  const [summary, setSummary] = useState(null);
  
  // Loading state
  const [loading, setLoading] = useState(false);

  // New entry form
  const [showNewEntry, setShowNewEntry] = useState(false);
  const [newEntry, setNewEntry] = useState({
    title: '',
    entry_type: 'observation',
    severity: 'info',
    content: '',
    author: 'Operator'
  });

  // Load entries on mount
  useEffect(() => {
    loadEntries();
    loadSummary();
  }, []);

  const loadEntries = async () => {
    setLoading(true);
    try {
      let result;
      
      if (searchQuery) {
        result = await searchEntries({
          query: searchQuery,
          severity: severityFilter || undefined,
          entry_type: typeFilter || undefined,
          start_time: dateRange.start || undefined,
          end_time: dateRange.end || undefined
        });
      } else {
        result = await listEntries({
          severity: severityFilter || undefined,
          entry_type: typeFilter || undefined
        });
      }
      
      setEntries(result.entries || []);
      setTotalEntries(result.total || 0);
    } catch (error) {
      console.error('Failed to load entries:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    try {
      const sum = await getSummary();
      setSummary(sum);
    } catch (error) {
      console.error('Failed to load summary:', error);
    }
  };

  const handleSearch = () => {
    loadEntries();
  };

  const handleCreateEntry = async () => {
    try {
      await createEntry(newEntry);
      setShowNewEntry(false);
      setNewEntry({
        title: '',
        entry_type: 'observation',
        severity: 'info',
        content: '',
        author: 'Operator'
      });
      loadEntries();
      loadSummary();
    } catch (error) {
      console.error('Failed to create entry:', error);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      info: '#2196F3',
      warning: '#FF9800',
      critical: '#F44336'
    };
    return colors[severity] || '#9E9E9E';
  };

  const getTypeIcon = (type) => {
    const icons = {
      observation: '👁',
      incident: '🚨',
      maintenance: '🔧',
      inspection: '🔍',
      investigation: '📋',
      annotation: '📝'
    };
    return icons[type] || '📄';
  };

  return (
    <div className="digital-logbook">
      {/* Header */}
      <header className="logbook-header">
        <h1>Digital Logbook</h1>
        <div className="header-actions">
          <button onClick={() => setShowNewEntry(true)} className="new-entry-btn">
            + New Entry
          </button>
        </div>
      </header>

      <div className="logbook-layout">
        {/* Left Panel - Filters */}
        <aside className="logbook-sidebar left-panel">
          <div className="filters-section">
            <h3>Filters</h3>
            
            {/* Search */}
            <div className="filter-field">
              <label>Search</label>
              <div className="search-input">
                <input
                  type="text"
                  placeholder="Search entries..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                />
                <button onClick={handleSearch}>🔍</button>
              </div>
            </div>
            
            {/* Severity Filter */}
            <div className="filter-field">
              <label>Severity</label>
              <select
                value={severityFilter}
                onChange={(e) => {
                  setSeverityFilter(e.target.value);
                  setTimeout(loadEntries, 0);
                }}
              >
                <option value="">All</option>
                {SEVERITIES.map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            
            {/* Type Filter */}
            <div className="filter-field">
              <label>Type</label>
              <select
                value={typeFilter}
                onChange={(e) => {
                  setTypeFilter(e.target.value);
                  setTimeout(loadEntries, 0);
                }}
              >
                <option value="">All Types</option>
                {ENTRY_TYPES.map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
            
            {/* Date Range */}
            <div className="filter-field">
              <label>Date Range</label>
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                placeholder="Start"
              />
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                placeholder="End"
              />
            </div>
            
            <button onClick={loadEntries} className="apply-btn">
              Apply Filters
            </button>
          </div>
          
          {/* Summary */}
          {summary && (
            <div className="summary-section">
              <h3>Summary</h3>
              <div className="summary-stat">
                <span className="stat-value">{summary.total_entries}</span>
                <span className="stat-label">Total Entries</span>
              </div>
              <div className="severity-summary">
                <div className="severity-item">
                  <span className="dot" style={{ backgroundColor: getSeverityColor('info') }} />
                  <span>Info: {summary.by_severity?.info || 0}</span>
                </div>
                <div className="severity-item">
                  <span className="dot" style={{ backgroundColor: getSeverityColor('warning') }} />
                  <span>Warning: {summary.by_severity?.warning || 0}</span>
                </div>
                <div className="severity-item">
                  <span className="dot" style={{ backgroundColor: getSeverityColor('critical') }} />
                  <span>Critical: {summary.by_severity?.critical || 0}</span>
                </div>
              </div>
            </div>
          )}
        </aside>

        {/* Center Panel - Entries */}
        <main className="logbook-main">
          <div className="entries-header">
            <h3>Entries ({totalEntries})</h3>
          </div>
          
          {loading ? (
            <div className="loading">Loading entries...</div>
          ) : entries.length === 0 ? (
            <div className="empty-state">
              <p>No entries found</p>
            </div>
          ) : (
            <div className="entries-list">
              {entries.map(entry => (
                <LogbookEntryCard
                  key={entry.id}
                  entry={entry}
                  isSelected={selectedEntry?.id === entry.id}
                  onClick={() => setSelectedEntry(entry)}
                />
              ))}
            </div>
          )}
        </main>

        {/* Right Panel - Entry Details */}
        <aside className="logbook-sidebar right-panel">
          {selectedEntry ? (
            <div className="entry-details">
              <h3>Entry Details</h3>
              
              <div className="detail-header">
                <span className="type-badge" style={{
                  backgroundColor: getTypeIcon(selectedEntry.entry_type)
                }}>
                  {getTypeIcon(selectedEntry.entry_type)} {selectedEntry.entry_type}
                </span>
                <span className="severity-badge" style={{
                  backgroundColor: getSeverityColor(selectedEntry.severity)
                }}>
                  {selectedEntry.severity}
                </span>
              </div>
              
              <h4>{selectedEntry.title}</h4>
              
              <div className="detail-meta">
                <p><strong>Author:</strong> {selectedEntry.author}</p>
                <p><strong>Timestamp:</strong> {new Date(selectedEntry.timestamp).toLocaleString()}</p>
                {selectedEntry.entity_type && (
                  <p><strong>Entity:</strong> {selectedEntry.entity_type}/{selectedEntry.entity_id}</p>
                )}
              </div>
              
              <div className="detail-content">
                <h5>Content</h5>
                <p className="content-text">{selectedEntry.content}</p>
              </div>
              
              {selectedEntry.timeline_snapshot_id && (
                <div className="timeline-link">
                  <h5>Timeline Reference</h5>
                  <button
                    onClick={() => {/* Navigate to timeline */}}
                    className="timeline-btn"
                  >
                    View Timeline Frame
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="no-selection">
              <p>Select an entry to view details</p>
            </div>
          )}
        </aside>
      </div>

      {/* New Entry Modal */}
      {showNewEntry && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>New Logbook Entry</h2>
              <button onClick={() => setShowNewEntry(false)}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="form-field">
                <label>Title</label>
                <input
                  type="text"
                  value={newEntry.title}
                  onChange={(e) => setNewEntry(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Entry title"
                />
              </div>
              
              <div className="form-row">
                <div className="form-field">
                  <label>Type</label>
                  <select
                    value={newEntry.entry_type}
                    onChange={(e) => setNewEntry(prev => ({ ...prev, entry_type: e.target.value }))}
                  >
                    {ENTRY_TYPES.map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
                
                <div className="form-field">
                  <label>Severity</label>
                  <select
                    value={newEntry.severity}
                    onChange={(e) => setNewEntry(prev => ({ ...prev, severity: e.target.value }))}
                  >
                    {SEVERITIES.map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="form-field">
                <label>Author</label>
                <input
                  type="text"
                  value={newEntry.author}
                  onChange={(e) => setNewEntry(prev => ({ ...prev, author: e.target.value }))}
                />
              </div>
              
              <div className="form-field">
                <label>Content</label>
                <textarea
                  value={newEntry.content}
                  onChange={(e) => setNewEntry(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Enter observation, note, or narrative..."
                  rows={6}
                />
              </div>
            </div>
            
            <div className="modal-footer">
              <button onClick={() => setShowNewEntry(false)} className="cancel-btn">
                Cancel
              </button>
              <button onClick={handleCreateEntry} className="submit-btn">
                Create Entry
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DigitalLogbook;
