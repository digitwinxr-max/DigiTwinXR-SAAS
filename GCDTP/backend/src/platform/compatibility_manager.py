"""
Compatibility Manager

Manages compatibility matrix.
"""

from typing import Dict, List, Optional, Any


class CompatibilityManager:
    """
    Manages compatibility matrix.
    """
    
    def __init__(self):
        self._matrix: Dict[str, Dict] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default compatibility."""
        self.add_compatibility(
            "postgresql",
            "14.0",
            compatible={"14.x": "14.0-14.x", "15.x": "15.0-15.x"},
            incompatible=["13.x"]
        )
        
        self.add_compatibility(
            "python",
            "3.10",
            compatible={"3.10": "3.10.x", "3.11": "3.11.x"},
            incompatible=["3.9"]
        )
    
    def add_compatibility(
        self,
        component: str,
        version: str,
        compatible: Optional[Dict] = None,
        incompatible: Optional[List] = None,
        requirements: Optional[Dict] = None
    ) -> None:
        """Add compatibility entry."""
        key = f"{component}:{version}"
        self._matrix[key] = {
            "component": component,
            "version": version,
            "compatible": compatible or {},
            "incompatible": incompatible or [],
            "requirements": requirements or {}
        }
    
    def get_compatibility(self, component: str, version: str) -> Optional[Dict]:
        """Get compatibility info."""
        key = f"{component}:{version}"
        return self._matrix.get(key)
    
    def is_compatible(self, component: str, version: str, target_version: str) -> bool:
        """Check if versions are compatible."""
        key = f"{component}:{version}"
        entry = self._matrix.get(key)
        
        if not entry:
            return True  # Unknown, assume compatible
        
        # Check incompatible
        if target_version in entry.get("incompatible", []):
            return False
        
        return True
    
    def get_all_entries(self) -> List[Dict]:
        """Get all compatibility entries."""
        return list(self._matrix.values())
