import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { EventBusProvider } from './hooks/useEventBus';
import AssetList from './pages/AssetList';
import CreateAsset from './pages/CreateAsset';
import AssetDetails from './pages/AssetDetails';
import Map from './pages/Map';
import SensorList from './pages/SensorList';
import CreateSensor from './pages/CreateSensor';
import SensorDetails from './pages/SensorDetails';
import SensorMeasurements from './pages/SensorMeasurements';
import SensorThresholds from './pages/SensorThresholds';
import Measurements from './pages/Measurements';
import MeasurementDetails from './pages/MeasurementDetails';
import ThresholdList from './pages/ThresholdList';
import CreateThreshold from './pages/CreateThreshold';
import EventList from './pages/EventList';
import EventDetails from './pages/EventDetails';
import ActiveEvents from './pages/ActiveEvents';
import HealthDashboard from './pages/HealthDashboard';
import GeoPortal from './pages/GeoPortal';
import AssetHierarchy from './pages/AssetHierarchy';
import ImpactChain from './pages/ImpactChain';
import NetworkHealth from './pages/NetworkHealth';
import ScenarioStudio from './pages/ScenarioStudio';

function App() {
  return (
    <EventBusProvider>
      <BrowserRouter>
        <div>
          <header>
            <div className="container">
              <h1>GCDTP Operational Intelligence</h1>
              <nav>
                <Link to="/geoportal">GeoPortal</Link>
                <Link to="/assets">Assets</Link>
                <Link to="/sensors">Sensors</Link>
                <Link to="/measurements">Measurements</Link>
                <Link to="/thresholds">Thresholds</Link>
                <Link to="/events">Events</Link>
                <Link to="/health">Health</Link>
                <Link to="/hierarchy">Hierarchy</Link>
                <Link to="/impacts">Impact Chain</Link>
                <Link to="/network">Network Health</Link>
                <Link to="/scenarios">Scenario Studio</Link>
                <Link to="/map" className="deprecated">Map</Link>
              </nav>
            </div>
          </header>

          <main className="container">
            <Routes>
              <Route path="/" element={<GeoPortal />} />
              <Route path="/geoportal" element={<GeoPortal />} />
              <Route path="/assets" element={<AssetList />} />
              <Route path="/assets/create" element={<CreateAsset />} />
              <Route path="/assets/:id" element={<AssetDetails />} />
              <Route path="/sensors" element={<SensorList />} />
              <Route path="/sensors/create" element={<CreateSensor />} />
              <Route path="/sensors/:id" element={<SensorDetails />} />
              <Route path="/sensors/:id/measurements" element={<SensorMeasurements />} />
              <Route path="/sensors/:id/thresholds" element={<SensorThresholds />} />
              <Route path="/measurements" element={<Measurements />} />
              <Route path="/measurements/:id" element={<MeasurementDetails />} />
              <Route path="/thresholds" element={<ThresholdList />} />
              <Route path="/thresholds/create" element={<CreateThreshold />} />
              <Route path="/thresholds/:id/edit" element={<CreateThreshold />} />
              <Route path="/events" element={<EventList />} />
              <Route path="/events/active" element={<ActiveEvents />} />
              <Route path="/events/:id" element={<EventDetails />} />
              <Route path="/health" element={<HealthDashboard />} />
              <Route path="/hierarchy" element={<AssetHierarchy />} />
              <Route path="/impacts" element={<ImpactChain />} />
              <Route path="/network" element={<NetworkHealth />} />
              <Route path="/scenarios" element={<ScenarioStudio />} />
              <Route path="/map" element={<Map />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </EventBusProvider>
  );
}

export default App;
