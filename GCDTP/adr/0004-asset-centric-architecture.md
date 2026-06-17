# ADR-0004: Asset-Centric Architecture

## Status

Accepted

## Context

GCDTP (Generic Component-Driven Template Project) requires a core entity around which all functionality revolves. Assets serve as the central domain object that can be extended with sensors, events, and other components in future iterations.

## Decision

We adopt an asset-centric architecture where:
1. **Assets are the primary domain entity** - All operations, extensions, and integrations center on assets
2. **Assets have a well-defined schema** with essential attributes for identification, categorization, location, and status
3. **Asset CRUD operations** are provided via REST API endpoints
4. **The frontend** is organized around asset management views

## Asset Schema

```sql
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(100) NOT NULL,
    description TEXT,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## API Design

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /assets | Create a new asset |
| GET | /assets | List all assets (paginated) |
| GET | /assets/{id} | Get asset by ID |
| PUT | /assets/{id} | Update an asset |
| DELETE | /assets/{id} | Delete an asset |

## Architecture Layers

```
┌─────────────────────────────────────┐
│           Frontend (React)          │
│  ┌─────────────────────────────┐   │
│  │  Asset List  │  Asset Form │   │
│  └─────────────────────────────┘   │
├─────────────────────────────────────┤
│         Backend API (FastAPI)      │
│  ┌─────────────────────────────┐   │
│  │ Routes → Services → Models │   │
│  └─────────────────────────────┘   │
├─────────────────────────────────────┤
│         Database (PostgreSQL)      │
│         ┌─────────────────┐        │
│         │  assets table   │        │
│         └─────────────────┘        │
└─────────────────────────────────────┘
```

## Decision Made By

GCDTP Core Team

## Date

2026-06-16

## Consequences

### Positive
- Clear primary entity provides focus for development
- Simple, well-defined schema enables rapid iteration
- Extensible design allows adding related entities (sensors, events) later
- Clean separation between frontend, backend, and database layers
- Testable architecture with clear boundaries

### Negative
- Initial scope limited to asset management only
- May require refactoring if asset model needs significant changes

### Neutral
- Asset-centric design is common in IoT and tracking applications
- PostgreSQL provides solid foundation for future TimescaleDB migration if needed

## Future Extensions

This architecture intentionally leaves space for:
- Sensors attached to assets
- Events triggered by assets
- Time-series data (TimescaleDB)
- Authentication/authorization
- Additional API endpoints for specialized queries
