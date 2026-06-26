"""
Storage Validator

Validates storage operations.
"""

from typing import Dict, List, Any


class StorageValidator:
    """
    Validates storage operations.
    """
    
    def __init__(self):
        self.issues: List[str] = []
    
    def validate_bucket_name(self, name: str) -> List[str]:
        """Validate bucket name."""
        issues = []
        
        if not name:
            issues.append("Bucket name is required")
        elif len(name) < 3:
            issues.append("Bucket name must be at least 3 characters")
        elif len(name) > 63:
            issues.append("Bucket name must be at most 63 characters")
        elif not name.replace("-", "").replace("_", "").isalnum():
            issues.append("Bucket name can only contain alphanumeric characters, hyphens, and underscores")
        
        return issues
    
    def validate_object_key(self, key: str) -> List[str]:
        """Validate object key."""
        issues = []
        
        if not key:
            issues.append("Object key is required")
        elif len(key) > 1024:
            issues.append("Object key must be at most 1024 characters")
        elif key.startswith("/"):
            issues.append("Object key cannot start with /")
        
        return issues
    
    def validate_upload_size(self, size_bytes: int, max_size: int = 5 * 1024 * 1024 * 1024) -> List[str]:
        """Validate upload size."""
        issues = []
        
        if size_bytes <= 0:
            issues.append("Upload size must be positive")
        elif size_bytes > max_size:
            issues.append(f"Upload size exceeds maximum ({max_size} bytes)")
        
        return issues
    
    def validate_content_type(self, content_type: str) -> List[str]:
        """Validate content type."""
        issues = []
        
        if not content_type:
            issues.append("Content type is required")
        elif "/" not in content_type:
            issues.append("Content type must be in format type/subtype")
        
        return issues
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "issues": self.issues,
            "issue_count": len(self.issues),
            "has_critical": any("required" in i.lower() for i in self.issues)
        }
