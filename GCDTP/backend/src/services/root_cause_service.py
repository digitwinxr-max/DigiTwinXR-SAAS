"""
Root Cause Analysis Service

READ ONLY engine - explains WHY failures occurred.
NO ML, NO LLM, NO external APIs, NO automation.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from ..models.root_cause_analysis import RootCauseAnalysis, AnalysisType
from ..models.cause_factor import CauseFactor, FactorType
from ..models.cause_chain import CauseChain
from ..schemas.root_cause import (
    RootCauseResponse,
    CauseFactorSchema,
    CauseChainSchema,
    FactorResponse,
    RankedFactorResponse,
    CauseChainResponse,
    ConfidenceResponse,
    AssetCauseSummary,
    HighConfidenceAnalysis,
    AnalysisResponse
)


class RootCauseService:
    """
    Root Cause Analysis Service.
    
    READ ONLY - Explains WHY failures occurred.
    NO ML, NO LLM reasoning, NO autonomous decisions.
    
    IMPORTANT:
    - This engine ONLY reconstructs causal chains
    - It does NOT modify events
    - It does NOT create work orders
    - It does NOT execute agents
    - It does NOT perform automation
    """
    
    def __init__(self):
        # In-memory storage
        self._analyses: Dict[str, RootCauseAnalysis] = {}
        self._factors: Dict[str, List[CauseFactor]] = defaultdict(list)
        self._chains: Dict[str, List[CauseChain]] = defaultdict(list)
    
    def calculate_confidence(
        self,
        factor_count: int,
        avg_factor_weight: float,
        chain_depth: int,
        evidence_count: int
    ) -> Tuple[float, ConfidenceResponse]:
        """
        Calculate confidence score based on factors and evidence.
        
        Formula:
        - Factor contribution: up to 40%
        - Chain depth contribution: up to 30%
        - Evidence contribution: up to 30%
        """
        # Factor score (up to 40%)
        factor_score = min(factor_count * 0.1, 0.4) * avg_factor_weight
        
        # Chain depth score (up to 30%)
        chain_score = min(chain_depth * 0.1, 0.3)
        
        # Evidence score (up to 30%)
        evidence_score = min(evidence_count * 0.1, 0.3)
        
        # Total confidence
        total = factor_score + chain_score + evidence_score
        total = max(0, min(1, total))
        
        confidence_detail = ConfidenceResponse(
            overall_confidence=total,
            factor_score=factor_score,
            chain_score=chain_score,
            evidence_score=evidence_score,
            factor_count=factor_count,
            chain_depth=chain_depth,
            evidence_count=evidence_count
        )
        
        return total, confidence_detail
    
    def rank_factors(self, analysis_id: str) -> List[RankedFactorResponse]:
        """Rank factors by weight for an analysis."""
        factors = self._factors.get(analysis_id, [])
        
        # Sort by weight descending
        sorted_factors = sorted(factors, key=lambda f: f.weight, reverse=True)
        
        ranked = []
        for idx, factor in enumerate(sorted_factors):
            ranked.append(RankedFactorResponse(
                rank=idx + 1,
                factor=FactorResponse(
                    id=factor.id,
                    factor_type=factor.factor_type.value if hasattr(factor.factor_type, 'value') else factor.factor_type,
                    description=factor.description,
                    weight=factor.weight,
                    evidence=factor.evidence
                )
            ))
        
        return ranked
    
    def analyze_asset(
        self,
        asset_id: str,
        analysis_type: AnalysisType = AnalysisType.FAILURE,
        time_window_hours: int = 24
    ) -> RootCauseAnalysis:
        """
        Analyze an asset for root cause.
        
        Combines all factor analysis methods.
        """
        analysis = RootCauseAnalysis(
            asset_id=asset_id,
            analysis_type=analysis_type,
            probable_cause="Analyzing...",
            confidence=0.0
        )
        
        # Analyze measurements
        measurement_factors = self.analyze_measurements(asset_id, time_window_hours)
        
        # Analyze health history
        health_factors = self.analyze_health_history(asset_id, time_window_hours)
        
        # Analyze events
        event_factors = self.analyze_events(asset_id, time_window_hours)
        
        # Analyze timeline
        timeline_factors = self.analyze_timeline(asset_id, time_window_hours)
        
        # Analyze logbook
        logbook_factors = self.analyze_logbook(asset_id, time_window_hours)
        
        # Combine all factors
        all_factors = (
            measurement_factors +
            health_factors +
            event_factors +
            timeline_factors +
            logbook_factors
        )
        
        # Add factors to analysis
        for factor in all_factors:
            factor.analysis_id = analysis.id
            self._factors[analysis.id].append(factor)
        
        # Build causal chain
        chain = self.build_causal_chain(analysis.id, asset_id)
        
        # Calculate confidence
        avg_weight = sum(f.weight for f in all_factors) / len(all_factors) if all_factors else 0
        confidence, _ = self.calculate_confidence(
            factor_count=len(all_factors),
            avg_factor_weight=avg_weight,
            chain_depth=len(chain),
            evidence_count=len(all_factors)
        )
        
        # Determine probable cause
        probable_cause = self._determine_probable_cause(all_factors)
        
        # Generate summary
        summary = self.generate_summary(analysis.id, asset_id)
        
        # Update analysis
        analysis.probable_cause = probable_cause
        analysis.confidence = confidence
        analysis.summary = summary
        
        # Store analysis
        self._analyses[analysis.id] = analysis
        
        return analysis
    
    def analyze_event(
        self,
        event_id: str,
        asset_id: str
    ) -> RootCauseAnalysis:
        """Analyze a specific event for root cause."""
        analysis = RootCauseAnalysis(
            asset_id=asset_id,
            event_id=event_id,
            analysis_type=AnalysisType.EVENT_SEQUENCE,
            probable_cause="Analyzing event...",
            confidence=0.0
        )
        
        # Analyze event factors
        event_factors = self.analyze_events(asset_id, 24, event_id)
        
        for factor in event_factors:
            factor.analysis_id = analysis.id
            self._factors[analysis.id].append(factor)
        
        # Calculate confidence
        avg_weight = sum(f.weight for f in event_factors) / len(event_factors) if event_factors else 0
        confidence, _ = self.calculate_confidence(
            factor_count=len(event_factors),
            avg_factor_weight=avg_weight,
            chain_depth=1,
            evidence_count=len(event_factors)
        )
        
        # Determine cause
        probable_cause = self._determine_probable_cause(event_factors)
        summary = f"Event sequence analysis for event {event_id}"
        
        analysis.probable_cause = probable_cause
        analysis.confidence = confidence
        analysis.summary = summary
        
        self._analyses[analysis.id] = analysis
        
        return analysis
    
    def analyze_measurements(
        self,
        asset_id: str,
        time_window_hours: int,
        event_id: Optional[str] = None
    ) -> List[CauseFactor]:
        """Analyze measurement anomalies."""
        factors = []
        
        # Simulate measurement analysis
        # In real implementation, would query measurement_service
        measurement_anomalies = self._get_measurement_anomalies(asset_id, time_window_hours)
        
        for anomaly in measurement_anomalies:
            factor = CauseFactor(
                factor_type=FactorType.MEASUREMENT,
                reference_id=anomaly.get("measurement_id"),
                weight=anomaly.get("severity", 0.5),
                description=f"Measurement anomaly: {anomaly.get('description', 'Unknown')}",
                evidence=anomaly.get("evidence")
            )
            factors.append(factor)
        
        return factors
    
    def analyze_health_history(
        self,
        asset_id: str,
        time_window_hours: int
    ) -> List[CauseFactor]:
        """Analyze health history for degradation patterns."""
        factors = []
        
        # Simulate health history analysis
        health_issues = self._get_health_issues(asset_id, time_window_hours)
        
        for issue in health_issues:
            factor = CauseFactor(
                factor_type=FactorType.HEALTH,
                reference_id=issue.get("health_record_id"),
                weight=issue.get("severity", 0.5),
                description=f"Health degradation: {issue.get('description', 'Unknown')}",
                evidence=issue.get("evidence")
            )
            factors.append(factor)
        
        return factors
    
    def analyze_events(
        self,
        asset_id: str,
        time_window_hours: int,
        specific_event_id: Optional[str] = None
    ) -> List[CauseFactor]:
        """Analyze related events."""
        factors = []
        
        events = self._get_related_events(asset_id, time_window_hours, specific_event_id)
        
        for event in events:
            factor = CauseFactor(
                factor_type=FactorType.EVENT,
                reference_id=event.get("event_id"),
                weight=event.get("severity", 0.5),
                description=f"Event: {event.get('description', 'Unknown')}",
                evidence=event.get("evidence")
            )
            factors.append(factor)
        
        return factors
    
    def analyze_timeline(
        self,
        asset_id: str,
        time_window_hours: int
    ) -> List[CauseFactor]:
        """Analyze timeline for patterns."""
        factors = []
        
        timeline_events = self._get_timeline_events(asset_id, time_window_hours)
        
        for tevent in timeline_events:
            factor = CauseFactor(
                factor_type=FactorType.TIMELINE,
                reference_id=tevent.get("timeline_id"),
                weight=tevent.get("significance", 0.5),
                description=f"Timeline event: {tevent.get('description', 'Unknown')}",
                evidence=tevent.get("evidence")
            )
            factors.append(factor)
        
        return factors
    
    def analyze_logbook(
        self,
        asset_id: str,
        time_window_hours: int
    ) -> List[CauseFactor]:
        """Analyze logbook entries."""
        factors = []
        
        logbook_entries = self._get_logbook_entries(asset_id, time_window_hours)
        
        for entry in logbook_entries:
            factor = CauseFactor(
                factor_type=FactorType.LOGBOOK,
                reference_id=entry.get("entry_id"),
                weight=entry.get("relevance", 0.5),
                description=f"Logbook: {entry.get('description', 'Unknown')}",
                evidence=entry.get("evidence")
            )
            factors.append(factor)
        
        return factors
    
    def build_causal_chain(
        self,
        analysis_id: str,
        asset_id: str
    ) -> List[CauseChain]:
        """Build causal chain of asset dependencies."""
        chain = []
        
        # Trace dependency chain
        dependencies = self.trace_dependency_chain(asset_id)
        
        for depth, dep in enumerate(dependencies):
            cause_chain = CauseChain(
                analysis_id=analysis_id,
                depth=depth,
                source_asset_id=dep.get("source_asset_id", asset_id),
                target_asset_id=dep.get("target_asset_id", asset_id),
                relationship_type=dep.get("relationship_type"),
                description=dep.get("description"),
                propagation_time_seconds=dep.get("propagation_time")
            )
            chain.append(cause_chain)
            self._chains[analysis_id].append(cause_chain)
        
        return chain
    
    def trace_dependency_chain(self, asset_id: str) -> List[Dict[str, Any]]:
        """Trace dependency chain for an asset."""
        # Simulate dependency tracing
        # In real implementation, would use relationship service
        dependencies = []
        
        # Example: if asset has dependencies, trace them
        # This is a simplified implementation
        dep_count = hash(asset_id) % 3  # Simulate 0-2 dependencies
        
        for i in range(dep_count):
            dependencies.append({
                "source_asset_id": f"parent-{i}-{asset_id}",
                "target_asset_id": asset_id,
                "relationship_type": "depends_on",
                "description": f"Dependency {i + 1} for {asset_id}",
                "propagation_time": (i + 1) * 60  # seconds
            })
        
        return dependencies
    
    def generate_summary(
        self,
        analysis_id: str,
        asset_id: str
    ) -> str:
        """Generate human-readable summary."""
        factors = self._factors.get(analysis_id, [])
        
        if not factors:
            return f"No significant factors found for asset {asset_id}"
        
        # Get top factors
        top_factors = sorted(factors, key=lambda f: f.weight, reverse=True)[:3]
        
        factor_descriptions = []
        for f in top_factors:
            ft = f.factor_type.value if hasattr(f.factor_type, 'value') else f.factor_type
            factor_descriptions.append(f"{ft}: {f.description}")
        
        return f"Analysis for {asset_id}: {', '.join(factor_descriptions)}"
    
    def get_analysis(self, analysis_id: str) -> Optional[RootCauseAnalysis]:
        """Get analysis by ID."""
        return self._analyses.get(analysis_id)
    
    def get_analyses_for_asset(self, asset_id: str) -> List[RootCauseAnalysis]:
        """Get all analyses for an asset."""
        return [
            a for a in self._analyses.values()
            if a.asset_id == asset_id
        ]
    
    def get_high_confidence_analyses(self, threshold: float = 0.7) -> List[RootCauseAnalysis]:
        """Get high confidence analyses."""
        return [
            a for a in self._analyses.values()
            if a.confidence >= threshold
        ]
    
    def get_factors_for_analysis(self, analysis_id: str) -> List[CauseFactor]:
        """Get all factors for an analysis."""
        return self._factors.get(analysis_id, [])
    
    def get_chains_for_analysis(self, analysis_id: str) -> List[CauseChain]:
        """Get all chains for an analysis."""
        return self._chains.get(analysis_id, [])
    
    # Helper methods (simulated data)
    def _get_measurement_anomalies(self, asset_id: str, hours: int) -> List[Dict]:
        # Simulate finding measurement anomalies
        count = hash(f"{asset_id}-measurements") % 2
        return [
            {
                "measurement_id": f"meas-{i}-{asset_id}",
                "description": f"Measurement spike detected at hour {i}",
                "severity": 0.3 + (i * 0.2),
                "evidence": f"Value exceeded threshold by 20%"
            }
            for i in range(count)
        ]
    
    def _get_health_issues(self, asset_id: str, hours: int) -> List[Dict]:
        count = hash(f"{asset_id}-health") % 2
        return [
            {
                "health_record_id": f"health-{i}-{asset_id}",
                "description": f"Health score dropped below threshold",
                "severity": 0.4 + (i * 0.2),
                "evidence": f"Health score was 75, threshold is 80"
            }
            for i in range(count)
        ]
    
    def _get_related_events(self, asset_id: str, hours: int, event_id: Optional[str]) -> List[Dict]:
        count = hash(f"{asset_id}-events") % 3
        return [
            {
                "event_id": f"event-{i}-{asset_id}",
                "description": f"Related event type {i + 1}",
                "severity": 0.3 + (i * 0.15),
                "evidence": f"Event occurred within analysis window"
            }
            for i in range(count)
        ]
    
    def _get_timeline_events(self, asset_id: str, hours: int) -> List[Dict]:
        count = hash(f"{asset_id}-timeline") % 2
        return [
            {
                "timeline_id": f"tl-{i}-{asset_id}",
                "description": f"Significant timeline event",
                "significance": 0.5,
                "evidence": f"Event recorded at critical timestamp"
            }
            for i in range(count)
        ]
    
    def _get_logbook_entries(self, asset_id: str, hours: int) -> List[Dict]:
        count = hash(f"{asset_id}-logbook") % 2
        return [
            {
                "entry_id": f"log-{i}-{asset_id}",
                "description": f"Relevant logbook entry",
                "relevance": 0.4,
                "evidence": f"Entry mentions similar issue"
            }
            for i in range(count)
        ]
    
    def _determine_probable_cause(self, factors: List[CauseFactor]) -> str:
        """Determine probable cause from factors."""
        if not factors:
            return "No significant factors identified"
        
        # Group by type
        by_type = defaultdict(list)
        for f in factors:
            ft = f.factor_type.value if hasattr(f.factor_type, 'value') else f.factor_type
            by_type[ft].append(f.weight)
        
        # Find highest weighted type
        if by_type:
            max_type = max(by_type.keys(), key=lambda t: sum(by_type[t]))
            
            cause_templates = {
                "measurement": "Measurement anomalies contributed to the issue",
                "event": "Related events triggered the degradation",
                "health": "Health degradation pattern detected",
                "relationship": "Dependency chain affected the asset",
                "timeline": "Timeline pattern indicates root cause",
                "logbook": "Historical logs show similar issues",
                "knowledge": "Knowledge base indicates known failure mode"
            }
            
            return cause_templates.get(max_type, f"Primary factor: {max_type}")
        
        return "Multiple contributing factors identified"


# Global instance
root_cause_service = RootCauseService()
