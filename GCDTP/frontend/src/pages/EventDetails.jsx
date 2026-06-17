import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getEvent, resolveEvent } from '../api/events';

function EventDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [resolving, setResolving] = useState(false);
  const [resolutionNotes, setResolutionNotes] = useState('');

  useEffect(() => {
    loadEvent();
  }, [id]);

  async function loadEvent() {
    try {
      setLoading(true);
      const data = await getEvent(id);
      setEvent(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleResolve() {
    if (!window.confirm('Are you sure you want to resolve this event?')) return;
    
    try {
      setResolving(true);
      await resolveEvent(id, resolutionNotes || null);
      loadEvent();
    } catch (err) {
      setError(err.message);
    } finally {
      setResolving(false);
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

  if (loading) return <div className="loading">Loading...</div>;
  if (error && !event) return <div className="error">{error}</div>;

  return (
    <div>
      <h2>Event Details</h2>
      
      {error && <div className="error">{error}</div>}
      
      {event && (
        <div className="event-detail">
          <div className="info-row">
            <span className="label">Severity:</span>
            <span className={`severity-badge ${getSeverityClass(event.severity)}`}>
              {event.severity}
            </span>
          </div>
          
          <div className="info-row">
            <span className="label">Status:</span>
            <span className={`status-badge ${getStatusClass(event.status)}`}>
              {event.status}
            </span>
          </div>
          
          <div className="info-row">
            <span className="label">Type:</span> {event.event_type}
          </div>
          
          <div className="info-row">
            <span className="label">Message:</span>
            <p className="message-text">{event.message}</p>
          </div>
          
          <div className="info-row">
            <span className="label">Value:</span> {event.value !== null ? event.value : 'N/A'}
          </div>
          
          <div className="info-row">
            <span className="label">Sensor:</span>
            {event.sensor_id ? (
              <Link to={`/sensors/${event.sensor_id}`}>{event.sensor_id}</Link>
            ) : 'N/A'}
          </div>
          
          <div className="info-row">
            <span className="label">Asset:</span>
            {event.asset_id ? (
              <Link to={`/assets/${event.asset_id}`}>{event.asset_id}</Link>
            ) : 'N/A'}
          </div>
          
          <div className="info-row">
            <span className="label">Threshold Rule:</span>
            {event.threshold_rule_id || 'N/A'}
          </div>
          
          <div className="info-row">
            <span className="label">Timestamp:</span>
            {new Date(event.timestamp).toLocaleString()}
          </div>
          
          <div className="info-row">
            <span className="label">Created:</span>
            {new Date(event.created_at).toLocaleString()}
          </div>
          
          {event.status === 'ACTIVE' && (
            <div className="resolve-section">
              <h3>Resolve Event</h3>
              <textarea
                placeholder="Resolution notes (optional)"
                value={resolutionNotes}
                onChange={(e) => setResolutionNotes(e.target.value)}
                rows={3}
              />
              <div className="actions">
                <button 
                  onClick={handleResolve} 
                  disabled={resolving}
                >
                  {resolving ? 'Resolving...' : 'Resolve Event'}
                </button>
                <Link to="/events">
                  <button>Back</button>
                </Link>
              </div>
            </div>
          )}
          
          <div className="actions">
            <Link to="/events">
              <button>Back to Events</button>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

export default EventDetails;