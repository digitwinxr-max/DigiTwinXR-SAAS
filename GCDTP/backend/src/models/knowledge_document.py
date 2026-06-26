"""
Knowledge Document Model

Represents structured knowledge in the repository.
This is metadata only - NO AI, NO embeddings.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


class DocumentType(str, Enum):
    """Types of knowledge documents."""
    MANUAL = "manual"
    SOP = "sop"
    TROUBLESHOOTING = "troubleshooting"
    ADR = "adr"
    REPORT = "report"
    LESSON_LEARNED = "lesson_learned"
    REFERENCE = "reference"
    EXTERNAL = "external"


@dataclass
class KnowledgeDocument:
    """
    Knowledge document in the repository.
    
    This is pure metadata - no AI processing, no embeddings.
    Documents are organized, categorized, and linked.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    document_type: DocumentType = DocumentType.REFERENCE
    category: str = ""
    source: Optional[str] = None
    author: str = ""
    summary: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    external_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "document_type": self.document_type.value if isinstance(self.document_type, Enum) else self.document_type,
            "category": self.category,
            "source": self.source,
            "author": self.author,
            "summary": self.summary,
            "tags": self.tags,
            "external_url": self.external_url,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeDocument":
        """Create from dictionary."""
        doc_type = data.get("document_type")
        if isinstance(doc_type, str):
            doc_type = DocumentType(doc_type)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            document_type=doc_type or DocumentType.REFERENCE,
            category=data.get("category", ""),
            source=data.get("source"),
            author=data.get("author", ""),
            summary=data.get("summary"),
            tags=data.get("tags", []),
            external_url=data.get("external_url"),
            created_at=created_at or datetime.utcnow()
        )
    
    def get_type_icon(self) -> str:
        """Get icon for document type."""
        icons = {
            DocumentType.MANUAL: "📖",
            DocumentType.SOP: "📋",
            DocumentType.TROUBLESHOOTING: "🔧",
            DocumentType.ADR: "📝",
            DocumentType.REPORT: "📊",
            DocumentType.LESSON_LEARNED: "💡",
            DocumentType.REFERENCE: "📚",
            DocumentType.EXTERNAL: "🔗"
        }
        return icons.get(self.document_type, "📄")
    
    def get_category_color(self) -> str:
        """Get color for category."""
        colors = {
            "infrastructure": "#4CAF50",
            "operations": "#2196F3",
            "maintenance": "#FF9800",
            "safety": "#F44336",
            "compliance": "#9C27B0",
            "training": "#00BCD4",
            "architecture": "#795548",
            "general": "#607D8B"
        }
        return colors.get(self.category.lower(), "#9E9E9E")
