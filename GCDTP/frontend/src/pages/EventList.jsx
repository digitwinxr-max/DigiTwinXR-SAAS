import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getEvents } from '../api/events';

function EventList() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadEvents();
  }, [filter]);

  async function loadEvents() {
    try {
      setLoading(true);
      const params = {};
      if (filter === 'active') params.status = 'ACTIVE';
      if (filter === 'resolved') params.status = 'RESOLVED';
      
      const data = await getEvents(params);
      setEvents(data.items);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
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

  function getStatusClass(status) {
    return status === 'ACTIVE' ? 'status-active' : 'status-resolved';
  }

  if (loading) return <div className="loading">Loading events...</div>;

  return (
    <div>
      <h2>Events</h2>
      
      <div className="page-header">
        <div className="filter-group">
          <label>Filter:</label>
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">All Events</option>
            <option value="active">Active Only</option>
            <option value="resolved">Resolved Only</option>
          </select>
        </div>
        <Link to="/events/active">
          <button>View Active Events</button>
        </Link>
      </div>
      
      {error && <div className="error">{error}</div>}
      
      {events.length === 0 ? (
        <p>No events found.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Severity</th>
              <th>Status</th>
              <th>Type</th>
              <th>Message</th>
              <th>Sensor</th>
              <th>Timestamp</th>
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
                <td>
                  <span className={`status-badge ${getStatusClass(event.status)}`}>
                    {event.status}
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
                <td>{new Date(event.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default EventList;