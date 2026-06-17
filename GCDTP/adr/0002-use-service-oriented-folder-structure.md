# ADR-0002: Use Service-Oriented Folder Structure

## Status

Accepted

## Context

GCDTP needs a folder structure that supports multiple services/components while maintaining clarity and separation of concerns. The structure should accommodate growth without requiring major refactoring.

## Decision

We will use a service-oriented folder structure with the following top-level directories:
- `adr/` - Architecture Decision Records
- `backend/` - Backend services and logic
- `database/` - Database schemas and migrations
- `frontend/` - Frontend application code
- `tests/` - Test suites and fixtures

## Decision Made By

*(Define before use)*

## Date

*(Define before use)*

## Consequences

### Positive
- Clear ownership of each folder
- Easy to locate files based on their purpose
- Supports parallel development across teams
- Scales well with project growth

### Negative
- May require additional coordination for cross-cutting concerns

### Neutral
- Standard structure that aligns with industry practices
