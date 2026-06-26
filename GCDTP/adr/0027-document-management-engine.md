# ADR-0027: Document Management Engine

## Status

Accepted

## Context

After implementing the Work Order Engine (ADR-0026), GCDTP has comprehensive maintenance tracking. However, there is no mechanism to store and manage documents related to assets and work orders.

### The Gap

```
Asset
    ↓
Work Order
    ↓
(no document management)
    ↓
Reports, manuals, forms stored externally...
```

### The Need

We need to store and manage:

```
Asset
    ↓
Documents
    ↓
Work Orders
    ↓
Timeline
```

This creates a complete asset documentation system.

## Decision

Create the Document Management Engine:

```
backend/src/services/documents/
├── document_types.py       # Core types
├── document_engine.py      # Main engine
├── document_indexer.py     # Pure Python search
├── attachment_manager.py   # File management
├── document_validator.py   # Validation
└── __init__.py
```

## Core Types

### Document

```python
@dataclass
class Document:
    id: str
    title: str
    document_type: DocumentType
    description: str
    
    # Linkages
    asset_id: Optional[str]
    work_order_id: Optional[str]
    
    # File info
    file_name: str
    mime_type: str
    file_size: int
    storage_path: str
    checksum: str
    
    # Versioning
    version: int
    
    # Status
    status: DocumentStatus
```

### DocumentType

```python
class DocumentType(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    REPORT = "report"
    MANUAL = "manual"
    DRAWING = "drawing"
    INSPECTION_FORM = "inspection_form"
    MAINTENANCE_REPORT = "maintenance_report"
    VIDEO_METADATA = "video_metadata"
    CERTIFICATE = "certificate"
    CONTRACT = "contract"
    OTHER = "other"
```

### DocumentStatus

```python
class DocumentStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
```

## Workflows

### Document Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT LIFECYCLE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CREATE ──→ ACTIVE ──→ ARCHIVED ──→ (restore) ──→ ACTIVE        │
│     │         │                                                │
│     │         ▼                                                │
│     └─────→ DELETED ──→ (restore) ──→ ACTIVE                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Version Control

```
Document v1
    │
    └── Update ──→ Document v2
                      │
                      └── Update ──→ Document v3
                                         │
                          Version History: v1, v2, v3
```

## Database Schema

### documents table

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    asset_id UUID REFERENCES assets(id),
    work_order_id UUID REFERENCES work_orders(id),
    title VARCHAR(255) NOT NULL,
    document_type document_type NOT NULL,
    file_name VARCHAR(255),
    mime_type VARCHAR(100),
    file_size BIGINT,
    storage_path VARCHAR(500),
    version INTEGER DEFAULT 1,
    status document_status DEFAULT 'active',
    checksum VARCHAR(64),
    uploaded_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    archived_at TIMESTAMP,
    deleted_at TIMESTAMP,
    metadata JSONB
);
```

### document_versions table

```sql
CREATE TABLE document_versions (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    version_number INTEGER NOT NULL,
    file_name VARCHAR(255),
    change_notes TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### document_tags table

```sql
CREATE TABLE document_tags (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    tag VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Pure Python Indexer

No external search engine dependencies:

```python
class DocumentIndexer:
    def index_document(self, document, tags)
    def search(self, filter) -> List[DocumentSearchResult]
    def search_by_text(self, text) -> List[Document]
    def search_by_tag(self, tag) -> List[Document]
    def search_by_asset(self, asset_id) -> List[Document]
    def search_by_work_order(self, work_order_id) -> List[Document]
```

Features:
- In-memory indexing
- Full-text search on title/description
- Tag-based filtering
- Relevance scoring
- Date range filtering

## EventBus Integration

The Document Engine publishes events:

- DOCUMENT_CREATED
- DOCUMENT_UPDATED
- DOCUMENT_VERSION_CREATED
- DOCUMENT_ARCHIVED
- DOCUMENT_RESTORED
- DOCUMENT_DELETED

## Validation Rules

### File Type Validation

Supported types:
- PDF, Images (PNG, JPEG, GIF, SVG)
- Documents (DOC, DOCX, XLS, XLSX, PPT, PPTX)
- Text (TXT, CSV)
- Archives (ZIP)
- Videos (MP4, AVI)

### Size Validation

Maximum file size: 100 MB

### Duplicate Detection

Checksum comparison for duplicate content.

## Asset-Centric Design

All documents are linked to assets or work orders:

```
Asset A
    ├── Document #1 (manual)
    ├── Document #2 (certificate)
    └── Document #3 (drawing)

Work Order #1
    ├── Document #4 (inspection form)
    └── Document #5 (maintenance report)
```

This enables:
- Asset documentation history
- Work order evidence
- Compliance documentation
- Training materials

## Consequences

### Positive

1. **Complete documentation** - All assets have documentation
2. **Asset-centric** - Documents linked to assets/work orders
3. **Version control** - Full revision history
4. **Pure Python search** - No external dependencies
5. **Event integration** - Timeline includes document events

### Negative

1. **Storage management** - Actual file storage not implemented
2. **Data entry** - Documents need metadata
3. **Index size** - In-memory index for large document sets

### Neutral

1. **Database migration** - New tables
2. **No external dependencies** - Pure Python
3. **Preserves architecture** - Follows existing patterns

## Acceptance Criteria

- [x] Document creation and management
- [x] Version control
- [x] Asset linkage
- [x] Work order linkage
- [x] Pure Python indexing
- [x] Tagging
- [x] Search
- [x] Validation
- [x] Soft delete
- [x] Restore
- [x] EventBus integration
- [x] Database migration
- [x] 50+ tests
- [x] ADR documentation
