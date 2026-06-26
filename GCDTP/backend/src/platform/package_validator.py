"""
Package Validator

Validates platform packages.
"""

from typing import Dict, List, Any


class PackageValidator:
    """
    Validates platform packages.
    """
    
    def __init__(self):
        self.issues: List[str] = []
    
    def validate_bundle(
        self,
        bundle_type: str,
        components: List[str]
    ) -> List[str]:
        """Validate a bundle."""
        issues = []
        
        valid_types = ["docker", "offline", "enterprise", "upgrade", "backup"]
        if bundle_type not in valid_types:
            issues.append(f"Invalid bundle type: {bundle_type}")
        
        if not components:
            issues.append("Bundle must have at least one component")
        
        return issues
    
    def validate_installation(
        self,
        profile: str,
        components: List[str]
    ) -> List[str]:
        """Validate an installation."""
        issues = []
        
        valid_profiles = ["minimal", "standard", "enterprise", "full"]
        if profile not in valid_profiles:
            issues.append(f"Invalid profile: {profile}")
        
        if not components:
            issues.append("Installation must have at least one component")
        
        return issues
    
    def validate_upgrade(
        self,
        from_version: str,
        to_version: str
    ) -> List[str]:
        """Validate an upgrade."""
        issues = []
        
        if not from_version:
            issues.append("Source version is required")
        
        if not to_version:
            issues.append("Target version is required")
        
        return issues
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "issues": self.issues,
            "issue_count": len(self.issues),
            "has_critical": any("required" in i.lower() for i in self.issues)
        }
