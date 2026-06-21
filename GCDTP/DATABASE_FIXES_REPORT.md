# Database Migration Fixes Report

## Summary
Fixed 4 critical database migration issues that prevented PostgreSQL from starting.

## Issues Resolved

### 1. Missing schema_migrations Table (Multiple Files)
**Problem:** Migration scripts referenced `schema_migrations` table that didn't exist.
**Fix:** Added schema_migrations table creation to `001_create_asset_table.sql`:
```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(10) NOT NULL UNIQUE,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO schema_migrations (version) VALUES ('001') ON CONFLICT (version) DO NOTHING;
```
**Files Fixed:** `001_create_asset_table.sql`

### 2. Recursive CTE Type Mismatch (021_create_ontology_tables.sql)
**Problem:** Recursive common table expressions had type mismatches between non-recursive and recursive parts.
**Error:** `recursive query "class_tree" column 8 has type character varying(255)[] in non-recursive term but type character varying[] overall`
**Fix:** Cast arrays explicitly to `text[]` type:
```sql
-- Non-recursive term
ARRAY[c.name]::text[] as hierarchy
-- Recursive term  
ct.hierarchy || ARRAY[c.name]::text[]
```
**Files Fixed:** `021_create_ontology_tables.sql` (2 CTEs: class_tree, capability_tree)

### 3. Reserved Keyword Usage (039_create_timeline_snapshots.sql, 040_create_logbook_tables.sql)
**Problem:** `timestamp` is a reserved keyword in PostgreSQL, used as column name in function RETURN TABLE clauses.
**Error:** `syntax error at or near "timestamp"`
**Fix:** Quoted reserved keyword in function return types:
```sql
RETURNS TABLE (
    id UUID,
    "timestamp" TIMESTAMP WITH TIME ZONE,
    ...
)
```
**Files Fixed:** 
- `039_create_timeline_snapshots.sql`
- `040_create_logbook_tables.sql`

### 4. Ambiguous Column Reference (046_create_root_cause_analysis.sql)
**Problem:** `created_at` column reference was ambiguous in GROUP BY query.
**Error:** `column reference "created_at" is ambiguous`
**Fix:** Qualify column with table alias:
```sql
MIN(rca.created_at) as first_analysis,
MAX(rca.created_at) as last_analysis
```
**Files Fixed:** `046_create_root_cause_analysis.sql`

## Verification Results
- All 9 containers running successfully
- PostgreSQL healthy and accepting connections
- Backend API responding (health check passing)
- All migrations executed without errors

## Files Modified
1. `/database/migrations/001_create_asset_table.sql`
2. `/database/migrations/021_create_ontology_tables.sql`
3. `/database/migrations/039_create_timeline_snapshots.sql`
4. `/database/migrations/040_create_logbook_tables.sql`
5. `/database/migrations/046_create_root_cause_analysis.sql`
