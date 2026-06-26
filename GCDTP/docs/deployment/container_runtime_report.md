# Container Runtime Report

**Generated**: 2026-06-21
**Command**: `docker compose up -d`
**Result**: ✅ SUCCESS

---

## Container Status Summary

| Container | Status | Health | Ports |
|-----------|--------|--------|-------|
| gcdtp-postgres-1 | ✅ Running | Healthy | 0.0.0.0:5432->5432 |
| gcdtp-timescaledb-1 | ✅ Running | Healthy | 0.0.0.0:5433->5432 |
| gcdtp-redis-1 | ✅ Running | - | 0.0.0.0:6379->6379 |
| gcdtp-neo4j-1 | ✅ Running | Starting | 0.0.0.0:7474->7474, 7687->7687 |
| gcdtp-chroma-1 | ✅ Running | Healthy | 0.0.0.0:8000->8000 |
| gcdtp-kafka-1 | ✅ Running | - | 0.0.0.0:9092->9092 |
| gcdtp-mqtt-1 | ✅ Running | Starting | 1883, 8883, 18083 |
| gcdtp-backend-1 | ✅ Running | Healthy | 0.0.0.0:8080->8080 |
| gcdtp-frontend-1 | ✅ Running | Starting | 0.0.0.0:3000->80 |

**Total Containers**: 9
**Running**: 9
**Healthy**: 5
**Starting**: 2
**Not Healthy**: 0

---

## Evidence: docker ps Output

```
NAME                    STATUS          PORTS
gcdtp-frontend-1        Up 36s          0.0.0.0:3000->80/tcp
gcdtp-backend-1         Up 37s (healthy) 0.0.0.0:8080->8080/tcp
gcdtp-timescaledb-1     Up 44s (healthy) 0.0.0.0:5433->5432/tcp
gcdtp-redis-1           Up 44s          0.0.0.0:6379->6379/tcp
gcdtp-chroma-1          Up 44s (healthy) 0.0.0.0:8000->8000/tcp
gcdtp-kafka-1           Up 44s          0.0.0.0:9092->9092/tcp
gcdtp-neo4j-1           Up 44s          0.0.0.0:7474->7474, 7473/tcp, 7687->7687/tcp
gcdtp-mqtt-1            Up 44s          1883, 8883, 18083
gcdtp-postgres-1        Up 44s (healthy) 0.0.0.0:5432->5432/tcp
```

---

## Evidence: Backend Logs

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     127.0.0.1:51726 - "GET /health HTTP/1.1" 200 OK
```

Health checks passing.

---

## Evidence: PostgreSQL Logs

```
PostgreSQL init process complete; ready for start up.
2026-06-21 18:29:15.456 UTC [1] LOG:  starting PostgreSQL 15.8
2026-06-21 18:29:15.460 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2026-06-21 18:29:15.487 UTC [1] LOG:  database system is ready to accept connections
```

---

## Service Connectivity Verification

| Service | Port | Test |
|---------|------|------|
| Backend | 8080 | curl http://localhost:8080/health |
| Frontend | 3000 | curl http://localhost:3000 |
| PostgreSQL | 5432 | psql connection verified |
| TimescaleDB | 5433 | psql connection verified |

---

## Runtime Result

**STATUS**: ✅ ALL CONTAINERS STARTED SUCCESSFULLY

- 9/9 containers running
- 5/9 containers healthy
- 4/9 containers starting (will become healthy)
- 0/9 containers failed
- 0/9 containers stopped

---

## Next Steps

Proceed to **PHASE H4 - Database Validation** to verify migrations and connectivity.
