"""
Timeline Module

Operational timeline and digital twin time machine.
Provides event recording, snapshot capture, replay, and query capabilities.
"""

from .timeline_types import (
    TimelineEvent,
    TimelineSnapshot,
    TopologySnapshot,
    TimelineSegment,
    ReplaySession,
    DiffResult,
    TimelineQuery,
    Timeline,
    AssetState,
    FlowState,
    ResilienceState,
    Severity,
    TimelineEventType,
    ReplayState,
    DiffType,
)

from .event_recorder import EventRecorder
from .snapshot_manager import SnapshotManager
from .timeline_engine import TimelineEngine
from .replay_engine import ReplayEngine, DeterministicReplayEngine
from .timeline_query_engine import TimelineQueryEngine
from .diff_engine import DiffEngine
from .timeline_validator import TimelineValidator


__all__ = [
    # Types
    "TimelineEvent",
    "TimelineSnapshot",
    "TopologySnapshot",
    "TimelineSegment",
    "ReplaySession",
    "DiffResult",
    "TimelineQuery",
    "Timeline",
    "AssetState",
    "FlowState",
    "ResilienceState",
    # Enums
    "Severity",
    "TimelineEventType",
    "ReplayState",
    "DiffType",
    # Engines
    "EventRecorder",
    "SnapshotManager",
    "TimelineEngine",
    "ReplayEngine",
    "DeterministicReplayEngine",
    "TimelineQueryEngine",
    "DiffEngine",
    "TimelineValidator",
]
