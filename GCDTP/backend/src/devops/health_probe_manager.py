"""
Health Probe Manager

Manages health probes for Kubernetes/orchestration.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


class ProbeType(str):
    """Probe types."""
    READINESS = "readiness"
    LIVENESS = "liveness"
    STARTUP = "startup"
    DEPENDENCY = "dependency"


@dataclass
class HealthProbe:
    """Health probe configuration."""
    name: str
    probe_type: ProbeType
    endpoint: str
    target_service: str
    check_interval_seconds: int = 30
    timeout_seconds: int = 10
    failure_threshold: int = 3
    success_threshold: int = 1
    is_enabled: bool = True


class HealthProbeManager:
    """
    Manages health probes.
    
    Supports:
    - Readiness probes
    - Liveness probes
    - Startup probes
    - Dependency probes
    """
    
    def __init__(self):
        self._probes: Dict[str, HealthProbe] = {}
        self._results: Dict[str, Dict] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default probes."""
        self.register_probe(HealthProbe(
            name="api_readiness",
            probe_type=ProbeType.READINESS,
            endpoint="/health/ready",
            target_service="api"
        ))
        
        self.register_probe(HealthProbe(
            name="api_liveness",
            probe_type=ProbeType.LIVENESS,
            endpoint="/health/live",
            target_service="api"
        ))
        
        self.register_probe(HealthProbe(
            name="database_dependency",
            probe_type=ProbeType.DEPENDENCY,
            endpoint="/health",
            target_service="database"
        ))
        
        self.register_probe(HealthProbe(
            name="eventbus_dependency",
            probe_type=ProbeType.DEPENDENCY,
            endpoint="/health",
            target_service="eventbus"
        ))
    
    def register_probe(self, probe: HealthProbe) -> None:
        """Register a health probe."""
        self._probes[probe.name] = probe
    
    def get_probe(self, name: str) -> Optional[HealthProbe]:
        """Get a probe."""
        return self._probes.get(name)
    
    def get_probes_by_type(self, probe_type: ProbeType) -> List[HealthProbe]:
        """Get probes by type."""
        return [p for p in self._probes.values() if p.probe_type == probe_type]
    
    def get_enabled_probes(self) -> List[HealthProbe]:
        """Get enabled probes."""
        return [p for p in self._probes.values() if p.is_enabled]
    
    def disable_probe(self, name: str) -> bool:
        """Disable a probe."""
        probe = self._probes.get(name)
        if probe:
            probe.is_enabled = False
            return True
        return False
    
    def enable_probe(self, name: str) -> bool:
        """Enable a probe."""
        probe = self._probes.get(name)
        if probe:
            probe.is_enabled = True
            return True
        return False
    
    def record_result(
        self,
        probe_name: str,
        healthy: bool,
        response_time_ms: int = 0,
        error_message: str = ""
    ) -> None:
        """Record probe result."""
        self._results[probe_name] = {
            "healthy": healthy,
            "response_time_ms": response_time_ms,
            "error_message": error_message,
            "checked_at": datetime.utcnow().isoformat()
        }
    
    def get_result(self, probe_name: str) -> Optional[Dict]:
        """Get probe result."""
        return self._results.get(probe_name)
    
    def get_all_results(self) -> Dict[str, Dict]:
        """Get all probe results."""
        return dict(self._results)
    
    def is_ready(self) -> bool:
        """Check if all readiness probes pass."""
        readiness_probes = self.get_probes_by_type(ProbeType.READINESS)
        if not readiness_probes:
            return True
        
        for probe in readiness_probes:
            result = self._results.get(probe.name)
            if not result or not result.get("healthy"):
                return False
        return True
    
    def is_alive(self) -> bool:
        """Check if all liveness probes pass."""
        liveness_probes = self.get_probes_by_type(ProbeType.LIVENESS)
        if not liveness_probes:
            return True
        
        for probe in liveness_probes:
            result = self._results.get(probe.name)
            if not result or not result.get("healthy"):
                return False
        return True
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check all dependency probes."""
        dependency_probes = self.get_probes_by_type(ProbeType.DEPENDENCY)
        results = {}
        
        for probe in dependency_probes:
            result = self._results.get(probe.name)
            results[probe.name] = result.get("healthy", False) if result else False
        
        return results
