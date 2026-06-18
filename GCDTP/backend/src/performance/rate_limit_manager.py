"""
Rate Limit Manager

Provides rate limiting support.
"""

import time
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
from enum import Enum


class RateLimitAlgorithm(str, Enum):
    """Rate limiting algorithms."""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"


@dataclass
class RateLimitRule:
    """Rate limit rule."""
    rule_id: str
    limit_type: str  # user, organization, global
    target_id: Optional[str]
    requests_per_minute: int
    requests_per_hour: Optional[int] = None
    requests_per_day: Optional[int] = None
    burst_limit: int = 10
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.TOKEN_BUCKET
    is_active: bool = True


@dataclass
class RateLimitResult:
    """Rate limit check result."""
    allowed: bool
    remaining: int
    reset_at: datetime
    limit: int
    algorithm: str


class RateLimitManager:
    """
    Provides rate limiting support.
    
    Supports:
    - Per-user limits
    - Per-organization limits
    - Burst limits
    - Token bucket
    - Sliding window
    - 429 responses
    """
    
    def __init__(self):
        self._rules: Dict[str, RateLimitRule] = {}
        self._buckets: Dict[str, deque] = {}  # Token bucket storage
        self._windows: Dict[str, deque] = {}  # Sliding window storage
        self._violations: Dict[str, list] = {}  # Track violations
    
    def add_rule(
        self,
        rule: RateLimitRule
    ) -> None:
        """Add a rate limit rule."""
        key = self._get_key(rule.limit_type, rule.target_id)
        self._rules[key] = rule
    
    def remove_rule(
        self,
        limit_type: str,
        target_id: Optional[str] = None
    ) -> bool:
        """Remove a rate limit rule."""
        key = self._get_key(limit_type, target_id)
        if key in self._rules:
            del self._rules[key]
            return True
        return False
    
    def check_limit(
        self,
        limit_type: str,
        target_id: Optional[str] = None,
        identifier: Optional[str] = None
    ) -> RateLimitResult:
        """
        Check if request is within rate limit.
        
        Args:
            limit_type: Type of limit (user, organization, global)
            target_id: Target ID (user_id or org_id)
            identifier: Request identifier
            
        Returns:
            RateLimitResult
        """
        key = self._get_key(limit_type, target_id)
        rule = self._rules.get(key)
        
        if not rule or not rule.is_active:
            return RateLimitResult(
                allowed=True,
                remaining=999999,
                reset_at=datetime.utcnow() + timedelta(hours=1),
                limit=0,
                algorithm="none"
            )
        
        # Use appropriate algorithm
        if rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return self._check_token_bucket(rule, identifier or key)
        elif rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return self._check_sliding_window(rule, identifier or key)
        else:
            return self._check_fixed_window(rule, identifier or key)
    
    def _get_key(
        self,
        limit_type: str,
        target_id: Optional[str]
    ) -> str:
        """Get storage key."""
        if target_id:
            return f"{limit_type}:{target_id}"
        return f"{limit_type}:global"
    
    def _check_token_bucket(
        self,
        rule: RateLimitRule,
        key: str
    ) -> RateLimitResult:
        """Check using token bucket algorithm."""
        now = time.time()
        
        if key not in self._buckets:
            # Initialize bucket with full tokens
            self._buckets[key] = deque(maxlen=rule.requests_per_minute)
        
        bucket = self._buckets[key]
        
        # Remove expired tokens
        while bucket and bucket[0] < now - 60:
            bucket.popleft()
        
        # Check limit
        if len(bucket) < rule.requests_per_minute:
            bucket.append(now)
            return RateLimitResult(
                allowed=True,
                remaining=rule.requests_per_minute - len(bucket),
                reset_at=datetime.fromtimestamp(bucket[0] + 60) if bucket else datetime.utcnow(),
                limit=rule.requests_per_minute,
                algorithm="token_bucket"
            )
        
        return RateLimitResult(
            allowed=False,
            remaining=0,
            reset_at=datetime.fromtimestamp(bucket[0] + 60) if bucket else datetime.utcnow(),
            limit=rule.requests_per_minute,
            algorithm="token_bucket"
        )
    
    def _check_sliding_window(
        self,
        rule: RateLimitRule,
        key: str
    ) -> RateLimitResult:
        """Check using sliding window algorithm."""
        now = time.time()
        window = 60  # 1 minute
        
        if key not in self._windows:
            self._windows[key] = deque()
        
        window_store = self._windows[key]
        
        # Remove expired entries
        while window_store and window_store[0] < now - window:
            window_store.popleft()
        
        # Check limit
        if len(window_store) < rule.requests_per_minute:
            window_store.append(now)
            return RateLimitResult(
                allowed=True,
                remaining=rule.requests_per_minute - len(window_store),
                reset_at=datetime.fromtimestamp(now + window),
                limit=rule.requests_per_minute,
                algorithm="sliding_window"
            )
        
        return RateLimitResult(
            allowed=False,
            remaining=0,
            reset_at=datetime.fromtimestamp(now + window),
            limit=rule.requests_per_minute,
            algorithm="sliding_window"
        )
    
    def _check_fixed_window(
        self,
        rule: RateLimitRule,
        key: str
    ) -> RateLimitResult:
        """Check using fixed window algorithm."""
        now = datetime.utcnow()
        window_start = now.replace(second=0, microsecond=0)
        
        if key not in self._windows:
            self._windows[key] = deque()
        
        window_store = self._windows[key]
        
        # Reset if new window
        if window_store and window_store[0] != window_start:
            window_store.clear()
            window_store.append(window_start)
        
        if not window_store:
            window_store.append(window_start)
        
        count = len(window_store) - 1 if len(window_store) > 0 else 0
        
        if count < rule.requests_per_minute:
            window_store.append(now)
            return RateLimitResult(
                allowed=True,
                remaining=rule.requests_per_minute - count - 1,
                reset_at=window_start + timedelta(minutes=1),
                limit=rule.requests_per_minute,
                algorithm="fixed_window"
            )
        
        return RateLimitResult(
            allowed=False,
            remaining=0,
            reset_at=window_start + timedelta(minutes=1),
            limit=rule.requests_per_minute,
            algorithm="fixed_window"
        )
    
    def record_violation(
        self,
        limit_type: str,
        target_id: Optional[str],
        identifier: str
    ) -> None:
        """Record a rate limit violation."""
        key = self._get_key(limit_type, target_id)
        
        if key not in self._violations:
            self._violations[key] = []
        
        self._violations[key].append({
            "identifier": identifier,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Trim old violations
        if len(self._violations[key]) > 100:
            self._violations[key] = self._violations[key][-100:]
    
    def get_violations(
        self,
        limit_type: str,
        target_id: Optional[str] = None,
        window_hours: int = 24
    ) -> list:
        """Get rate limit violations."""
        key = self._get_key(limit_type, target_id)
        violations = self._violations.get(key, [])
        
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        return [
            v for v in violations
            if datetime.fromisoformat(v["timestamp"]) > cutoff
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limit statistics."""
        return {
            "total_rules": len(self._rules),
            "active_rules": sum(1 for r in self._rules.values() if r.is_active),
            "violations_tracked": sum(len(v) for v in self._violations.values())
        }
