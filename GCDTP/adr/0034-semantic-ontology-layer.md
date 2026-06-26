# ADR-0034: Semantic Ontology Layer

## Status

Accepted

## Context

GCDTP needs to provide meaning and classification across all domains:
- Electrical infrastructure
- Water distribution
- Transportation networks
- Buildings
- Telecommunications
- Environment
- Energy systems
- Industrial processes

We need a semantic layer for:
- Classification of entities
- Taxonomy hierarchies
- Capability definitions
- Property inheritance
- Cross-domain relationships

### The Decision

Introduce a **Semantic Ontology Layer** for classification and meaning. **No AI, no inference engines.**

```
┌─────────────────────────────────────────────────────────────────┐
│                    SEMANTIC ONTOLOGY LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    ONTOLOGY ENGINE                         ││
│  │                                                          ││
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ││
│  │  │ Domain  │  │ Class   │  │ Taxonomy│  │Capability│  ││
│  │  │Registry │  │Registry│  │ Engine  │  │ Engine  │  ││
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  ││
│  │                                                          ││
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ││
│  │  │Classify │  │Inherit  │  │ Query   │  │  Sync   │  ││
│  │  │Engine   │  │Engine   │  │ Engine  │  │ Engine  │  ││
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  ││
│  │                                                          ││
│  └─────────────────────────────────────────────────────────┘│
│                                                                  │
│  Sync with: Assets, Documents, Work Orders, Devices, Organizations │
└─────────────────────────────────────────────────────────────────┘
```

## Key Principle

**No AI, no inference engines.** Simple taxonomy and classification only.

## Decision

Create Semantic Ontology Layer:

```
backend/src/ontology/
├── ontology_types.py              # Core types
├── ontology_registry.py           # Domain and class registration
├── taxonomy_engine.py             # Hierarchy management
├── classification_engine.py       # Entity classification
├── inheritance_engine.py         # Property/capability inheritance
├── capability_engine.py          # Capability management
├── semantic_query_engine.py      # Query capabilities
├── ontology_validator.py         # Validation
├── ontology_sync_engine.py       # External sync
└── __init__.py
```

## Supported Domains

| Domain | Description |
|--------|-------------|
| Electrical | Power infrastructure |
| Water | Water distribution |
| Transport | Transportation networks |
| Buildings | Building systems |
| Telecommunications | Communication |
| Environment | Environmental monitoring |
| Energy | Energy systems |
| Industrial | Industrial processes |
| Custom | User-defined |

## Ontology Structure

### Domains
- Top-level classification containers
- Support for hierarchy (parent domains)
- Domain-specific taxonomies

### Classes
- Belong to a domain
- Support hierarchy (parent classes)
- Properties and capabilities
- Abstract or concrete

### Relationships
- Connect classes
- Cardinality support
- Directionality
- Inverse relationships

## Engine Capabilities

### Taxonomy Engine
- Class hierarchy management
- Subclass traversal
- Parent class lookup
- Taxonomy traversal

### Classification Engine
- Asset classification
- Document classification
- Work order classification
- Device classification
- Organization classification

### Inheritance Engine
- Property inheritance
- Capability inheritance
- Taxonomy inheritance
- Semantic propagation

### Capability Engine
- Capability lookup
- Shared capabilities
- Cross-domain capabilities
- Dependency capabilities

### Semantic Query Engine
- Find by class
- Find by capability
- Find related classes
- Taxonomy traversal
- Ancestor/descendant lookup

## Database Schema

### ontology_domains

```sql
CREATE TABLE ontology_domains (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    display_name VARCHAR(255),
    domain_type ontology_domain
);
```

### ontology_classes

```sql
CREATE TABLE ontology_classes (
    id UUID PRIMARY KEY,
    domain_id UUID,
    name VARCHAR(255),
    parent_class_id UUID,
    level INTEGER,
    path VARCHAR(1000),
    properties JSONB,
    capabilities JSONB,
    is_abstract BOOLEAN
);
```

## EventBus Integration

Ontology events published to Timeline Engine:

- ONTOLOGY_CLASS_CREATED
- ONTOLOGY_UPDATED
- SEMANTIC_TAG_ASSIGNED
- CLASSIFICATION_UPDATED
- ONTOLOGY_SYNC_COMPLETED

## Consequences

### Positive

1. **Classification** - Meaningful entity classification
2. **Taxonomy** - Hierarchical organization
3. **Capabilities** - Define what entities can do
4. **Inheritance** - Reduce duplication
5. **No AI** - Simple, predictable behavior

### Negative

1. **Complexity** - Additional layer to manage
2. **Maintenance** - Keep ontology up-to-date
3. **Sync** - External entity sync required

### Neutral

1. **PostgreSQL authoritative** - No business logic changes
2. **Additive only** - Existing features unchanged
3. **Simple semantics** - No inference complexity

## Acceptance Criteria

- [x] Ontology registry
- [x] Taxonomy engine
- [x] Classification engine
- [x] Inheritance engine
- [x] Capability engine
- [x] Semantic query engine
- [x] Ontology validator
- [x] Ontology sync engine
- [x] All supported domains
- [x] EventBus integration
- [x] Timeline integration
- [x] Database migration
- [x] 75+ tests
- [x] ADR documentation
