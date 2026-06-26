"""
Replay Engine

Provides Digital Twin Time Machine capability.
Enables playback of recorded timelines with speed control and branching.
"""

import uuid
import time
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from backend.src.services.timeline.timeline_types import (
    ReplaySession,
    ReplayState,
    TimelineSegment,
    TimelineEvent,
    TimelineSnapshot,
)


class ReplayEngine:
    """
    Provides time-travel replay capability.
    
    Features:
    - Play, pause, resume, stop
    - Speed control (0.25x to 100x)
    - Seek to timestamp
    - Step forward/backward
    - Branching for alternative histories
    - Deterministic replay
    """
    
    AVAILABLE_SPEEDS = [0.25, 0.5, 1.0, 2.0, 10.0, 100.0]
    
    def __init__(self):
        self.current_session: Optional[ReplaySession] = None
        self._playback_thread: Optional[Any] = None
        self._is_playing = False
        self._callbacks: Dict[str, Callable] = {}
    
    def create_session(
        self,
        segment: TimelineSegment,
        speed: float = 1.0,
        is_branch: bool = False,
        parent_session_id: Optional[str] = None,
        branch_point: Optional[datetime] = None
    ) -> ReplaySession:
        """
        Create a new replay session.
        
        Args:
            segment: Timeline segment to replay
            speed: Playback speed
            is_branch: Whether this is a branch session
            parent_session_id: Parent session ID for branches
            branch_point: Branch point timestamp
            
        Returns:
            Created ReplaySession
        """
        session = ReplaySession(
            session_id=str(uuid.uuid4()),
            timeline_segment=segment,
            speed=speed,
            current_index=0,
            current_time=segment.start_time if segment.events else None,
            state=ReplayState.IDLE,
            is_branch=is_branch,
            parent_session_id=parent_session_id,
            branch_point=branch_point
        )
        
        self.current_session = session
        return session
    
    def play(self) -> bool:
        """
        Start playback.
        
        Returns:
            True if started successfully
        """
        if not self.current_session:
            return False
        
        if self.current_session.state == ReplayState.PLAYING:
            return True
        
        self.current_session.state = ReplayState.PLAYING
        self._is_playing = True
        
        self._trigger_callback("on_play", self.current_session)
        return True
    
    def pause(self) -> bool:
        """Pause playback."""
        if not self.current_session:
            return False
        
        if self.current_session.state != ReplayState.PLAYING:
            return False
        
        self.current_session.state = ReplayState.PAUSED
        self._is_playing = False
        
        self._trigger_callback("on_pause", self.current_session)
        return True
    
    def resume(self) -> bool:
        """Resume playback."""
        if not self.current_session:
            return False
        
        if self.current_session.state != ReplayState.PAUSED:
            return False
        
        return self.play()
    
    def stop(self) -> bool:
        """Stop playback."""
        if not self.current_session:
            return False
        
        self._is_playing = False
        self.current_session.state = ReplayState.STOPPED
        
        self._trigger_callback("on_stop", self.current_session)
        return True
    
    def seek(self, timestamp: datetime) -> bool:
        """
        Seek to a specific timestamp.
        
        Args:
            timestamp: Target timestamp
            
        Returns:
            True if seek successful
        """
        if not self.current_session:
            return False
        
        events = self.current_session.timeline_segment.events
        
        # Find event index for timestamp
        for i, event in enumerate(events):
            if event.timestamp >= timestamp:
                self.current_session.current_index = i
                self.current_session.current_time = event.timestamp
                self._trigger_callback("on_seek", self.current_session)
                return True
        
        # If past all events, go to end
        if events:
            self.current_session.current_index = len(events) - 1
            self.current_session.current_time = events[-1].timestamp
        
        self._trigger_callback("on_seek", self.current_session)
        return True
    
    def seek_to_index(self, index: int) -> bool:
        """
        Seek to a specific event index.
        
        Args:
            index: Target event index
            
        Returns:
            True if seek successful
        """
        if not self.current_session:
            return False
        
        events = self.current_session.timeline_segment.events
        
        if index < 0 or index >= len(events):
            return False
        
        self.current_session.current_index = index
        self.current_session.current_time = events[index].timestamp
        
        self._trigger_callback("on_seek", self.current_session)
        return True
    
    def step_forward(self) -> Optional[TimelineEvent]:
        """
        Step forward one event.
        
        Returns:
            Next event or None
        """
        if not self.current_session:
            return None
        
        events = self.current_session.timeline_segment.events
        
        if self.current_session.current_index >= len(events) - 1:
            return None
        
        self.current_session.current_index += 1
        event = events[self.current_session.current_index]
        self.current_session.current_time = event.timestamp
        
        self._trigger_callback("on_step", self.current_session, event)
        return event
    
    def step_backward(self) -> Optional[TimelineEvent]:
        """
        Step backward one event.
        
        Returns:
            Previous event or None
        """
        if not self.current_session:
            return None
        
        events = self.current_session.timeline_segment.events
        
        if self.current_session.current_index <= 0:
            return None
        
        self.current_session.current_index -= 1
        event = events[self.current_session.current_index]
        self.current_session.current_time = event.timestamp
        
        self._trigger_callback("on_step", self.current_session, event)
        return event
    
    def change_speed(self, speed: float) -> bool:
        """
        Change playback speed.
        
        Args:
            speed: New speed (must be in AVAILABLE_SPEEDS)
            
        Returns:
            True if speed changed
        """
        if speed not in self.AVAILABLE_SPEEDS:
            return False
        
        if not self.current_session:
            return False
        
        self.current_session.speed = speed
        self._trigger_callback("on_speed_change", self.current_session)
        return True
    
    def get_current_event(self) -> Optional[TimelineEvent]:
        """Get current event."""
        if not self.current_session:
            return None
        
        events = self.current_session.timeline_segment.events
        
        if not events or self.current_session.current_index >= len(events):
            return None
        
        return events[self.current_session.current_index]
    
    def get_events_up_to(self, index: Optional[int] = None) -> List[TimelineEvent]:
        """Get all events up to current position."""
        if not self.current_session:
            return []
        
        events = self.current_session.timeline_segment.events
        target_index = index if index is not None else self.current_session.current_index
        
        return events[:target_index + 1]
    
    def get_events_after(self, index: Optional[int] = None) -> List[TimelineEvent]:
        """Get all events after current position."""
        if not self.current_session:
            return []
        
        events = self.current_session.timeline_segment.events
        target_index = index if index is not None else self.current_session.current_index
        
        return events[target_index + 1:]
    
    def create_branch(
        self,
        branch_name: str,
        from_timestamp: Optional[datetime] = None
    ) -> Optional[ReplaySession]:
        """
        Create a branch session for alternative history.
        
        Args:
            branch_name: Name for the branch
            from_timestamp: Start branch from this timestamp
            
        Returns:
            New branch session or None
        """
        if not self.current_session:
            return None
        
        # Find branch point
        branch_point = from_timestamp or self.current_session.current_time
        
        if not self.current_session.timeline_segment.events:
            return None
        
        # Find events before branch point
        branch_events = [
            e for e in self.current_session.timeline_segment.events
            if e.timestamp < branch_point
        ]
        
        # Create new segment
        segment = TimelineSegment(
            segment_id=f"branch-{branch_name}",
            start_time=branch_point,
            end_time=self.current_session.timeline_segment.end_time,
            events=branch_events
        )
        
        return self.create_session(
            segment=segment,
            is_branch=True,
            parent_session_id=self.current_session.session_id,
            branch_point=branch_point
        )
    
    def get_session_state(self) -> Dict:
        """Get current session state."""
        if not self.current_session:
            return {
                "active": False,
                "session": None
            }
        
        session = self.current_session
        
        return {
            "active": True,
            "session_id": session.session_id,
            "state": session.state.value,
            "speed": session.speed,
            "current_index": session.current_index,
            "current_time": session.current_time.isoformat() if session.current_time else None,
            "total_events": session.total_events,
            "progress": session.progress,
            "is_complete": session.is_complete,
            "is_branch": session.is_branch,
            "parent_session_id": session.parent_session_id,
        }
    
    def on(self, event_name: str, callback: Callable) -> None:
        """Register a callback for playback events."""
        self._callbacks[event_name] = callback
    
    def _trigger_callback(self, event_name: str, *args) -> None:
        """Trigger a registered callback."""
        if event_name in self._callbacks:
            try:
                self._callbacks[event_name](*args)
            except Exception:
                pass  # Don't let callback errors break playback
    
    def get_next_events(self, count: int = 1) -> List[TimelineEvent]:
        """Get next N events without advancing position."""
        if not self.current_session:
            return []
        
        events = self.current_session.timeline_segment.events
        start = self.current_session.current_index + 1
        end = min(start + count, len(events))
        
        return events[start:end]
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for replay to complete.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if completed, False if timeout
        """
        if not self.current_session:
            return True
        
        start_time = time.time()
        
        while self._is_playing:
            if self.current_session.is_complete:
                return True
            
            if timeout and (time.time() - start_time) > timeout:
                return False
            
            time.sleep(0.1)
        
        return True


class DeterministicReplayEngine(ReplayEngine):
    """
    Replay engine with deterministic playback guarantee.
    
    Same input always produces same output.
    """
    
    def __init__(self):
        super().__init__()
        self._seed = None
    
    def set_seed(self, seed: int) -> None:
        """Set random seed for deterministic replay."""
        self._seed = seed
        import random
        random.seed(seed)
    
    def create_session(
        self,
        segment: TimelineSegment,
        speed: float = 1.0,
        is_branch: bool = False,
        parent_session_id: Optional[str] = None,
        branch_point: Optional[datetime] = None
    ) -> ReplaySession:
        """Create session with deterministic ordering."""
        session = super().create_session(
            segment=segment,
            speed=speed,
            is_branch=is_branch,
            parent_session_id=parent_session_id,
            branch_point=branch_point
        )
        
        # Sort events by timestamp for deterministic order
        session.timeline_segment.events.sort(key=lambda e: (e.timestamp, e.event_id))
        
        return session
