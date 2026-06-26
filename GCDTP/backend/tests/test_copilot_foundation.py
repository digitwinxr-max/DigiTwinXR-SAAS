"""
Tests for Cognitive Copilot Foundation

Tests session creation, message storage, 
context bundle generation, and history retrieval.
"""

import pytest
from datetime import datetime
from src.models.copilot_session import CopilotSession
from src.models.copilot_message import CopilotMessage, MessageRole
from src.services.copilot_service import CopilotService
from src.schemas.copilot import ContextBundle


class TestCopilotSession:
    """Tests for copilot session operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = CopilotService()
    
    def test_create_session(self):
        """Test creating a copilot session."""
        session = self.service.create_session("Test Session")
        
        assert session is not None
        assert session.session_name == "Test Session"
        assert session.message_count == 0
    
    def test_get_session(self):
        """Test getting a session by ID."""
        created = self.service.create_session("Test")
        retrieved = self.service.get_session(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
    
    def test_get_all_sessions(self):
        """Test getting all sessions."""
        self.service.create_session("Session 1")
        self.service.create_session("Session 2")
        self.service.create_session("Session 3")
        
        sessions = self.service.get_all_sessions()
        assert len(sessions) == 3


class TestCopilotMessage:
    """Tests for copilot message operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = CopilotService()
        self.session = self.service.create_session("Test Session")
    
    def test_add_user_message(self):
        """Test adding a user message."""
        message = self.service.add_message(
            session_id=self.session.id,
            role="user",
            message="What is the health status?"
        )
        
        assert message is not None
        assert message.role == MessageRole.USER
        assert message.message == "What is the health status?"
    
    def test_add_assistant_message(self):
        """Test adding an assistant message."""
        message = self.service.add_message(
            session_id=self.session.id,
            role="assistant",
            message="The health status is healthy."
        )
        
        assert message is not None
        assert message.role == MessageRole.ASSISTANT
    
    def test_add_message_with_context(self):
        """Test adding a message with context data."""
        context = {"health_score": 95, "status": "healthy"}
        
        message = self.service.add_message(
            session_id=self.session.id,
            role="assistant",
            message="Health is good.",
            context_data=context
        )
        
        assert message is not None
        assert message.context_data == context
    
    def test_get_messages(self):
        """Test getting all messages in a session."""
        self.service.add_message(self.session.id, "user", "Query 1")
        self.service.add_message(self.session.id, "assistant", "Response 1")
        self.service.add_message(self.session.id, "user", "Query 2")
        
        messages = self.service.get_messages(self.session.id)
        assert len(messages) == 3
    
    def test_message_order(self):
        """Test that messages are ordered by timestamp."""
        self.service.add_message(self.session.id, "user", "First")
        self.service.add_message(self.session.id, "user", "Second")
        self.service.add_message(self.session.id, "user", "Third")
        
        messages = self.service.get_messages(self.session.id)
        assert messages[0].message == "First"
        assert messages[1].message == "Second"
        assert messages[2].message == "Third"


class TestContextBundle:
    """Tests for context bundle generation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = CopilotService()
    
    def test_build_empty_bundle(self):
        """Test building an empty context bundle."""
        bundle = self.service.build_context_bundle("asset", "test-asset")
        
        assert bundle.entity_type == "asset"
        assert bundle.entity_id == "test-asset"
        assert bundle.summary is not None
    
    def test_build_bundle_with_data(self):
        """Test building bundle with provided data."""
        context_data = {
            "asset": {"name": "Test Asset", "status": "healthy"},
            "health": {"health_score": 95},
            "events": [{"id": "1", "message": "Event 1"}]
        }
        
        bundle = self.service.build_context_bundle(
            entity_type="asset",
            entity_id="test-asset",
            context_data=context_data
        )
        
        assert bundle.asset is not None
        assert bundle.asset["name"] == "Test Asset"
        assert bundle.health is not None
        assert bundle.health["health_score"] == 95
        assert len(bundle.events) == 1


class TestSummaries:
    """Tests for summary generation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = CopilotService()
    
    def test_summarize_asset(self):
        """Test asset summary generation."""
        asset_data = {
            "name": "Substation Alpha",
            "status": "healthy",
            "category": "power",
            "location": "Building A"
        }
        
        summary = self.service.summarize_asset(asset_data)
        
        assert "Substation Alpha" in summary
        assert "healthy" in summary
        assert "power" in summary
    
    def test_summarize_health(self):
        """Test health summary generation."""
        health_data = {
            "health_status": "HEALTHY",
            "health_score": 95,
            "dependency_penalty": 2.5
        }
        
        summary = self.service.summarize_health(health_data)
        
        assert "HEALTHY" in summary
        assert "95" in summary
    
    def test_summarize_events(self):
        """Test events summary generation."""
        events = [
            {"severity": "WARNING", "message": "Warning event"},
            {"severity": "CRITICAL", "message": "Critical event"},
            {"severity": "WARNING", "message": "Another warning"}
        ]
        
        summary = self.service.summarize_events(events)
        
        assert "3" in summary
        assert "Critical: 1" in summary
        assert "Warning: 2" in summary
    
    def test_summarize_empty_events(self):
        """Test events summary with no events."""
        summary = self.service.summarize_events([])
        assert "No active events" in summary


class TestGenerateContext:
    """Tests for context generation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = CopilotService()
    
    def test_generate_health_response(self):
        """Test generating response about health."""
        bundle = self.service.build_context_bundle(
            entity_type="asset",
            entity_id="test",
            context_data={
                "health": {
                    "health_status": "HEALTHY",
                    "health_score": 95
                }
            }
        )
        
        answer = self.service.generate_context(
            "What is the health status?",
            bundle
        )
        
        assert "HEALTHY" in answer.answer
        assert "health" in answer.context_used
        assert "Health Engine" in answer.sources
    
    def test_generate_event_response(self):
        """Test generating response about events."""
        bundle = self.service.build_context_bundle(
            entity_type="asset",
            entity_id="test",
            context_data={
                "events": [
                    {"severity": "WARNING", "message": "Test event"}
                ]
            }
        )
        
        answer = self.service.generate_context(
            "Show me events",
            bundle
        )
        
        assert "event" in answer.answer.lower()
        assert "events" in answer.context_used
    
    def test_suggestions_generated(self):
        """Test that suggestions are generated."""
        bundle = self.service.build_context_bundle(
            entity_type="asset",
            entity_id="test",
            context_data={
                "health": {"health_status": "CRITICAL"}
            }
        )
        
        answer = self.service.generate_context(
            "What is the health?",
            bundle
        )
        
        assert len(answer.suggestions) > 0


class TestHistory:
    """Tests for session history."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = CopilotService()
        self.session = self.service.create_session("History Test")
    
    def test_history_retrieval(self):
        """Test retrieving session history."""
        self.service.add_message(self.session.id, "user", "Query 1")
        self.service.add_message(self.session.id, "assistant", "Response 1")
        self.service.add_message(self.session.id, "user", "Query 2")
        
        messages = self.service.get_messages(self.session.id)
        
        assert len(messages) == 3
        assert messages[0].message == "Query 1"
        assert messages[1].message == "Response 1"
        assert messages[2].message == "Query 2"
    
    def test_session_updates_activity(self):
        """Test that session activity is updated."""
        session = self.service.get_session(self.session.id)
        initial_count = session.message_count
        
        self.service.add_message(self.session.id, "user", "New message")
        
        updated = self.service.get_session(self.session.id)
        assert updated.message_count == initial_count + 1
