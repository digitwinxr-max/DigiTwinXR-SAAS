"""Health service for calculating and managing asset health."""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.health import AssetHealth
from ..models.asset import Asset
from ..models.event import Event
from ..models.asset_health_dependency import AssetHealthDependency
from ..schemas.health import (
    AssetHealthWithAssetResponse,
    HealthRecalculateResponse,
    HealthSummaryResponse,
)
from ..events import emit, EventType


class HealthService:
    """Service class for asset health operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_health_for_asset(self, asset_id: UUID) -> Optional[AssetHealth]:
        """Get health record for a specific asset."""
        return self.db.query(AssetHealth).filter(AssetHealth.asset_id == asset_id).first()

    def get_all_health_records(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> tuple[List[AssetHealth], int]:
        """Get all asset health records with optional filtering."""
        query = self.db.query(AssetHealth)

        if status:
            query = query.filter(AssetHealth.health_status == status)

        total = query.count()
        records = query.order_by(AssetHealth.health_score.desc()).offset(skip).limit(limit).all()

        return records, total

    def calculate_asset_health(self, asset_id: UUID) -> AssetHealth:
        """Calculate health for an asset based on active events and dependencies.
        
        Logic:
        - Start score = 100
        - CRITICAL event = -20
        - WARNING event = -10
        - Subtract dependency penalties from related assets
        - Clamp score between 0 and 100
        - Derive status: 80-100 HEALTHY, 40-79 DEGRADED, 0-39 CRITICAL
        
        Args:
            asset_id: The asset ID to calculate health for
            
        Returns:
            AssetHealth record (created or updated)
        """
        # Count active events by severity
        events = self.db.query(Event).filter(
            Event.asset_id == asset_id,
            Event.status == "ACTIVE",
        ).all()

        critical_count = sum(1 for e in events if e.severity == "CRITICAL")
        warning_count = sum(1 for e in events if e.severity == "WARNING")

        # Get or create health record
        health = self.get_health_for_asset(asset_id)
        if not health:
            health = AssetHealth(asset_id=asset_id)
            self.db.add(health)

        # Update health based on events (this sets the base penalty)
        health.update_from_events(critical_count, warning_count)
        
        # Apply dependency penalties
        dependency_penalty = self._calculate_dependency_penalty(asset_id)
        
        # Final health = 100 - local_penalty - dependency_penalty
        # Note: health.penalty already = local_event_penalty
        base_health = 100.0
        final_score = base_health - health.penalty - dependency_penalty
        
        # Clamp to valid range
        final_score = max(0.0, min(100.0, final_score))
        
        # Update health record
        health.health_score = final_score
        health.dependency_penalty = dependency_penalty
        
        # Update status
        if final_score >= 80:
            health.health_status = "HEALTHY"
        elif final_score >= 40:
            health.health_status = "DEGRADED"
        else:
            health.health_status = "CRITICAL"
        
        self.db.commit()
        self.db.refresh(health)
        
        return health
    
    def _calculate_dependency_penalty(self, asset_id: UUID) -> float:
        """Calculate total dependency penalty for an asset.
        
        Args:
            asset_id: The asset ID
            
        Returns:
            Total dependency penalty (0-100)
        """
        # Get all dependency penalties for this asset
        dependencies = self.db.query(AssetHealthDependency).filter(
            AssetHealthDependency.asset_id == asset_id
        ).all()
        
        return sum(d.penalty for d in dependencies)

    def recalculate_health(self, asset_id: UUID, emit_event: bool = True) -> HealthRecalculateResponse:
        """Recalculate health for an asset (idempotent).
        
        This is the main entry point for health recalculation.
        Can be called manually or triggered by event changes.
        
        Args:
            asset_id: The asset ID to recalculate health for
            emit_event: Whether to emit health.updated event (default: True)
            
        Returns:
            HealthRecalculateResponse with updated values
        """
        health = self.calculate_asset_health(asset_id)
        
        # Emit health.updated event via dispatcher
        if emit_event:
            emit(
                event_type=EventType.HEALTH_UPDATED,
                source="HealthService",
                payload={
                    "health_id": str(health.id),
                    "health_score": health.health_score,
                    "health_status": health.health_status,
                    "active_event_count": health.active_event_count,
                },
                asset_id=asset_id,
            )
        
        return HealthRecalculateResponse(
            asset_id=asset_id,
            health_score=health.health_score,
            health_status=health.health_status,
            active_event_count=health.active_event_count,
            message=f"Health recalculated for asset {asset_id}",
        )

    def recalculate_all_health(self, recalculate_network: bool = True) -> List[HealthRecalculateResponse]:
        """Recalculate health for all assets with sensors or events.
        
        Args:
            recalculate_network: Whether to also recalculate dependency network
            
        Returns:
            List of HealthRecalculateResponse for all updated assets
        """
        # First recalculate dependency penalties if requested
        if recalculate_network:
            self._recalculate_dependency_network()
        
        # Get all assets that have events or health records
        asset_ids_with_events = self.db.query(Event.asset_id).distinct().all()
        asset_ids_with_health = self.db.query(AssetHealth.asset_id).distinct().all()
        
        all_asset_ids = set(
            [a[0] for a in asset_ids_with_events] + 
            [a[0] for a in asset_ids_with_health]
        )
        
        results = []
        for asset_id in all_asset_ids:
            result = self.recalculate_health(asset_id)
            results.append(result)
        
        return results
    
    def _recalculate_dependency_network(self):
        """Recalculate the dependency health network.
        
        This is called automatically when health is recalculated to ensure
        dependency penalties are up-to-date.
        """
        from .dependency_health_service import DependencyHealthService
        
        try:
            dep_service = DependencyHealthService(self.db)
            dep_service.recalculate_network_health()
        except Exception as e:
            # Log but don't fail health recalculation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to recalculate dependency network: {e}")

    def get_health_with_asset_info(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> tuple[List[AssetHealthWithAssetResponse], int]:
        """Get health records with associated asset information."""
        records, total = self.get_all_health_records(skip, limit, status)
        
        result = []
        for health in records:
            asset = self.db.query(Asset).filter(Asset.id == health.asset_id).first()
            result.append(AssetHealthWithAssetResponse(
                id=health.id,
                asset_id=health.asset_id,
                health_score=health.health_score,
                health_status=health.health_status,
                active_event_count=health.active_event_count,
                calculation_method=health.calculation_method,
                last_updated=health.last_updated,
                asset_name=asset.name if asset else None,
                asset_type=asset.asset_type if asset else None,
            ))
        
        return result, total

    def get_health_summary(self) -> HealthSummaryResponse:
        """Get summary statistics for all asset health."""
        all_health = self.db.query(AssetHealth).all()
        
        total = len(all_health)
        if total == 0:
            return HealthSummaryResponse(
                total_assets=0,
                healthy_count=0,
                degraded_count=0,
                critical_count=0,
                average_health_score=100.0,
            )
        
        healthy = sum(1 for h in all_health if h.health_status == "HEALTHY")
        degraded = sum(1 for h in all_health if h.health_status == "DEGRADED")
        critical = sum(1 for h in all_health if h.health_status == "CRITICAL")
        avg_score = sum(h.health_score for h in all_health) / total
        
        return HealthSummaryResponse(
            total_assets=total,
            healthy_count=healthy,
            degraded_count=degraded,
            critical_count=critical,
            average_health_score=round(avg_score, 2),
        )