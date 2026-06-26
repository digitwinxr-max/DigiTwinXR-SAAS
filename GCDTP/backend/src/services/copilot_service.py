"""
Cognitive Copilot Service

Provides AI context and explanations.
This is read-only - NO LLM integration yet.
Responses are deterministic templates.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import defaultdict

from ..models.copilot_session import CopilotSession
from ..models.copilot_message import CopilotMessage, MessageRole
from ..schemas.copilot import (
    CopilotQuery,
    CopilotAnswer,
    ContextBundle,
    AssetSummary,
    HealthSummary,
    EventSummary
)


class CopilotService:
    """
    Service for Cognitive Copilot operations.
    
    This service provides:
    - Session management
    - Message storage
    - Context bundle building
    - Deterministic summaries
    
    IMPORTANT:
    - NO LLM integration yet
    - Responses are deterministic templates
    - Simple templates only
    - Pure aggregation
    
    This is read-only - no operational modifications.
    """
    
    def __init__(self):
        # In-memory session storage
        self._sessions: Dict[str, CopilotSession] = {}
        # In-memory message storage
        self._messages: Dict[str, CopilotMessage] = {}
        # Index by session
        self._messages_by_session: Dict[str, List[str]] = defaultdict(list)
    
    def create_session(self, session_name: str) -> CopilotSession:
        """
        Create a new copilot session.
        
        Args:
            session_name: Name for the session
            
        Returns:
            Created CopilotSession
        """
        session = CopilotSession(session_name=session_name)
        self._sessions[session.id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[CopilotSession]:
        """Get a session by ID."""
        return self._sessions.get(session_id)
    
    def get_all_sessions(self) -> List[CopilotSession]:
        """Get all sessions sorted by last activity."""
        sessions = list(self._sessions.values())
        sessions.sort(key=lambda s: s.last_activity_at, reverse=True)
        return sessions
    
    def add_message(
        self,
        session_id: str,
        role: str,
        message: str,
        context_data: Optional[Dict[str, Any]] = None
    ) -> Optional[CopilotMessage]:
        """
        Add a message to a session.
        
        Args:
            session_id: Session ID
            role: Message role (user/assistant)
            message: Message content
            context_data: Optional context data
            
        Returns:
            Created CopilotMessage or None
        """
        if session_id not in self._sessions:
            return None
        
        msg = CopilotMessage(
            session_id=session_id,
            role=MessageRole(role),
            message=message,
            context_data=context_data
        )
        
        self._messages[msg.id] = msg
        self._messages_by_session[session_id].append(msg.id)
        
        # Update session
        session = self._sessions[session_id]
        session.last_activity_at = datetime.utcnow()
        session.message_count = len(self._messages_by_session[session_id])
        
        return msg
    
    def get_messages(self, session_id: str) -> List[CopilotMessage]:
        """Get all messages in a session."""
        msg_ids = self._messages_by_session.get(session_id, [])
        messages = [self._messages[mid] for mid in msg_ids if mid in self._messages]
        messages.sort(key=lambda m: m.timestamp)
        return messages
    
    def build_context_bundle(
        self,
        entity_type: str,
        entity_id: str,
        context_data: Dict[str, Any] = None
    ) -> ContextBundle:
        """
        Build a context bundle from all sources.
        
        This aggregates data from:
        - Asset Engine
        - Measurement Engine
        - Event Engine
        - Health Engine
        - Relationship Engine
        - Timeline Engine
        - Logbook Engine
        - Knowledge Repository
        - Semantic Layer
        - Scenario Engine
        - Recovery Engine
        
        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            context_data: Additional context
            
        Returns:
            ContextBundle with aggregated data
        """
        bundle = ContextBundle(
            entity_type=entity_type,
            entity_id=entity_id
        )
        
        # Summarize from each source
        if context_data:
            if "asset" in context_data:
                bundle.asset = context_data["asset"]
            if "health" in context_data:
                bundle.health = context_data["health"]
            if "sensors" in context_data:
                bundle.sensors = context_data["sensors"]
            if "events" in context_data:
                bundle.events = context_data["events"]
            if "measurements" in context_data:
                bundle.measurements = context_data["measurements"]
            if "relationships" in context_data:
                bundle.relationships = context_data["relationships"]
            if "semantic" in context_data:
                bundle.semantic = context_data["semantic"]
            if "timeline" in context_data:
                bundle.timeline = context_data["timeline"]
            if "logbook" in context_data:
                bundle.logbook = context_data["logbook"]
            if "knowledge" in context_data:
                bundle.knowledge = context_data["knowledge"]
        
        # Generate summary
        bundle.summary = self._generate_bundle_summary(bundle)
        
        return bundle
    
    def _generate_bundle_summary(self, bundle: ContextBundle) -> str:
        """Generate a summary of the context bundle."""
        parts = []
        
        if bundle.entity_type and bundle.entity_id:
            parts.append(f"Entity: {bundle.entity_type}/{bundle.entity_id}")
        
        if bundle.asset:
            parts.append(f"Asset: {bundle.asset.get('name', 'Unknown')}")
            parts.append(f"Status: {bundle.asset.get('status', 'Unknown')}")
        
        if bundle.health:
            parts.append(f"Health: {bundle.health.get('health_status', 'Unknown')}")
            if "health_score" in bundle.health:
                parts.append(f"Score: {bundle.health['health_score']}")
        
        if bundle.events:
            parts.append(f"Active Events: {len(bundle.events)}")
        
        if bundle.sensors:
            parts.append(f"Sensors: {len(bundle.sensors)}")
        
        if bundle.logbook:
            parts.append(f"Logbook Entries: {len(bundle.logbook)}")
        
        if bundle.knowledge:
            parts.append(f"Related Documents: {len(bundle.knowledge)}")
        
        return " | ".join(parts) if parts else "No context available"
    
    def summarize_asset(self, asset_data: Dict[str, Any]) -> str:
        """
        Generate asset summary.
        
        Args:
            asset_data: Asset data
            
        Returns:
            Summary string
        """
        if not asset_data:
            return "No asset information available."
        
        parts = []
        parts.append(f"Asset: {asset_data.get('name', 'Unknown')}")
        
        if "status" in asset_data:
            parts.append(f"Status: {asset_data['status']}")
        
        if "category" in asset_data:
            parts.append(f"Category: {asset_data['category']}")
        
        if "location" in asset_data:
            parts.append(f"Location: {asset_data['location']}")
        
        return ". ".join(parts)
    
    def summarize_health(self, health_data: Dict[str, Any]) -> str:
        """
        Generate health summary.
        
        Args:
            health_data: Health data
            
        Returns:
            Summary string
        """
        if not health_data:
            return "No health information available."
        
        parts = []
        parts.append(f"Health Status: {health_data.get('health_status', 'Unknown')}")
        
        if "health_score" in health_data:
            score = health_data["health_score"]
            parts.append(f"Health Score: {score}/100")
        
        if "dependency_penalty" in health_data:
            penalty = health_data["dependency_penalty"]
            parts.append(f"Dependency Penalty: -{penalty}")
        
        return ". ".join(parts)
    
    def summarize_events(self, events: List[Dict[str, Any]]) -> str:
        """
        Generate events summary.
        
        Args:
            events: List of events
            
        Returns:
            Summary string
        """
        if not events:
            return "No active events."
        
        counts = defaultdict(int)
        for event in events:
            severity = event.get("severity", "UNKNOWN")
            counts[severity] += 1
        
        parts = [f"Total Events: {len(events)}"]
        
        if counts.get("CRITICAL"):
            parts.append(f"Critical: {counts['CRITICAL']}")
        if counts.get("WARNING"):
            parts.append(f"Warning: {counts['WARNING']}")
        
        return ". ".join(parts)
    
    def summarize_timeline(self, snapshots: List[Dict[str, Any]]) -> str:
        """
        Generate timeline summary.
        
        Args:
            snapshots: List of timeline snapshots
            
        Returns:
            Summary string
        """
        if not snapshots:
            return "No timeline data available."
        
        types = defaultdict(int)
        for snap in snapshots:
            stype = snap.get("snapshot_type", "unknown")
            types[stype] += 1
        
        parts = [f"Timeline Snapshots: {len(snapshots)}"]
        for stype, count in types.items():
            parts.append(f"{stype}: {count}")
        
        return ". ".join(parts)
    
    def summarize_logbook(self, entries: List[Dict[str, Any]]) -> str:
        """
        Generate logbook summary.
        
        Args:
            entries: List of logbook entries
            
        Returns:
            Summary string
        """
        if not entries:
            return "No logbook entries."
        
        types = defaultdict(int)
        for entry in entries:
            etype = entry.get("entry_type", "unknown")
            types[etype] += 1
        
        parts = [f"Logbook Entries: {len(entries)}"]
        for etype, count in types.items():
            parts.append(f"{etype}: {count}")
        
        return ". ".join(parts)
    
    def summarize_knowledge(self, documents: List[Dict[str, Any]]) -> str:
        """
        Generate knowledge summary.
        
        Args:
            documents: List of knowledge documents
            
        Returns:
            Summary string
        """
        if not documents:
            return "No related documents."
        
        types = defaultdict(int)
        for doc in documents:
            dtype = doc.get("document_type", "unknown")
            types[dtype] += 1
        
        parts = [f"Related Documents: {len(documents)}"]
        for dtype, count in types.items():
            parts.append(f"{dtype}: {count}")
        
        return ". ".join(parts)
    
    def generate_context(
        self,
        query: str,
        context_bundle: ContextBundle
    ) -> CopilotAnswer:
        """
        Generate deterministic response based on context.
        
        NOTE: This is placeholder logic.
        NO LLM integration yet.
        Responses are deterministic templates.
        
        Args:
            query: User query
            context_bundle: Context bundle
            
        Returns:
            CopilotAnswer with deterministic response
        """
        # Deterministic template-based response
        answer_parts = []
        sources = []
        context_used = []
        
        # Build response based on query type
        query_lower = query.lower()
        
        if "health" in query_lower:
            if context_bundle.health:
                answer_parts.append(self.summarize_health(context_bundle.health))
                context_used.append("health")
                sources.append("Health Engine")
            else:
                answer_parts.append("No health data available for this entity.")
        
        if "event" in query_lower:
            if context_bundle.events:
                answer_parts.append(self.summarize_events(context_bundle.events))
                context_used.append("events")
                sources.append("Event Engine")
            else:
                answer_parts.append("No events recorded for this entity.")
        
        if "asset" in query_lower:
            if context_bundle.asset:
                answer_parts.append(self.summarize_asset(context_bundle.asset))
                context_used.append("asset")
                sources.append("Asset Engine")
            else:
                answer_parts.append("No asset data available.")
        
        if "timeline" in query_lower:
            if context_bundle.timeline:
                answer_parts.append(self.summarize_timeline(context_bundle.timeline))
                context_used.append("timeline")
                sources.append("Timeline Engine")
            else:
                answer_parts.append("No timeline data available.")
        
        if "logbook" in query_lower:
            if context_bundle.logbook:
                answer_parts.append(self.summarize_logbook(context_bundle.logbook))
                context_used.append("logbook")
                sources.append("Digital Logbook")
            else:
                answer_parts.append("No logbook entries for this entity.")
        
        if "knowledge" in query_lower or "document" in query_lower:
            if context_bundle.knowledge:
                answer_parts.append(self.summarize_knowledge(context_bundle.knowledge))
                context_used.append("knowledge")
                sources.append("Knowledge Repository")
            else:
                answer_parts.append("No related documents found.")
        
        # If no specific match, provide general context
        if not answer_parts:
            answer_parts.append(context_bundle.summary)
            if context_bundle.asset:
                context_used.append("asset")
                sources.append("Asset Engine")
        
        # Generate suggestions
        suggestions = self._generate_suggestions(context_bundle)
        
        return CopilotAnswer(
            answer=" ".join(answer_parts),
            context_used=context_used,
            sources=sources,
            suggestions=suggestions
        )
    
    def _generate_suggestions(self, bundle: ContextBundle) -> List[str]:
        """Generate deterministic suggestions."""
        suggestions = []
        
        if bundle.health:
            health_status = bundle.health.get("health_status", "")
            if health_status == "CRITICAL":
                suggestions.append("Review critical health alerts")
                suggestions.append("Check dependency chain")
            elif health_status == "DEGRADED":
                suggestions.append("Monitor health trend")
                suggestions.append("Review recent events")
        
        if bundle.events:
            suggestions.append("Review active events")
            if len(bundle.events) > 5:
                suggestions.append("Prioritize critical events")
        
        if bundle.knowledge:
            suggestions.append("Review related documentation")
        
        return suggestions[:3]  # Limit to 3 suggestions


# Global instance
copilot_service = CopilotService()
