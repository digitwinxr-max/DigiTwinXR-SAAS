"""
Feature Flag Manager

Manages feature flags.
"""

import uuid
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


class FeatureFlagStatus(str):
    """Feature flag status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SCHEDULED = "scheduled"
    PAUSED = "paused"


@dataclass
class FeatureFlag:
    """Feature flag."""
    name: str
    key: str
    description: str = ""
    status: FeatureFlagStatus = FeatureFlagStatus.INACTIVE
    rollout_percentage: int = 0
    target_organizations: List[str] = None
    scheduled_activation: Optional[datetime] = None
    scheduled_deactivation: Optional[datetime] = None
    
    def __post_init__(self):
        if self.target_organizations is None:
            self.target_organizations = []


class FeatureFlagManager:
    """
    Manages feature flags.
    
    Supports:
    - Enable/disable modules
    - Rollout percentages
    - Organization-specific features
    - Scheduled activation
    """
    
    def __init__(self):
        self._flags: Dict[str, FeatureFlag] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default feature flags."""
        self.create_flag(
            name="New Simulation Engine",
            key="new_simulation_engine",
            description="Enable new simulation engine"
        )
        
        self.create_flag(
            name="Advanced Analytics",
            key="advanced_analytics",
            description="Enable advanced analytics features"
        )
    
    def create_flag(
        self,
        name: str,
        key: str,
        description: str = "",
        rollout_percentage: int = 0
    ) -> FeatureFlag:
        """Create a feature flag."""
        flag = FeatureFlag(
            name=name,
            key=key,
            description=description,
            rollout_percentage=rollout_percentage
        )
        self._flags[key] = flag
        return flag
    
    def get_flag(self, key: str) -> Optional[FeatureFlag]:
        """Get a feature flag."""
        return self._flags.get(key)
    
    def get_all_flags(self) -> List[FeatureFlag]:
        """Get all feature flags."""
        return list(self._flags.values())
    
    def get_active_flags(self) -> List[FeatureFlag]:
        """Get active feature flags."""
        return [f for f in self._flags.values() if f.status == FeatureFlagStatus.ACTIVE]
    
    def enable(self, key: str) -> bool:
        """Enable a feature flag."""
        flag = self._flags.get(key)
        if flag:
            flag.status = FeatureFlagStatus.ACTIVE
            return True
        return False
    
    def disable(self, key: str) -> bool:
        """Disable a feature flag."""
        flag = self._flags.get(key)
        if flag:
            flag.status = FeatureFlagStatus.INACTIVE
            return True
        return False
    
    def set_rollout_percentage(self, key: str, percentage: int) -> bool:
        """Set rollout percentage."""
        if percentage < 0 or percentage > 100:
            return False
        
        flag = self._flags.get(key)
        if flag:
            flag.rollout_percentage = percentage
            return True
        return False
    
    def schedule_activation(
        self,
        key: str,
        activation_time: datetime
    ) -> bool:
        """Schedule flag activation."""
        flag = self._flags.get(key)
        if flag:
            flag.scheduled_activation = activation_time
            flag.status = FeatureFlagStatus.SCHEDULED
            return True
        return False
    
    def schedule_deactivation(
        self,
        key: str,
        deactivation_time: datetime
    ) -> bool:
        """Schedule flag deactivation."""
        flag = self._flags.get(key)
        if flag:
            flag.scheduled_deactivation = deactivation_time
            return True
        return False
    
    def add_organization(self, key: str, org_id: str) -> bool:
        """Add organization to flag."""
        flag = self._flags.get(key)
        if flag and org_id not in flag.target_organizations:
            flag.target_organizations.append(org_id)
            return True
        return False
    
    def remove_organization(self, key: str, org_id: str) -> bool:
        """Remove organization from flag."""
        flag = self._flags.get(key)
        if flag and org_id in flag.target_organizations:
            flag.target_organizations.remove(org_id)
            return True
        return False
    
    def is_enabled(
        self,
        key: str,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """Check if a feature flag is enabled."""
        flag = self._flags.get(key)
        if not flag:
            return False
        
        # Check status
        if flag.status != FeatureFlagStatus.ACTIVE:
            # Check scheduled
            if flag.status == FeatureFlagStatus.SCHEDULED:
                if flag.scheduled_activation and datetime.utcnow() >= flag.scheduled_activation:
                    return True
            return False
        
        # Check organization
        if organization_id and organization_id in flag.target_organizations:
            return True
        
        # Check rollout percentage
        if flag.rollout_percentage > 0:
            if user_id:
                # Deterministic based on user_id
                return hash(user_id) % 100 < flag.rollout_percentage
            else:
                return random.random() * 100 < flag.rollout_percentage
        
        return True
