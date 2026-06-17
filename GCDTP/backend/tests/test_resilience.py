"""
Tests for Resilience Analysis Engine

Tests criticality calculations, resilience scoring,
single point of failure detection, and recommendations.
"""

import pytest
from unittest.mock import MagicMock, patch
import uuid

from backend.src.services.resilience_service import (
    ResilienceService,
    UPSTREAM_WEIGHT,
    DOWNSTREAM_WEIGHT,
    DEPENDENCY_WEIGHT,
    ACTIVE_EVENT_WEIGHT,
    DEPENDENCY_PENALTY_WEIGHT,
    FAILURE_PROPAGATION_PENALTY_WEIGHT,
    ACTIVE_EVENT_PENALTY_WEIGHT,
    MAX_SCORE,
    MIN_SCORE,
)


class TestCriticalityCalculations:
    """Tests for criticality score calculations."""
    
    def test_criticality_zero_inputs(self):
        """Test criticality with all zero inputs."""
        service = MagicMock()
        result = ResilienceService.calculate_criticality_score(
            service,
            upstream_count=0,
            downstream_count=0,
            dependency_count=0,
            active_events=0,
        )
        assert result == 0.0
    
    def test_criticality_with_upstream(self):
        """Test criticality increases with upstream dependencies."""
        service = MagicMock()
        
        # Single upstream
        score_single = ResilienceService.calculate_criticality_score(
            service,
            upstream_count=1,
            downstream_count=0,
            dependency_count=0,
            active_events=0,
        )
        
        # Multiple upstream
        score_multiple = ResilienceService.calculate_criticality_score(
            service,
            upstream_count=5,
            downstream_count=0,
            dependency_count=0,
            active_events=0,
        )
        
        assert score_multiple > score_single
    
    def test_criticality_with_downstream(self):
        """Test criticality increases with downstream dependents."""
        service = MagicMock()
        
        # Single downstream
        score_single = ResilienceService.calculate_criticality_score(
            service,
            upstream_count=0,
            downstream_count=1,
            dependency_count=0,
            active_events=0,
        )
        
        # Multiple downstream
        score_multiple = ResilienceService.calculate_criticality_score(
            service,
            upstream_count=0,
            downstream_count=5,
            dependency_count=0,
            active_events=0,
        )
        
        assert score_multiple > score_single
    
    def test_criticality_with_dependencies(self):
        """Test criticality increases with dependencies."""
        service = MagicMock()
        
        # Single dependency
        score_single = ResilienceService.calculate_criticality_score(
            service,
            upstream_count=0,
            downstream_count=0,
            dependency_count=1,
            active_events=0,
        )
        
        # Multiple dependencies
        score_multiple = ResilienceService.calculate_criticality_score(
            service,
            upstream_count=0,
            downstream_count=0,
            dependency_count=10,
            active_events=0,
        )
        
        assert score_multiple > score_single
    
    def test_criticality_with_active_events(self):
        """Test criticality increases with active events."""
        service = MagicMock()
        
        # No events
        score_no_events = ResilienceService.calculate_criticality_score(
            service,
            upstream_count=0,
            downstream_count=0,
            dependency_count=0,
            active_events=0,
        )
        
        # With events
        score_with_events = ResilienceService.calculate_criticality_score(
            service,
            upstream_count=0,
            downstream_count=0,
            dependency_count=0,
            active_events=3,
        )
        
        assert score_with_events > score_no_events
    
    def test_criticality_formula_weights(self):
        """Test that formula weights are applied correctly."""
        service = MagicMock()
        
        # Equal counts should weight downstream more heavily
        score_downstream = ResilienceService.calculate_criticality_score(
            service,
            upstream_count=5,
            downstream_count=0,
            dependency_count=0,
            active_events=0,
        )
        
        score_upstream = ResilienceService.calculate_criticality_score(
            service,
            upstream_count=0,
            downstream_count=5,
            dependency_count=0,
            active_events=0,
        )
        
        # Downstream should have higher weight
        assert score_upstream > score_downstream
    
    def test_criticality_score_clamping(self):
        """Test that criticality score is clamped to 0-100."""
        service = MagicMock()
        
        # Very high values should be clamped
        score = ResilienceService.calculate_criticality_score(
            service,
            upstream_count=100,
            downstream_count=100,
            dependency_count=100,
            active_events=100,
        )
        
        assert MIN_SCORE <= score <= MAX_SCORE


