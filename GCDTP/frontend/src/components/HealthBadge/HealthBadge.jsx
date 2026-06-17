import React from 'react';

function HealthBadge({ score, status, size = 'normal', showScore = true }) {
  function getStatusClass(status) {
    switch (status) {
      case 'HEALTHY': return 'badge-healthy';
      case 'DEGRADED': return 'badge-degraded';
      case 'CRITICAL': return 'badge-critical';
      default: return 'badge-unknown';
    }
  }

  function getScoreClass(score) {
    if (score >= 80) return 'score-healthy';
    if (score >= 40) return 'score-degraded';
    return 'score-critical';
  }

  return (
    <span className={`health-badge ${getStatusClass(status)} ${size}`}>
      {showScore && score !== undefined && (
        <span className={`score ${getScoreClass(score)}`}>
          {score}
        </span>
      )}
      {status && (
        <span className="status">{status}</span>
      )}
    </span>
  );
}

export default HealthBadge;