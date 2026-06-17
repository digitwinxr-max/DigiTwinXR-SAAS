# Database

This directory contains database schemas, migrations, and initialization scripts.

## Structure

```
database/
├── migrations/        # Database migration files
├── schemas/           # Schema definitions
├── seeds/             # Seed data for testing
├── init/              # Docker initialization scripts
└── docker-entrypoint-initdb.d/  # PostgreSQL init scripts
```

## Asset Schema

The core asset table stores all asset-related data:

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Asset name |
| asset_type | VARCHAR(100) | Type of asset |
| description | TEXT | Asset description |
| longitude | FLOAT | Geographic longitude |
| latitude | FLOAT | Geographic latitude |
| status | VARCHAR(50) | Current status |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

## Getting Started

```bash
# Apply migrations
psql -h localhost -U postgres -d gcdtp -f migrations/001_create_asset_table.sql
```

## Migrations

- `001_create_asset_table.sql` - Initial asset table schema

## Seeds

*(Define seed data before use)*
