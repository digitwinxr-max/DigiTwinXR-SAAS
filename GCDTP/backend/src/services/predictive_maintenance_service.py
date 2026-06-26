"""
Predictive Maintenance Service

Deterministic failure probability prediction.
NO ML, NO neural networks, NO external AI.
Pure mathematical calculations only.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from ..models.maintenance_prediction import MaintenancePrediction, RiskLevel
from ..models.maintenance_history import MaintenanceHistory, MaintenanceType
from ..schemas.predictive_maintenance import (
    PredictionRequest,
    PredictionResponse,
    HealthProjection,
    HealthTimeline,
    RiskSummary,
    RiskDistribution,
    RecommendationResponse,
    RecommendationsListResponse,
    FactorBreakdown,
    DetailedPredictionResponse,
    HighRiskAsset,
    HighRiskAssetsResponse,
    PredictionHistoryItem,
    PredictionHistoryResponse,
    FailureProbabilityResponse
)


class PredictiveMaintenanceService:
    """
    Predictive Maintenance Service.
    
    Uses deterministic formula for failure probability:
    
    FP = 0.30 × health_degradation
       + 0.25 × active_events
       + 0.25 × measurement_anomalies
       + 0.20 × maintenance_age
    
    Risk Levels:
    - 0-25: LOW
    - 26-50: MEDIUM
    - 51-75: HIGH
    - 76-100: CRITICAL
    
    IMPORTANT:
    - NO ML/AI
    - NO neural networks
    - NO TensorFlow/PyTorch/sklearn
    - Deterministic scoring only
    """
    
    # Weights for failure probability formula
    WEIGHT_HEALTH_DEGRADATION = 0.30
    WEIGHT_ACTIVE_EVENTS = 0.25
    WEIGHT_MEASUREMENT_ANOMALIES = 0.25
    WEIGHT_MAINTENANCE_AGE = 0.20
    
    # Risk level thresholds
    RISK_THRESHOLDS = {
        RiskLevel.LOW: 25,
        RiskLevel.MEDIUM: 50,
        RiskLevel.HIGH: 75,
        RiskLevel.CRITICAL: 100
    }
    
    def __init__(self):
        # In-memory storage
        self._predictions: Dict[str, MaintenancePrediction] = {}
        self._history: Dict[str, MaintenanceHistory] = {}
        
        # Indexes
        self._predictions_by_asset: Dict[str, List[str]] = defaultdict(list)
        self._history_by_asset: Dict[str, List[str]] = defaultdict(list)
    
    def calculate_failure_probability(
        self,
        current_health: float,
        health_trend: float,
        active_events: int,
        measurement_anomalies: int,
        days_since_maintenance: int,
        data_quality_score: float = 0.8
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate failure probability using deterministic formula.
        
        Formula:
        FP = 0.30 × health_degradation
           + 0.25 × active_events
           + 0.25 × measurement_anomalies
           + 0.20 × maintenance_age
        
        Args:
            current_health: Current health score (0-100)
            health_trend: Health trend per day (-100 to +100)
            active_events: Number of active events
            measurement_anomalies: Number of measurement anomalies
            days_since_maintenance: Days since last maintenance
            data_quality_score: Data quality (0-1), affects confidence
            
        Returns:
            Tuple of (failure_probability, factor_breakdown)
        """
        # Calculate health degradation factor (0-100)
        # Higher degradation = higher failure probability
        health_degradation = max(0, min(100, (100 - current_health) + abs(health_trend) * 7))
        
        # Calculate active events factor (0-100)
        # More events = higher failure probability
        active_events_factor = min(100, active_events * 20)
        
        # Calculate measurement anomalies factor (0-100)
        # More anomalies = higher failure probability
        measurement_anomalies_factor = min(100, measurement_anomalies * 25)
        
        # Calculate maintenance age factor (0-100)
        # Older maintenance = higher failure probability
        maintenance_age_factor = min(100, days_since_maintenance * 0.5)
        
        # Calculate weighted failure probability
        failure_probability = (
            self.WEIGHT_HEALTH_DEGRADATION * health_degradation +
            self.WEIGHT_ACTIVE_EVENTS * active_events_factor +
            self.WEIGHT_MEASUREMENT_ANOMALIES * measurement_anomalies_factor +
            self.WEIGHT_MAINTENANCE_AGE * maintenance_age_factor
        )
        
        # Clamp to 0-100
        failure_probability = max(0, min(100, failure_probability))
        
        # Calculate confidence based on data quality
        confidence = data_quality_score * (1 - failure_probability / 200)
        
        # Factor breakdown
        factors = {
            "health_degradation": health_degradation,
            "active_events": active_events_factor,
            "measurement_anomalies": measurement_anomalies_factor,
            "maintenance_age": maintenance_age_factor
        }
        
        return failure_probability, confidence, factors
    
    def classify_risk(self, failure_probability: float) -> RiskLevel:
        """
        Classify risk level based on failure probability.
        
        Thresholds:
        - 0-25: LOW
        - 26-50: MEDIUM
        - 51-75: HIGH
        - 76-100: CRITICAL
        """
        if failure_probability <= 25:
            return RiskLevel.LOW
        elif failure_probability <= 50:
            return RiskLevel.MEDIUM
        elif failure_probability <= 75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def predict_health(
        self,
        current_health: float,
        health_trend: float,
        days_ahead: int
    ) -> float:
        """
        Predict health at future point.
        
        Args:
            current_health: Current health score (0-100)
            health_trend: Daily health trend (-100 to +100)
            days_ahead: Days to predict ahead
            
        Returns:
            Predicted health score
        """
        # Simple linear projection
        predicted_health = current_health + (health_trend * days_ahead)
        
        # Clamp to 0-100
        return max(0, min(100, predicted_health))
    
    def recommend_action(
        self,
        failure_probability: float,
        risk_level: RiskLevel,
        predicted_health: float,
        asset_type: str = "generic"
    ) -> str:
        """
        Recommend maintenance action based on prediction.
        
        Args:
            failure_probability: Calculated failure probability
            risk_level: Classified risk level
            predicted_health: Predicted health score
            asset_type: Type of asset
            
        Returns:
            Recommended action string
        """
        # Critical: Immediate action
        if risk_level == RiskLevel.CRITICAL or failure_probability > 75:
            return "Emergency inspection required - Schedule immediate maintenance"
        
        # High: Urgent action
        if risk_level == RiskLevel.HIGH or failure_probability > 50:
            if "transformer" in asset_type.lower():
                return "Inspect transformer oil - Schedule maintenance within 7 days"
            if "sensor" in asset_type.lower():
                return "Replace sensor - Schedule maintenance within 7 days"
            return "Schedule maintenance within 7 days - Increase monitoring frequency"
        
        # Medium: Planned action
        if risk_level == RiskLevel.MEDIUM or failure_probability > 25:
            if predicted_health < 70:
                return "Plan maintenance within 30 days - Monitor health trends"
            return "Continue monitoring - Plan routine maintenance"
        
        # Low: Regular monitoring
        return "Continue regular monitoring - No immediate action required"
    
    def run_prediction(
        self,
        asset_id: str,
        current_health: float = 100.0,
        health_trend: float = 0.0,
        active_events: int = 0,
        measurement_anomalies: int = 0,
        days_since_maintenance: int = 0,
        asset_type: str = "generic",
        data_quality_score: float = 0.8
    ) -> MaintenancePrediction:
        """
        Run complete prediction for an asset.
        
        Args:
            asset_id: Asset ID
            current_health: Current health score (0-100)
            health_trend: Daily health trend
            active_events: Number of active events
            measurement_anomalies: Number of anomalies
            days_since_maintenance: Days since last maintenance
            asset_type: Type of asset
            data_quality_score: Data quality (0-1)
            
        Returns:
            MaintenancePrediction object
        """
        # Calculate failure probability
        failure_probability, confidence, factors = self.calculate_failure_probability(
            current_health=current_health,
            health_trend=health_trend,
            active_events=active_events,
            measurement_anomalies=measurement_anomalies,
            days_since_maintenance=days_since_maintenance,
            data_quality_score=data_quality_score
        )
        
        # Classify risk
        risk_level = self.classify_risk(failure_probability)
        
        # Predict health at 90 days
        predicted_health = self.predict_health(current_health, health_trend, 90)
        
        # Generate recommendation
        recommended_action = self.recommend_action(
            failure_probability=failure_probability,
            risk_level=risk_level,
            predicted_health=predicted_health,
            asset_type=asset_type
        )
        
        # Create prediction object
        prediction = MaintenancePrediction(
            asset_id=asset_id,
            prediction_date=datetime.utcnow(),
            failure_probability=failure_probability,
            predicted_health=predicted_health,
            risk_level=risk_level,
            recommended_action=recommended_action,
            confidence=confidence,
            health_degradation_factor=factors["health_degradation"],
            active_events_factor=factors["active_events"],
            measurement_anomalies_factor=factors["measurement_anomalies"],
            maintenance_age_factor=factors["maintenance_age"]
        )
        
        # Store prediction
        self._predictions[prediction.id] = prediction
        self._predictions_by_asset[asset_id].append(prediction.id)
        
        return prediction
    
    def get_prediction(self, asset_id: str) -> Optional[MaintenancePrediction]:
        """Get latest prediction for an asset."""
        prediction_ids = self._predictions_by_asset.get(asset_id, [])
        if not prediction_ids:
            return None
        
        # Return most recent
        latest_id = prediction_ids[-1]
        return self._predictions.get(latest_id)
    
    def get_prediction_history(self, asset_id: str) -> List[MaintenancePrediction]:
        """Get all predictions for an asset."""
        prediction_ids = self._predictions_by_asset.get(asset_id, [])
        return [
            self._predictions[pid]
            for pid in prediction_ids
            if pid in self._predictions
        ]
    
    def get_high_risk_assets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get high-risk assets (HIGH or CRITICAL risk)."""
        high_risk = []
        
        for asset_id in self._predictions_by_asset:
            prediction = self.get_prediction(asset_id)
            if prediction and prediction.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                high_risk.append({
                    "asset_id": asset_id,
                    "failure_probability": prediction.failure_probability,
                    "predicted_health": prediction.predicted_health,
                    "risk_level": prediction.risk_level.value,
                    "recommended_action": prediction.recommended_action,
                    "prediction_date": prediction.prediction_date
                })
        
        # Sort by failure probability descending
        high_risk.sort(key=lambda x: x["failure_probability"], reverse=True)
        
        return high_risk[:limit]
    
    def get_recommendations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get maintenance recommendations for all assets."""
        recommendations = []
        
        for asset_id in self._predictions_by_asset:
            prediction = self.get_prediction(asset_id)
            if prediction and prediction.recommended_action:
                recommendations.append({
                    "asset_id": asset_id,
                    "recommendation": prediction.recommended_action,
                    "priority": prediction.risk_level.value,
                    "reason": f"Failure probability: {prediction.failure_probability:.1f}%"
                })
        
        # Sort by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        return recommendations[:limit]
    
    def get_health_timeline(
        self,
        current_health: float,
        health_trend: float
    ) -> HealthTimeline:
        """Get health timeline with projections."""
        projections = [
            HealthProjection(
                timeframe="7 days",
                predicted_health=self.predict_health(current_health, health_trend, 7),
                projected_probability=self._calculate_projected_probability(
                    current_health, health_trend, 7
                ),
                risk_trend="degrading" if health_trend < 0 else ("stable" if health_trend == 0 else "improving")
            ),
            HealthProjection(
                timeframe="30 days",
                predicted_health=self.predict_health(current_health, health_trend, 30),
                projected_probability=self._calculate_projected_probability(
                    current_health, health_trend, 30
                ),
                risk_trend="degrading" if health_trend < -1 else ("stable" if abs(health_trend) <= 1 else "improving")
            ),
            HealthProjection(
                timeframe="90 days",
                predicted_health=self.predict_health(current_health, health_trend, 90),
                projected_probability=self._calculate_projected_probability(
                    current_health, health_trend, 90
                ),
                risk_trend="degrading" if health_trend < -0.5 else ("stable" if abs(health_trend) <= 0.5 else "improving")
            )
        ]
        
        return HealthTimeline(
            current_health=current_health,
            current_probability=100 - current_health,
            projections=projections,
            degradation_rate=health_trend
        )
    
    def _calculate_projected_probability(
        self,
        current_health: float,
        health_trend: float,
        days_ahead: int
    ) -> float:
        """Calculate projected failure probability."""
        projected_health = self.predict_health(current_health, health_trend, days_ahead)
        return max(0, min(100, 100 - projected_health + abs(health_trend) * days_ahead * 0.1))


# Global instance
predictive_maintenance_service = PredictiveMaintenanceService()
