# ADR-0014: GeoPortal v2 - Operational Intelligence

## Status

Accepted

## Context

GCDTP has implemented:
1. **Measurement Engine** (ADR-0008) - Stores sensor measurements
2. **Threshold Engine** (ADR-0010) - Evaluates measurements against rules
3. **Event Engine** (ADR-0011) - Stores threshold violation events
4. **Health Engine** (ADR-0013) - Derived health state from events

We now have rich operational data. The original GeoPortal (Map) was a simple visualization tool showing asset locations. It needs to evolve into an **operational intelligence dashboard** that reflects the current state of the system.

## Why Operational Intelligence?

### From Visualization to Operational Twin

The old map was a **data visualization** tool:
- Showed assets on a map
- Blue dots for all assets
- Basic location information

The new GeoPortal is an **operational intelligence** tool:
- Shows real-time system state
- Color-coded by health status
- Displays active events
- Provides actionable insights

```
┌─────────────────────────────────────────┐
│           OLD MAP                        │
│  "Where are my assets?"                  │
│  → Simple location display               │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        NEW GEOPORTAL                     │
│  "What's the state of my system?"        │
│  → Operational intelligence              │
└─────────────────────────────────────────┘
```

## Architecture

### Layer Separation

The GeoPortal combines multiple data sources into a unified view:

```
┌─────────────────────────────────────────┐
│              GEOPORTAL                  │
├─────────────────────────────────────────┤
│  Data Layers (from API)                 │
│  ├── Assets (GeoJSON)                   │
│  ├── Health (color coding)              │
│  └── Events (active only)               │
├─────────────────────────────────────────┤
│  Visualization Layers                    │
│  ├── Asset Markers (color by health)    │
│  ├── Event Markers (pulsing rings)      │
│  └── Popups (detailed info)             │
└─────────────────────────────────────────┘
```

### Data Sources

| Source | Endpoint | Purpose |
|--------|----------|---------|
| Assets | GET /assets/geojson | Asset locations |
| Health | GET /health/assets | Health status per asset |
| Events | GET /events/active | Active events |
| Sensors | GET /assets/{id}/sensors | Sensor count |

## Design Decisions

### Health-Based Asset Colors

Asset markers reflect health status:

| Status | Color | Hex |
|--------|-------|-----|
| HEALTHY | Green | #22c55e |
| DEGRADED | Orange | #f97316 |
| CRITICAL | Red | #ef4444 |
| UNKNOWN | Gray | #6b7280 |

### Event Overlay

Active events are displayed as pulsing rings:

| Severity | Color | Style |
|----------|-------|-------|
| WARNING | Yellow | Pulsing ring |
| CRITICAL | Red | Pulsing ring |

### Popup Content

When clicking an asset marker, the popup shows:

```
┌─────────────────────────────┐
│ Asset Name                  │
│ Asset Type                   │
├─────────────────────────────┤
│ Health Status: HEALTHY (95) │
├─────────────────────────────┤
│ Status: active              │
│ Sensors: 5                  │
├─────────────────────────────┤
│ Active Events (2)           │
│ ⚠ Warning: 1               │
│ 🔴 Critical: 1              │
└─────────────────────────────┘
```

### Sidebar

The GeoPortal includes a sidebar with:

1. **Layer Toggles**
   - Assets (on/off)
   - Events (on/off)
   - Sensors (on/off)

2. **Summary Cards**
   - Total active events
   - Warning count
   - Critical count
   - Healthy asset count

3. **Legend**
   - Health status colors
   - Event severity colors

4. **Refresh Button**
   - Manual data refresh

## Real-Time Updates

### Event Bus Architecture

The GeoPortal subscribes to events via an Event Bus:

```javascript
useEventSubscription(EVENTS.EVENT_CREATED, () => {
  fetchAllData();
});

useEventSubscription(EVENTS.EVENT_RESOLVED, () => {
  fetchAllData();
});

useEventSubscription(EVENTS.HEALTH_UPDATED, () => {
  fetchAllData();
});

useEventSubscription(EVENTS.ASSET_UPDATED, () => {
  fetchAllData();
});
```

### Why Event Bus?

1. **No Polling** - Updates happen only when events occur
2. **Efficient** - Only refreshes when state changes
3. **Reactive** - UI stays in sync with backend

### Event Bus Design

```javascript
// EventBusProvider - Context provider
const EventBusContext = createContext(null);

// useEventBus - Hook for manual subscribe/publish
const { subscribe, publish } = useEventBus();

// useEventSubscription - Hook for automatic subscription
useEventSubscription('event.created', callback);
```

### Event Types

| Event | Trigger | GeoPortal Action |
|-------|---------|------------------|
| event.created | New event created | Refresh map |
| event.resolved | Event resolved | Refresh map |
| health.updated | Health recalculated | Refresh map |
| asset.updated | Asset modified | Refresh map |

## Future: WebSocket Integration

The current implementation uses polling fallback. In the future, we can integrate WebSockets for true real-time updates:

```javascript
// Future WebSocket implementation
socket.on('event.created', (event) => {
  eventBus.publish(EVENTS.EVENT_CREATED, event);
});
```

## Separation: Data vs State

### Data Layers (Static-ish)

- **GeoJSON** - Asset locations (changes rarely)
- **Sensors** - Asset sensors (changes when sensors added/removed)

### State Layers (Dynamic)

- **Health** - Changes when events created/resolved
- **Events** - Changes when events occur

This separation helps understand which layers need real-time updates vs. on-demand loading.

## Consequences

### Positive
- Single view of operational state
- Color-coded health provides instant situational awareness
- Event markers highlight problem areas
- Popup details enable quick investigation
- Event bus enables reactive updates

### Negative
- More API calls (health, events, sensors)
- More complex state management
- Potential for stale data between updates

### Neutral
- No automatic alerts (that's future work)
- No historical trends (dashboard focus)
- No predictive capabilities (ML is future)

## Future Considerations

- **WebSocket Integration** - Real-time instead of event bus polling
- **Event Clustering** - Cluster nearby events for dense areas
- **Heatmaps** - Show event density on map
- **Historical Playback** - Replay events over time
- **Multiple Basemaps** - Satellite, terrain, etc.
- **Asset Filters** - Filter by type, status, health
- **Event Timeline** - Timeline of events on map

## Why Not Build Alerts Into Map?

Alerts are a separate concern from operational intelligence:

```
Operational Intelligence          Alerts
─────────────────────────────    ──────────────
What is happening now?           Who needs to know?
Visual state on map              Notification system
Passive viewing                  Active notifications
Dashboard use                    PagerDuty, email, SMS
```

The GeoPortal shows the state. A future Alert Engine would notify users.

## Component Structure

```
GeoPortal/
├── GeoPortal.jsx      # Main component
├── GeoPortal.css      # Styles
├── GeoPortal.test.jsx # Tests
└── index.js           # Export
```

## Dependencies

- react-leaflet - Map rendering
- react-leaflet CSS - Map styling
- useEventBus - Custom hook for event subscription