"""
Deployment Validator

Validates deployments.
"""

from typing import Dict, List, Any


class DeploymentValidator:
    """
    Validates deployment configurations.
    """
    
    def __init__(self):
        self.issues: List[str] = []
    
    def validate_deployment_config(
        self,
        version: str,
        environment: str,
        deployment_type: str
    ) -> List[str]:
        """Validate deployment configuration."""
        issues = []
        
        if not version:
            issues.append("Version is required")
        
        valid_environments = ["development", "test", "staging", "production"]
        if environment not in valid_environments:
            issues.append(f"Invalid environment: {environment}")
        
        valid_types = ["blue_green", "rolling", "canary", "recreate"]
        if deployment_type not in valid_types:
            issues.append(f"Invalid deployment type: {deployment_type}")
        
        return issues
    
    def validate_backup_config(
        self,
        backup_type: str,
        compression_enabled: bool
    ) -> List[str]:
        """Validate backup configuration."""
        issues = []
        
        valid_types = ["postgresql", "config", "metadata", "snapshot"]
        if backup_type not in valid_types:
            issues.append(f"Invalid backup type: {backup_type}")
        
        return issues
    
    def validate_restore_config(
        self,
        restore_type: str,
        point_in_time: bool
    ) -> List[str]:
        """Validate restore configuration."""
        issues = []
        
        valid_types = ["full", "point_in_time", "selective"]
        if restore_type not in valid_types:
            issues.append(f"Invalid restore type: {restore_type}")
        
        if restore_type == "point_in_time" and not point_in_time:
            issues.append("Point-in-time restore requires timestamp")
        
        return issues
    
    def validate_dr_plan(self, plan: Dict) -> List[str]:
        """Validate DR plan."""
        issues = []
        
        required = ["name", "plan_type", "target_rto_minutes", "target_rpo_minutes"]
        for field in required:
            if field not in plan:
                issues.append(f"Missing required field: {field}")
        
        if "target_rto_minutes" in plan and plan["target_rto_minutes"] <= 0:
            issues.append("RTO must be positive")
        
        if "target_rpo_minutes" in plan and plan["target_rpo_minutes"] <= 0:
            issues.append("RPO must be positive")
        
        return issues
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "issues": self.issues,
            "issue_count": len(self.issues),
            "has_critical": any(
                "required" in i.lower() or "must be" in i.lower()
                for i in self.issues
            ),
        }
