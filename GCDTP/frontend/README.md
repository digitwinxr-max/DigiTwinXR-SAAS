# Frontend

This directory contains the React frontend application.

## Structure

```
frontend/
├── src/
│   ├── api/          # API client functions
│   ├── pages/        # Page components
│   │   ├── AssetList.jsx
│   │   ├── AssetDetails.jsx
│   │   ├── CreateAsset.jsx
│   │   └── Map.jsx
│   ├── components/   # Reusable components
│   │   └── MapView/  # Leaflet map component
│   ├── App.jsx       # Main application component
│   └── main.jsx      # Entry point
├── public/           # Static assets
├── tests/            # Test files
├── package.json
├── vite.config.js
└── index.html
```

## Pages

| Page | Route | Description |
|------|-------|-------------|
| **GeoPortal** | /geoportal | Operational intelligence dashboard (default) |
| Asset List | /assets | View all assets |
| Asset Details | /assets/:id | View and edit single asset |
| Create Asset | /assets/create | Form to create new asset |
| Sensor List | /sensors | View all sensors |
| Sensor Details | /sensors/:id | View and edit single sensor |
| Create Sensor | /sensors/create | Form to create new sensor |
| Sensor Measurements | /sensors/:id/measurements | View sensor measurements with chart |
| Sensor Thresholds | /sensors/:id/thresholds | View sensor threshold rules |
| Measurement List | /measurements | View all measurements |
| Measurement Details | /measurements/:id | View measurement details |
| Threshold List | /thresholds | View all threshold rules |
| Create Threshold | /thresholds/create | Form to create threshold rule |
| Event List | /events | View all events |
| Active Events | /events/active | View active events with summary |
| Event Details | /events/:id | View event details and resolve |
| Health Dashboard | /health | View all asset health status |
| Map | /map | Map viewer (deprecated) |

## GeoPortal - Operational Intelligence

The GeoPortal is an operational intelligence dashboard that shows real-time system state:

### Features
- Asset markers color-coded by health status
- Pulsing event markers for active warnings/criticals
- Interactive popups with asset, health, and event details
- Layer toggles for assets, events, sensors
- Summary cards with event counts
- Event bus integration for real-time updates

### Health Colors
- **Green**: HEALTHY (80-100)
- **Orange**: DEGRADED (40-79)
- **Red**: CRITICAL (0-39)

### Event Markers
- **Yellow pulsing ring**: WARNING
- **Red pulsing ring**: CRITICAL

## Map Viewer

The map uses Leaflet with OpenStreetMap tiles:

- **Default View**: Centered on Botswana (zoom 6)
- **Markers**: Circle markers for each asset
- **Popups**: Display name, type, status, coordinates
- **Data Source**: Loads from `/api/assets/geojson`

## Measurement Chart

The chart uses Recharts for visualization:

- **Line Chart**: Displays measurements over time
- **Tooltip**: Shows timestamp, value, and quality
- **Responsive**: Adapts to screen size
- **No live updates**: Static data display

## Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at http://localhost:3000

### Testing

```bash
npm test
```

### Production Build

```bash
npm run build
```

## Dependencies

- React 18
- React Router DOM 6
- Leaflet
- React-Leaflet
- Recharts
- Vite

## API Integration

The frontend communicates with the backend API at `/api`. Configure the API base URL in the environment or proxy settings.
