"""
Retention Manager

Manages retention policies and object lifecycle.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .storage_types import RetentionMode, RetentionStatus


@dataclass
class RetentionPolicy:
    """Retention policy."""
    id: str
    name: str
    bucket_id: str
    retention_days: int
    retention_mode: RetentionMode
    is_default: bool
    status: RetentionStatus


class RetentionManager:
    """
    Manages retention policies.
    
    Features:
    - Retention policies
    - Expiration dates
    - Archive status
    - Legal hold metadata
    """
    
    def __init__(self):
        self._policies: Dict[str, RetentionPolicy] = {}
        self._legal_holds: Dict[str, datetime] = {}  # object_id -> hold_until
    
    def create_policy(
        self,
        name: str,
        bucket_id: str,
        retention_days: int,
        retention_mode: RetentionMode,
        is_default: bool = False
    ) -> RetentionPolicy:
        """Create a retention policy."""
        policy_id = str(uuid.uuid4())
        
        policy = RetentionPolicy(
            id=policy_id,
            name=name,
            bucket_id=bucket_id,
            retention_days=retention_days,
            retention_mode=retention_mode,
            is_default=is_default,
            status=RetentionStatus.ACTIVE
        )
        
        self._policies[policy_id] = policy
        return policy
    
    def get_policy(self, policy_id: str) -> Optional[RetentionPolicy]:
        """Get a policy."""
        return self._policies.get(policy_id)
    
    def get_policies_by_bucket(self, bucket_id: str) -> List[RetentionPolicy]:
        """Get policies for a bucket."""
        return [p for p in self._policies.values() if p.bucket_id == bucket_id]
    
    def get_default_policy(self, bucket_id: str) -> Optional[RetentionPolicy]:
        """Get default policy for a bucket."""
        for policy in self._policies.values():
            if policy.bucket_id == bucket_id and policy.is_default:
                return policy
        return None
    
    def is_expired(self, object_id: str, created_at: datetime) -> bool:
        """Check if an object is expired based on retention policy."""
        for policy in self._policies.values():
            if policy.status == RetentionStatus.ACTIVE:
                expiry_date = created_at + timedelta(days=policy.retention_days)
                if datetime.utcnow() > expiry_date:
                    return True
        return False
    
    def apply_legal_hold(self, object_id: str, hold_until: datetime) -> bool:
        """Apply legal hold to an object."""
        self._legal_holds[object_id] = hold_until
        return True
    
    def remove_legal_hold(self, object_id: str) -> bool:
        """Remove legal hold from an object."""
        if object_id in self._legal_holds:
            del self._legal_holds[object_id]
            return True
        return False
    
    def is_legal_hold(self, object_id: str) -> bool:
        """Check if object has legal hold."""
        if object_id not in self._legal_holds:
            return False
        
        hold_until = self._legal_holds[object_id]
        if hold_until and datetime.utcnow() > hold_until:
            del self._legal_holds[object_id]
            return False
        
        return True
