import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

function MapView() {
  const [geojsonData, setGeojsonData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchGeoJSON();
  }, []);

  async function fetchGeoJSON() {
    try {
      setLoading(true);
      const response = await fetch('/api/assets/geojson');
      if (!response.ok) throw new Error('Failed to fetch GeoJSON');
      const data = await response.json();
      setGeojsonData(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="loading">Loading map data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <MapContainer
      center={[-22.3285, 24.6849]}
      zoom={6}
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {geojsonData?.features?.map((feature) => {
        if (!feature.geometry?.coordinates) return null;
        const [lng, lat] = feature.geometry.coordinates;
        const { name, asset_type, status } = feature.properties;

        return (
          <CircleMarker
            key={feature.id}
            center={[lat, lng]}
            radius={8}
            pathOptions={{ color: 'blue', fillColor: 'blue', fillOpacity: 0.6 }}
          >
            <Popup>
              <strong>{name}</strong>
              <br />
              Type: {asset_type}
              <br />
              Status: {status}
              <br />
              Coordinates: {lat.toFixed(6)}, {lng.toFixed(6)}
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}

export default MapView;
