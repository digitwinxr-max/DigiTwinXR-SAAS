import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getActiveEvents, resolveEvent } from '../api/events';

function ActiveEvents() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [severityFilter, setSeverityFilter] = useState('all');

  useEffect(() => {
    loadEvents();
  }, [severityFilter]);

  async function loadEvents() {
    try {
      setLoading(true);
      const params = {};
      if (severityFilter !== 'all') params.severity = severityFilter;
      
      const data = await getActiveEvents(params);
      setEvents(data.items);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleResolve(eventId) {
    if (!window.confirm('Are you sure you want to resolve this event?')) return;
    
    try {
      await resolveEvent(eventId);
      loadEvents();
    } catch (err) {
      setError(err.message);
    }
  }

  function getSeverityClass(severity) {
    switch (severity) {
      case 'CRITICAL': return 'severity-critical';
      case 'WARNING': return 'severity-warning';
      case 'OK': return 'severity-ok';
      default: return '';
    }
  }

  // Count events by severity
  const criticalCount = events.filter(e => e.severity === 'CRITICAL').length;
  const warningCount = events.filter(e => e.severity === 'WARNING').length;

  if (loading) return <div className="loading">Loading active events...</div>;

  return (
    <div>
      <h2>Active Events</h2>
      
      <div className="event-summary">
        <div className="summary-card critical">
          <span className="count">{criticalCount}</span>
          <span className="label">Critical</span>
        </div>
        <div className="summary-card warning">
          <span className="count">{warningCount}</span>
          <span className="label">Warning</span>
        </div>
        <div className="summary-card total">
          <span className="count">{events.length}</span>
          <span className="label">Total Active</span>
        </div>
      </div>
      
      <div className="page-header">
        <div className="filter-group">
          <label>Severity Filter:</label>
          <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
            <option value="all">All Severities</option>
            <option value="CRITICAL">Critical Only</option>
            <option value="WARNING">Warning Only</option>
          </select>
        </div>
        <Link to="/events">
          <button>View All Events</button>
        </Link>
      </div>
      
      {error && <div className="error">{error}</div>}
      
      {events.length === 0 ? (
        <p className="no-events">No active events. All systems normal.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Severity</th>
              <th>Type</th>
              <th>Message</th>
              <th>Sensor</th>
              <th>Value</th>
              <th>Timestamp</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr key={event.id}>
                <td>
                  <span className={`severity-badge ${getSeverityClass(event.severity)}`}>
                    {event.severity}
                  </span>
                </td>
                <td>{event.event_type}</td>
                <td className="message-cell">{event.message}</td>
                <td>
                  {event.sensor_id ? (
                    <Link to={`/sensors/${event.sensor_id}`}>
                      {event.sensor_id.substring(0, 8)}...
                    </Link>
                  ) : 'N/A'}
                </td>
                <td>{event.value !== null ? event.value : 'N/A'}</td>
                <td>{new Date(event.timestamp).toLocaleString()}</td>
                <td className="actions">
                  <button onClick={() => handleResolve(event.id)}>
                    Resolve
                  </button>
                  <Link to={`/events/${event.id}`}>
                    <button>Details</button>
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default ActiveEvents;