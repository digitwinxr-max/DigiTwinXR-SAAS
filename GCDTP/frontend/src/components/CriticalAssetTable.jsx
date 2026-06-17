/**
 * Critical Asset Table Component
 * 
 * Displays ranked list of critical assets with scores.
 */

import React from 'react';
import {
  getCriticalityColor,
  getResilienceColor,
  getCriticalityLevel,
  formatRecommendationType,
} from '../api/resilience';


function CriticalAssetTable({ assets, onSelectAsset, selectedAsset }) {
  if (!assets || assets.length === 0) {
    return (
      <div className="critical-asset-table empty">
        <p>No critical assets found.</p>
      </div>
    );
  }


  return (
    <div className="critical-asset-table">
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Asset</th>
            <th>Type</th>
            <th>Criticality</th>
            <th>Resilience</th>
            <th>SPOF</th>
            <th>Top Recommendation</th>
          </tr>
        </thead>
        <tbody>
          {assets.map((asset, index) => (
            <tr
              key={asset.asset_id}
              className={selectedAsset === asset.asset_id ? 'selected' : ''}
              onClick={() => onSelectAsset && onSelectAsset(asset.asset_id)}
            >
              <td className="rank">#{index + 1}</td>
              <td className="asset-name">{asset.asset_name}</td>
              <td className="asset-type">{asset.asset_type}</td>
              <td className="criticality">
                <div className="score-cell">
                  <div 
                    className="score-bar"
                    style={{ 
                      width: `${asset.criticality_score}%`,
                      backgroundColor: getCriticalityColor(asset.criticality_score)
                    }}
                  ></div>
                  <span 
                    className="score-value"
                    style={{ color: getCriticalityColor(asset.criticality_score) }}
                  >
                    {asset.criticality_score.toFixed(1)}
                  </span>
                </div>
                <span className={`level-badge ${getCriticalityLevel(asset.criticality_score)}`}>
                  {getCriticalityLevel(asset.criticality_score)}
                </span>
              </td>
              <td className="resilience">
                <div className="score-cell">
                  <div 
                    className="score-bar resilience-bar"
                    style={{ 
                      width: `${asset.resilience_score}%`,
                      backgroundColor: getResilienceColor(asset.resilience_score)
                    }}
                  ></div>
                  <span 
                    className="score-value"
                    style={{ color: getResilienceColor(asset.resilience_score) }}
                  >
                    {asset.resilience_score.toFixed(1)}
                  </span>
                </div>
              </td>
              <td className="spof">
                {asset.single_point_of_failure ? (
                  <span className="spof-badge" title="Single Point of Failure">
                    ⚠️
                  </span>
                ) : (
                  <span className="no-spof">—</span>
                )}
              </td>
              <td className="recommendation">
                {asset.top_recommendation ? (
                  <span className="rec-type">
                    {formatRecommendationType(asset.top_recommendation.recommendation_type)}
                  </span>
                ) : (
                  <span className="no-rec">—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


export default CriticalAssetTable;