class TestResilienceCalculations:
    """Tests for resilience score calculations."""
    
    def test_resilience_high_with_no_issues(self):
        """Test high resilience with no risk factors."""
        service = MagicMock()
        
        result = ResilienceService.calculate_resilience_score(
            service,
            asset_id=uuid.uuid4(),
            dependency_count=0,
            is_spof=False,
            active_events=0,
        )
        
        assert result == MAX_SCORE
    
    def test_resilience_reduced_by_spof(self):
        """Test that SPOF reduces resilience score."""
        service = MagicMock()
        
        # Not SPOF
        score_not_spof = ResilienceService.calculate_resilience_score(
            service,
            asset_id=uuid.uuid4(),
            dependency_count=0,
            is_spof=False,
            active_events=0,
        )
        
        # Is SPOF
        score_spof = ResilienceService.calculate_resilience_score(
            service,
            asset_id=uuid.uuid4(),
            dependency_count=0,
            is_spof=True,
            active_events=0,
        )
        
        assert score_spof < score_not_spof
    
    def test_resilience_reduced_by_dependencies(self):
        """Test that high dependency count reduces resilience."""
        service = MagicMock()
        
        # Low dependencies
        score_low = ResilienceService.calculate_resilience_score(
            service,
            asset_id=uuid.uuid4(),
            dependency_count=2,
            is_spof=False,
            active_events=0,
        )
        
        # High dependencies
        score_high = ResilienceService.calculate_resilience_score(
            service,
            asset_id=uuid.uuid4(),
            dependency_count=15,
            is_spof=False,
            active_events=0,
        )
        
        assert score_high < score_low
    
    def test_resilience_reduced_by_active_events(self):
        """Test that active events reduce resilience."""
        service = MagicMock()
        
        # No events
        score_no_events = ResilienceService.calculate_resilience_score(
            service,
            asset_id=uuid.uuid4(),
            dependency_count=0,
            is_spof=False,
            active_events=0,
        )
        
        # With events
        score_with_events = ResilienceService.calculate_resilience_score(
            service,
            asset_id=uuid.uuid4(),
            dependency_count=0,
            is_spof=False,
            active_events=3,
        )
        
        assert score_with_events < score_no_events
    
    def test_resilience_combined_penalties(self):
        """Test that multiple penalties stack correctly."""
        service = MagicMock()
        
        # All penalties
        score_all = ResilienceService.calculate_resilience_score(
            service,
            asset_id=uuid.uuid4(),
            dependency_count=20,
            is_spof=True,
            active_events=5,
        )
        
        # Only one penalty
        score_one = ResilienceService.calculate_resilience_score(
            service,
            asset_id=uuid.uuid4(),
            dependency_count=0,
            is_spof=False,
            active_events=0,
        )
        
        assert score_all < score_one
    
    def test_resilience_score_clamping(self):
        """Test that resilience score is clamped to 0-100."""
        service = MagicMock()
        
        # Extreme values
        score = ResilienceService.calculate_resilience_score(
            service,
            asset_id=uuid.uuid4(),
            dependency_count=100,
            is_spof=True,
            active_events=100,
        )
        
        assert MIN_SCORE <= score <= MAX_SCORE


class TestSinglePointOfFailure:
    """Tests for SPOF detection."""
    
    def test_spof_no_downstream(self):
        """Test that asset with no downstream is not SPOF."""
        service = MagicMock()
        service._get_all_downstream = MagicMock(return_value=[])
        
        result = ResilienceService.detect_single_point_of_failure(
            service,
            asset_id=uuid.uuid4(),
        )
        
        assert result is False
    
    def test_spof_single_downstream(self):
        """Test that asset with single downstream is not SPOF."""
        service = MagicMock()
        service._get_all_downstream = MagicMock(return_value=[uuid.uuid4()])
        service.db.query.return_value.filter.return_value.all.return_value = []
        
        result = ResilienceService.detect_single_point_of_failure(
            service,
            asset_id=uuid.uuid4(),
        )
        
        assert result is False


