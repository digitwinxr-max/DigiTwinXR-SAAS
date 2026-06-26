"""
Performance Validator

Validates performance components.
"""

from typing import Dict, List, Any


class PerformanceValidator:
    """
    Validates performance components.
    
    Checks:
    - Cache consistency
    - Rate limit configuration
    - Pagination parameters
    - Bulk operation integrity
    - API version support
    """
    
    def __init__(self):
        self.issues: List[str] = []
    
    def validate_cache_config(
        self,
        max_size: int,
        default_ttl: int
    ) -> List[str]:
        """Validate cache configuration."""
        issues = []
        
        if max_size <= 0:
            issues.append("Cache max_size must be positive")
        
        if max_size > 1000000:
            issues.append("Cache max_size seems unreasonably large")
        
        if default_ttl <= 0:
            issues.append("Cache default_ttl must be positive")
        
        if default_ttl > 86400:
            issues.append("Cache default_ttl exceeds 24 hours")
        
        return issues
    
    def validate_rate_limit_rule(
        self,
        rpm: int,
        burst: int
    ) -> List[str]:
        """Validate rate limit rule."""
        issues = []
        
        if rpm <= 0:
            issues.append("Rate limit RPM must be positive")
        
        if rpm > 10000:
            issues.append("Rate limit RPM seems unreasonably high")
        
        if burst < 0:
            issues.append("Burst limit cannot be negative")
        
        if burst > rpm:
            issues.append("Burst limit cannot exceed RPM")
        
        return issues
    
    def validate_pagination_params(
        self,
        page: int,
        page_size: int,
        max_page_size: int
    ) -> List[str]:
        """Validate pagination parameters."""
        issues = []
        
        if page < 1:
            issues.append("Page must be at least 1")
        
        if page_size < 1:
            issues.append("Page size must be at least 1")
        
        if page_size > max_page_size:
            issues.append(f"Page size exceeds maximum ({max_page_size})")
        
        return issues
    
    def validate_bulk_job(
        self,
        job_type: str,
        total_items: int,
        max_batch_size: int
    ) -> List[str]:
        """Validate bulk job."""
        issues = []
        
        valid_types = ["create", "update", "delete"]
        if job_type not in valid_types:
            issues.append(f"Invalid job type: {job_type}")
        
        if total_items <= 0:
            issues.append("Total items must be positive")
        
        if total_items > max_batch_size:
            issues.append(f"Total items exceeds max batch size ({max_batch_size})")
        
        return issues
    
    def validate_api_version(
        self,
        version: str,
        supported_versions: List[str]
    ) -> List[str]:
        """Validate API version."""
        issues = []
        
        if not version:
            issues.append("Version is required")
        
        if version and version not in supported_versions:
            issues.append(f"Version '{version}' is not supported")
        
        return issues
    
    def validate_connection_pool_config(
        self,
        min_connections: int,
        max_connections: int
    ) -> List[str]:
        """Validate connection pool configuration."""
        issues = []
        
        if min_connections < 0:
            issues.append("Min connections cannot be negative")
        
        if max_connections <= 0:
            issues.append("Max connections must be positive")
        
        if min_connections > max_connections:
            issues.append("Min connections cannot exceed max connections")
        
        return issues
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "issues": self.issues,
            "issue_count": len(self.issues),
            "has_critical": any(
                "must be positive" in i.lower() or
                "required" in i.lower()
                for i in self.issues
            ),
        }
