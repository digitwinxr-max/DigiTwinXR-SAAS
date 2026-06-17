import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getMeasurement, deleteMeasurement } from '../api/measurements';

function MeasurementDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [measurement, setMeasurement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadMeasurement();
  }, [id]);

  async function loadMeasurement() {
    try {
      setLoading(true);
      const data = await getMeasurement(id);
      setMeasurement(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete() {
    if (!window.confirm('Are you sure you want to delete this measurement?')) return;
    try {
      await deleteMeasurement(id);
      navigate('/measurements');
    } catch (err) {
      setError(err.message);
    }
  }

  function getQualityClass(quality) {
    switch (quality) {
      case 'good': return 'quality-good';
      case 'uncertain': return 'quality-uncertain';
      case 'bad': return 'quality-bad';
      default: return '';
    }
  }

  if (loading) return <div className="loading">Loading...</div>;
  if (error && !measurement) return <div className="error">{error}</div>;

  return (
    <div>
      <h2>Measurement Details</h2>
      
      {error && <div className="error">{error}</div>}
      
      {measurement && (
        <div className="measurement-detail">
          <div className="info-row">
            <span className="label">ID:</span> {measurement.id}
          </div>
          <div className="info-row">
            <span className="label">Sensor:</span>{' '}
            <Link to={`/sensors/${measurement.sensor_id}`}>
              {measurement.sensor_id}
            </Link>
          </div>
          <div className="info-row">
            <span className="label">Timestamp:</span>{' '}
            {new Date(measurement.timestamp).toLocaleString()}
          </div>
          <div className="info-row">
            <span className="label">Value:</span> {measurement.value}
          </div>
          <div className="info-row">
            <span className="label">Quality:</span>{' '}
            <span className={`quality-badge ${getQualityClass(measurement.quality)}`}>
              {measurement.quality}
            </span>
          </div>
          <div className="info-row">
            <span className="label">Created:</span>{' '}
            {new Date(measurement.created_at).toLocaleString()}
          </div>
          
          <div className="actions">
            <button className="danger" onClick={handleDelete}>Delete</button>
            <Link to="/measurements">
              <button>Back</button>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

export default MeasurementDetails;