class TestRecommendations:
    """Tests for recommendation generation."""
    
    def test_recommendations_for_spof(self):
        """Test that SPOF assets get critical recommendations."""
        service = MagicMock()
        
        # Create mock analysis
        analysis = MagicMock()
        analysis.id = uuid.uuid4()
        analysis.criticality_score = 80
        analysis.resilience_score = 30
        analysis.single_point_of_failure = True
        
        # Create mock asset
        asset = MagicMock()
        asset.name = "Test Asset"
        asset.id = uuid.uuid4()
        
        recommendations = ResilienceService.generate_recommendations(
            service,
            analysis=analysis,
            asset=asset,
            upstream_count=2,
            downstream_count=3,
            is_spof=True,
        )
        
        # Should have redundancy recommendation for SPOF
        rec_types = [r.recommendation_type for r in recommendations]
        assert 'redundancy' in rec_types
        assert 'failover' in rec_types
        
        # SPOF should be CRITICAL priority
        spof_rec = next(r for r in recommendations if r.recommendation_type == 'redundancy')
        assert spof_rec.priority == 'CRITICAL'
    
    def test_recommendations_for_high_criticality(self):
        """Test that high criticality assets get monitoring recommendations."""
        service = MagicMock()
        
        analysis = MagicMock()
        analysis.id = uuid.uuid4()
        analysis.criticality_score = 75
        analysis.resilience_score = 60
        analysis.single_point_of_failure = False
        
        asset = MagicMock()
        asset.name = "Critical Asset"
        asset.id = uuid.uuid4()
        
        recommendations = ResilienceService.generate_recommendations(
            service,
            analysis=analysis,
            asset=asset,
            upstream_count=2,
            downstream_count=2,
            is_spof=False,
        )
        
        rec_types = [r.recommendation_type for r in recommendations]
        assert 'monitoring' in rec_types
        assert 'early_warning' in rec_types
    
    def test_recommendations_for_low_resilience(self):
        """Test that low resilience assets get maintenance recommendations."""
        service = MagicMock()
        
        analysis = MagicMock()
        analysis.id = uuid.uuid4()
        analysis.criticality_score = 50
        analysis.resilience_score = 30
        analysis.single_point_of_failure = False
        
        asset = MagicMock()
        asset.name = "Low Resilient Asset"
        asset.id = uuid.uuid4()
        
        recommendations = ResilienceService.generate_recommendations(
            service,
            analysis=analysis,
            asset=asset,
            upstream_count=1,
            downstream_count=1,
            is_spof=False,
        )
        
        rec_types = [r.recommendation_type for r in recommendations]
        assert 'maintenance' in rec_types
        assert 'backup' in rec_types
    
    def test_recommendations_for_high_upstream(self):
        """Test that high upstream count gets diversification recommendation."""
        service = MagicMock()
        
        analysis = MagicMock()
        analysis.id = uuid.uuid4()
        analysis.criticality_score = 50
        analysis.resilience_score = 70
        analysis.single_point_of_failure = False
        
        asset = MagicMock()
        asset.name = "Diversified Asset"
        asset.id = uuid.uuid4()
        
        recommendations = ResilienceService.generate_recommendations(
            service,
            analysis=analysis,
            asset=asset,
            upstream_count=8,  # > 5
            downstream_count=1,
            is_spof=False,
        )
        
        rec_types = [r.recommendation_type for r in recommendations]
        assert 'diversification' in rec_types
    
    def test_no_recommendations_for_healthy_asset(self):
        """Test that healthy assets get minimal or no recommendations."""
        service = MagicMock()
        
        analysis = MagicMock()
        analysis.id = uuid.uuid4()
        analysis.criticality_score = 20  # Low
        analysis.resilience_score = 90  # High
        analysis.single_point_of_failure = False
        
        asset = MagicMock()
        asset.name = "Healthy Asset"
        asset.id = uuid.uuid4()
        
        recommendations = ResilienceService.generate_recommendations(
            service,
            analysis=analysis,
            asset=asset,
            upstream_count=1,
            downstream_count=1,
            is_spof=False,
        )
        
        # Should have few or no recommendations
        assert len(recommendations) <= 2


class TestScoreClamping:
    """Tests for score clamping utility."""
    
    def test_clamp_below_min(self):
        """Test clamping value below minimum."""
        service = MagicMock()
        result = ResilienceService._clamp_score(service, -50)
        assert result == MIN_SCORE
    
    def test_clamp_above_max(self):
        """Test clamping value above maximum."""
        service = MagicMock()
        result = ResilienceService._clamp_score(service, 150)
        assert result == MAX_SCORE
    
    def test_clamp_within_range(self):
        """Test clamping value within range."""
        service = MagicMock()
        result = ResilienceService._clamp_score(service, 50)
        assert result == 50
    
    def test_clamp_at_boundaries(self):
        """Test clamping at exact boundaries."""
        service = MagicMock()
        
        assert ResilienceService._clamp_score(service, 0) == 0
        assert ResilienceService._clamp_score(service, 100) == 100


class TestConstants:
    """Tests for service constants."""
    
    def test_weight_constants(self):
        """Test that weight constants sum appropriately."""
        # Criticality weights
        criticality_weights = UPSTREAM_WEIGHT + DOWNSTREAM_WEIGHT + DEPENDENCY_WEIGHT + ACTIVE_EVENT_WEIGHT
        assert criticality_weights <= 1.0  # Should not exceed 1
        
        # Resilience weights (penalties)
        resilience_weights = DEPENDENCY_PENALTY_WEIGHT + FAILURE_PROPAGATION_PENALTY_WEIGHT + ACTIVE_EVENT_PENALTY_WEIGHT
        assert resilience_weights <= 1.0  # Should not exceed 1
    
    def test_score_bounds(self):
        """Test that score bounds are valid."""
        assert MIN_SCORE == 0.0
        assert MAX_SCORE == 100.0
        assert MIN_SCORE < MAX_SCORE
