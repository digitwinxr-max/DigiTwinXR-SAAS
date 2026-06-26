"""
Resilience Analysis Service

Core service for resilience analysis engine.
This service performs analysis only - it never modifies operational state.

Analysis Components:
- Criticality scoring based on dependency graph
- Resilience scoring based on failure propagation
- Single point of failure detection
- Recommendation generation
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import uuid

from ..models import (
    Asset,
    AssetHealth,
    AssetRelationship,
    AssetHealthDependency,
    Event,
    ResilienceAnalysis,
    ResilienceRecommendation,
)
from ..schemas.resilience import (
    RecommendationPriority,
    RecommendationType,
    get_criticality_level,
    get_resilience_level,
)


# ============================================================================
# Constants
# ============================================================================

# Criticality formula weights
UPSTREAM_WEIGHT = 0.3
DOWNSTREAM_WEIGHT = 0.4
DEPENDENCY_WEIGHT = 0.2
ACTIVE_EVENT_WEIGHT = 0.1

# Resilience penalty weights
DEPENDENCY_PENALTY_WEIGHT = 0.4
FAILURE_PROPAGATION_PENALTY_WEIGHT = 0.35
ACTIVE_EVENT_PENALTY_WEIGHT = 0.25

# Single point of failure threshold
SPOF_BRANCH_THRESHOLD = 1

# Score bounds
MIN_SCORE = 0.0
MAX_SCORE = 100.0


# ============================================================================
# Service Class
# ============================================================================

class ResilienceService:
    """
    Service for performing resilience analysis.
    
    This service is read-only with respect to operational systems.
    It only reads from: assets, asset_relationships, asset_health_dependencies, events.
    It only writes to: resilience_analyses, resilience_recommendations.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================================================================
    # Core Analysis Methods
    # =========================================================================
    
    def analyze_asset(
        self,
        asset_id: uuid.UUID,
        force_refresh: bool = False
    ) -> Optional[ResilienceAnalysis]:
        """
        Perform comprehensive resilience analysis for a single asset.
        
        Args:
            asset_id: UUID of the asset to analyze
            force_refresh: If True, re-analyze even if recent analysis exists
            
        Returns:
            ResilienceAnalysis object or None if asset not found
        """
        # Verify asset exists
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return None
        
        # Check for existing analysis (unless force refresh)
        if not force_refresh:
            existing = self._get_recent_analysis(asset_id)
            if existing:
                return existing
        
        # Calculate metrics
        upstream_count = self.get_upstream_count(asset_id)
        downstream_count = self.get_downstream_count(asset_id)
        dependency_count = self._get_dependency_count(asset_id)
        active_events = self._get_active_event_count(asset_id)
        is_spof = self.detect_single_point_of_failure(asset_id)
        
        # Calculate scores
        criticality_score = self.calculate_criticality_score(
            upstream_count=upstream_count,
            downstream_count=downstream_count,
            dependency_count=dependency_count,
            active_events=active_events,
        )
        
        resilience_score = self.calculate_resilience_score(
            asset_id=asset_id,
            dependency_count=dependency_count,
            is_spof=is_spof,
            active_events=active_events,
        )
        
        # Create or update analysis
        analysis = ResilienceAnalysis(
            id=uuid.uuid4(),
            asset_id=asset_id,
            criticality_score=criticality_score,
            resilience_score=resilience_score,
            dependency_count=dependency_count,
            upstream_count=upstream_count,
            downstream_count=downstream_count,
            single_point_of_failure=is_spof,
            created_at=datetime.utcnow(),
        )
        
        self.db.add(analysis)
        self.db.flush()  # Get the ID
        
        # Generate recommendations
        recommendations = self.generate_recommendations(
            analysis=analysis,
            asset=asset,
            upstream_count=upstream_count,
            downstream_count=downstream_count,
            is_spof=is_spof,
        )
        
        for rec in recommendations:
            self.db.add(rec)
        
        self.db.commit()
        self.db.refresh(analysis)
        
        return analysis
    
    def analyze_network(self, force_refresh: bool = False) -> List[ResilienceAnalysis]:
        """
        Perform resilience analysis for all assets in the network.
        
        Args:
            force_refresh: If True, re-analyze all assets
            
        Returns:
            List of ResilienceAnalysis objects
        """
        assets = self.db.query(Asset).all()
        analyses = []
        
        for asset in assets:
            analysis = self.analyze_asset(
                asset_id=asset.id,
                force_refresh=force_refresh,
            )
            if analysis:
                analyses.append(analysis)
        
        return analyses
    
    # =========================================================================
    # Scoring Methods
    # =========================================================================
    
    def calculate_criticality_score(
        self,
        upstream_count: int,
        downstream_count: int,
        dependency_count: int,
        active_events: int,
    ) -> float:
        """
        Calculate criticality score using weighted formula.
        
        Formula:
            criticality = (upstream × 0.3) + (downstream × 0.4) + 
                         (dependency × 0.2) + (active_events × 0.1)
        
        Args:
            upstream_count: Number of upstream dependencies
            downstream_count: Number of downstream dependents
            dependency_count: Total direct dependencies
            active_events: Number of active events affecting asset
            
        Returns:
            Criticality score normalized to 0-100
        """
        # Calculate raw score
        raw_score = (
            (upstream_count * UPSTREAM_WEIGHT) +
            (downstream_count * DOWNSTREAM_WEIGHT) +
            (dependency_count * DEPENDENCY_WEIGHT) +
            (active_events * ACTIVE_EVENT_WEIGHT * 10)  # Scale events
        )
        
        # Normalize (assuming max reasonable values)
        # Typical max: 10 upstream, 10 downstream, 20 dependencies, 5 events
        max_expected = 10 * UPSTREAM_WEIGHT + 10 * DOWNSTREAM_WEIGHT + 20 * DEPENDENCY_WEIGHT + 5 * ACTIVE_EVENT_WEIGHT * 10
        normalized = (raw_score / max_expected) * 100 if max_expected > 0 else 0
        
        return self._clamp_score(normalized)
    
    def calculate_resilience_score(
        self,
        asset_id: uuid.UUID,
        dependency_count: int,
        is_spof: bool,
        active_events: int,
    ) -> float:
        """
        Calculate resilience score.
        
        Formula:
            resilience = 100 - dependency_penalty - propagation_penalty - event_penalty
        
        Args:
            asset_id: UUID of the asset
            dependency_count: Number of dependencies
            is_spof: Whether asset is a single point of failure
            active_events: Number of active events
            
        Returns:
            Resilience score (0-100)
        """
        # Calculate penalties
        # Dependency penalty: more dependencies = harder to maintain
        max_dependencies = 20
        dependency_penalty = min((dependency_count / max_dependencies) * 100 * DEPENDENCY_PENALTY_WEIGHT, 40)
        
        # Propagation penalty: being SPOF means failures spread easily
        propagation_penalty = 50 if is_spof else 0
        
        # Event penalty: active events reduce resilience
        max_events = 5
        event_penalty = min((active_events / max_events) * 100 * ACTIVE_EVENT_PENALTY_WEIGHT, 25)
        
        # Calculate final score
        resilience = MAX_SCORE - dependency_penalty - propagation_penalty - event_penalty
        
        return self._clamp_score(resilience)
    
    def detect_single_point_of_failure(self, asset_id: uuid.UUID) -> bool:
        """
        Detect if an asset is a single point of failure.
        
        An asset is a SPOF if removing it would disconnect more than
        one downstream branch in the dependency graph.
        
        Algorithm:
            1. Get all downstream assets
            2. Find unique paths from each downstream to the root
            3. Count paths that go through this asset
            4. If > 1 path goes through this asset, it's a SPOF
        
        Args:
            asset_id: UUID of the asset to check
            
        Returns:
            True if asset is a single point of failure
        """
        # Get all downstream relationships
        downstream = self._get_all_downstream(asset_id)
        
        if len(downstream) <= 1:
            # Can't be SPOF if 0 or 1 downstream asset
            return False
        
        # Get the immediate downstream assets
        immediate_downstream = self.db.query(AssetRelationship).filter(
            AssetRelationship.source_asset_id == asset_id
        ).all()
        
        if len(immediate_downstream) == 0:
            return False
        
        # Count how many distinct downstream branches there are
        # A branch is a path from the asset to a leaf node
        branches_through_asset = 0
        
        for ds in immediate_downstream:
            # Check if this downstream asset has other upstream paths
            other_upstreams = self.db.query(AssetRelationship).filter(
                AssetRelationship.target_asset_id == ds.target_asset_id,
                AssetRelationship.source_asset_id != asset_id
            ).count()
            
            if other_upstreams == 0:
                # This downstream has no other upstream = unique branch
                branches_through_asset += 1
        
        # SPOF if multiple branches go through this asset with no alternatives
        return branches_through_asset > SPOF_BRANCH_THRESHOLD
    
    def get_upstream_count(self, asset_id: uuid.UUID) -> int:
        """
        Get count of upstream dependencies.
        
        Upstream = what this asset depends on.
        
        Args:
            asset_id: UUID of the asset
            
        Returns:
            Number of assets this asset depends on
        """
        return self.db.query(AssetRelationship).filter(
            AssetRelationship.target_asset_id == asset_id
        ).count()
    
    def get_downstream_count(self, asset_id: uuid.UUID) -> int:
        """
        Get count of downstream dependents.
        
        Downstream = what depends on this asset.
        
        Args:
            asset_id: UUID of the asset
            
        Returns:
            Number of assets that depend on this asset
        """
        return self._get_all_downstream_count(asset_id)
    
    # =========================================================================
    # Recommendation Methods
    # =========================================================================
    
    def generate_recommendations(
        self,
        analysis: ResilienceAnalysis,
        asset: Asset,
        upstream_count: int,
        downstream_count: int,
        is_spof: bool,
    ) -> List[ResilienceRecommendation]:
        """
        Generate resilience recommendations for an asset.
        
        Args:
            analysis: The resilience analysis object
            asset: The asset being analyzed
            upstream_count: Number of upstream dependencies
            downstream_count: Number of downstream dependents
            is_spof: Whether asset is a single point of failure
            
        Returns:
            List of ResilienceRecommendation objects
        """
        recommendations = []
        
        # SPOF recommendations (highest priority)
        if is_spof:
            recommendations.append(ResilienceRecommendation(
                id=uuid.uuid4(),
                analysis_id=analysis.id,
                recommendation_type=RecommendationType.REDUNDANCY.value,
                priority=RecommendationPriority.CRITICAL.value,
                description=f"CRITICAL: {asset.name} is a single point of failure. Implement redundancy or alternative pathways immediately.",
            ))
            recommendations.append(ResilienceRecommendation(
                id=uuid.uuid4(),
                analysis_id=analysis.id,
                recommendation_type=RecommendationType.FAILOVER.value,
                priority=RecommendationPriority.HIGH.value,
                description=f"Implement automatic failover for {asset.name} to reduce impact of failures.",
            ))
        
        # High criticality recommendations
        if analysis.criticality_score >= 70:
            recommendations.append(ResilienceRecommendation(
                id=uuid.uuid4(),
                analysis_id=analysis.id,
                recommendation_type=RecommendationType.MONITORING.value,
                priority=RecommendationPriority.HIGH.value,
                description=f"Increase monitoring frequency for critical asset {asset.name}.",
            ))
            recommendations.append(ResilienceRecommendation(
                id=uuid.uuid4(),
                analysis_id=analysis.id,
                recommendation_type=RecommendationType.EARLY_WARNING.value,
                priority=RecommendationPriority.MEDIUM.value,
                description=f"Set up early warning alerts for {asset.name} health degradation.",
            ))
        
        # Low resilience recommendations
        if analysis.resilience_score < 40:
            recommendations.append(ResilienceRecommendation(
                id=uuid.uuid4(),
                analysis_id=analysis.id,
                recommendation_type=RecommendationType.MAINTENANCE.value,
                priority=RecommendationPriority.HIGH.value,
                description=f"Schedule preventive maintenance for {asset.name} to improve resilience.",
            ))
            recommendations.append(ResilienceRecommendation(
                id=uuid.uuid4(),
                analysis_id=analysis.id,
                recommendation_type=RecommendationType.BACKUP.value,
                priority=RecommendationPriority.MEDIUM.value,
                description=f"Ensure backup systems are in place for {asset.name}.",
            ))
        
        # High dependency recommendations
        if upstream_count > 5:
            recommendations.append(ResilienceRecommendation(
                id=uuid.uuid4(),
                analysis_id=analysis.id,
                recommendation_type=RecommendationType.DIVERSIFICATION.value,
                priority=RecommendationPriority.MEDIUM.value,
                description=f"Reduce dependency on {upstream_count} upstream assets by diversifying suppliers or pathways.",
            ))
        
        if downstream_count > 5:
            recommendations.append(ResilienceRecommendation(
                id=uuid.uuid4(),
                analysis_id=analysis.id,
                recommendation_type=RecommendationType.RECONFIGURATION.value,
                priority=RecommendationPriority.LOW.value,
                description=f"Consider load balancing across {downstream_count} downstream dependents.",
            ))
        
        # Low resilience due to dependencies
        if analysis.resilience_score < 60 and upstream_count < 3:
            recommendations.append(ResilienceRecommendation(
                id=uuid.uuid4(),
                analysis_id=analysis.id,
                recommendation_type=RecommendationType.REDUNDANCY.value,
                priority=RecommendationPriority.MEDIUM.value,
                description=f"Increase resilience by adding backup dependencies for {asset.name}.",
            ))
        
        return recommendations
    
    # =========================================================================
    # Query Methods
    # =========================================================================
    
    def get_network_resilience(self) -> Dict:
        """
        Get overall network resilience metrics.
        
        Returns:
            Dictionary with network-wide resilience statistics
        """
        analyses = self.db.query(ResilienceAnalysis).all()
        
        if not analyses:
            return {
                "total_assets": 0,
                "analyzed_assets": 0,
                "avg_criticality": 0,
                "avg_resilience": 0,
                "single_points_of_failure": 0,
            }
        
        total = self.db.query(Asset).count()
        
        avg_criticality = sum(a.criticality_score for a in analyses) / len(analyses)
        avg_resilience = sum(a.resilience_score for a in analyses) / len(analyses)
        spof_count = sum(1 for a in analyses if a.single_point_of_failure)
        
        high_critical = sum(1 for a in analyses if a.criticality_score >= 70)
        medium_critical = sum(1 for a in analyses if 40 <= a.criticality_score < 70)
        low_critical = sum(1 for a in analyses if a.criticality_score < 40)
        
        return {
            "total_assets": total,
            "analyzed_assets": len(analyses),
            "avg_criticality": round(avg_criticality, 2),
            "avg_resilience": round(avg_resilience, 2),
            "single_points_of_failure": spof_count,
            "high_criticality_count": high_critical,
            "medium_criticality_count": medium_critical,
            "low_criticality_count": low_critical,
        }
    
    def get_top_critical_assets(self, limit: int = 10) -> List[Dict]:
        """
        Get the most critical assets in the network.
        
        Args:
            limit: Maximum number of assets to return
            
        Returns:
            List of dictionaries with asset and analysis data
        """
        analyses = (
            self.db.query(ResilienceAnalysis, Asset)
            .join(Asset, ResilienceAnalysis.asset_id == Asset.id)
            .order_by(ResilienceAnalysis.criticality_score.desc())
            .limit(limit)
            .all()
        )
        
        results = []
        for analysis, asset in analyses:
            # Get top recommendation
            top_rec = (
                self.db.query(ResilienceRecommendation)
                .filter(ResilienceRecommendation.analysis_id == analysis.id)
                .order_by(
                    ResilienceRecommendation.priority.desc(),
                    ResilienceRecommendation.recommendation_type
                )
                .first()
            )
            
            results.append({
                "asset_id": str(asset.id),
                "asset_name": asset.name,
                "asset_type": asset.asset_type,
                "criticality_score": analysis.criticality_score,
                "resilience_score": analysis.resilience_score,
                "single_point_of_failure": analysis.single_point_of_failure,
                "dependency_count": analysis.dependency_count,
                "upstream_count": analysis.upstream_count,
                "downstream_count": analysis.downstream_count,
                "top_recommendation": top_rec.to_dict() if top_rec else None,
            })
        
        return results
    
    # =========================================================================
    # Private Helper Methods
    # =========================================================================
    
    def _get_recent_analysis(self, asset_id: uuid.UUID) -> Optional[ResilienceAnalysis]:
        """Get most recent analysis for an asset (if within last hour)."""
        one_hour_ago = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        
        return self.db.query(ResilienceAnalysis).filter(
            and_(
                ResilienceAnalysis.asset_id == asset_id,
                ResilienceAnalysis.created_at >= one_hour_ago
            )
        ).first()
    
    def _get_dependency_count(self, asset_id: uuid.UUID) -> int:
        """Get total dependency count (upstream + downstream)."""
        upstream = self.get_upstream_count(asset_id)
        downstream = self.get_downstream_count(asset_id)
        return upstream + downstream
    
    def _get_active_event_count(self, asset_id: uuid.UUID) -> int:
        """Get count of active events affecting an asset."""
        return self.db.query(Event).filter(
            and_(
                Event.asset_id == asset_id,
                Event.resolved == False
            )
        ).count()
    
    def _get_all_downstream(self, asset_id: uuid.UUID) -> List[uuid.UUID]:
        """Get all downstream asset IDs using BFS."""
        visited = set()
        queue = [asset_id]
        downstream = []
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Get direct downstream
            relationships = self.db.query(AssetRelationship).filter(
                AssetRelationship.source_asset_id == current
            ).all()
            
            for rel in relationships:
                if rel.target_asset_id not in visited:
                    downstream.append(rel.target_asset_id)
                    queue.append(rel.target_asset_id)
        
        return downstream
    
    def _get_all_downstream_count(self, asset_id: uuid.UUID) -> int:
        """Get count of all downstream assets."""
        return len(self._get_all_downstream(asset_id))
    
    def _clamp_score(self, score: float) -> float:
        """Clamp score to valid range."""
        return max(MIN_SCORE, min(MAX_SCORE, score))
