/**
 * Federation Manager
 * Integrates GeoServer, PostGIS, and other data sources
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { CatalogItem, CatalogItemType, FederationConfig } from './terria_types';

interface FederationContextValue {
  config: FederationConfig;
  federatedSources: FederatedSource[];
  addFederatedSource: (source: FederatedSource) => void;
  removeFederatedSource: (id: string) => void;
  getLayersFromSource: (sourceId: string) => CatalogItem[];
  updateConfig: (config: Partial<FederationConfig>) => void;
}

interface FederatedSource {
  id: string;
  name: string;
  type: FederatedSourceType;
  url: string;
  layers: CatalogItem[];
  isConnected: boolean;
}

enum FederatedSourceType {
  GEOSERVER_WMS = 'geoserver-wms',
  GEOSERVER_WFS = 'geoserver-wfs',
  POSTGIS = 'postgis',
  ARCIGIS = 'arcgis',
  CUSTOM = 'custom'
}

const FederationContext = createContext<FederationContextValue | undefined>(undefined);

interface FederationProviderProps {
  children: ReactNode;
  initialConfig?: Partial<FederationConfig>;
}

export function FederationProvider({ children, initialConfig }: FederationProviderProps) {
  const [config, setConfig] = useState<FederationConfig>({
    geoserverUrl: initialConfig?.geoserverUrl || 'http://localhost:8080/geoserver',
    enableTerrain: true,
    enable3dTiles: true,
    ...initialConfig
  });
  
  const [federatedSources, setFederatedSources] = useState<FederatedSource[]>([]);

  const addFederatedSource = (source: FederatedSource) => {
    setFederatedSources(prev => [...prev, source]);
  };

  const removeFederatedSource = (id: string) => {
    setFederatedSources(prev => prev.filter(s => s.id !== id));
  };

  const getLayersFromSource = (sourceId: string): CatalogItem[] => {
    const source = federatedSources.find(s => s.id === sourceId);
    return source?.layers || [];
  };

  const updateConfig = (newConfig: Partial<FederationConfig>) => {
    setConfig(prev => ({ ...prev, ...newConfig }));
  };

  const value: FederationContextValue = {
    config,
    federatedSources,
    addFederatedSource,
    removeFederatedSource,
    getLayersFromSource,
    updateConfig
  };

  return (
    <FederationContext.Provider value={value}>
      {children}
    </FederationContext.Provider>
  );
}

export function useFederation() {
  const context = useContext(FederationContext);
  if (!context) {
    throw new Error('useFederation must be used within a FederationProvider');
  }
  return context;
}

// GeoServer integration
export function useGeoServerFederation() {
  const { addFederatedSource, removeFederatedSource, federatedSources } = useFederation();
  const [isConnecting, setIsConnecting] = useState(false);

  const connectGeoServer = async (url: string, workspace?: string) => {
    setIsConnecting(true);
    try {
      // Get WMS capabilities
      const wmsUrl = `${url}/wms`;
      const layers = await fetchGeoServerLayers(wmsUrl, CatalogItemType.WMS);
      
      const source: FederatedSource = {
        id: `geoserver-${Date.now()}`,
        name: 'GeoServer',
        type: FederatedSourceType.GEOSERVER_WMS,
        url: wmsUrl,
        layers,
        isConnected: true
      };
      
      addFederatedSource(source);
      return source;
    } finally {
      setIsConnecting(false);
    }
  };

  const disconnectGeoServer = (sourceId: string) => {
    removeFederatedSource(sourceId);
  };

  const getConnectedGeoServers = () => {
    return federatedSources.filter(
      s => s.type === FederatedSourceType.GEOSERVER_WMS || 
           s.type === FederatedSourceType.GEOSERVER_WFS
    );
  };

  return {
    connectGeoServer,
    disconnectGeoServer,
    isConnecting,
    connectedServers: getConnectedGeoServers()
  };
}

// PostGIS integration
export function usePostGISFederation() {
  const { addFederatedSource, federatedSources } = useFederation();
  const [isConnecting, setIsConnecting] = useState(false);

  const connectPostGIS = async (connectionString: string) => {
    setIsConnecting(true);
    try {
      // Placeholder - would connect to PostGIS via backend API
      const layers: CatalogItem[] = [];
      
      const source: FederatedSource = {
        id: `postgis-${Date.now()}`,
        name: 'PostGIS',
        type: FederatedSourceType.POSTGIS,
        url: connectionString,
        layers,
        isConnected: true
      };
      
      addFederatedSource(source);
      return source;
    } finally {
      setIsConnecting(false);
    }
  };

  const getConnectedPostGIS = () => {
    return federatedSources.filter(s => s.type === FederatedSourceType.POSTGIS);
  };

  return {
    connectPostGIS,
    isConnecting,
    connectedSources: getConnectedPostGIS()
  };
}

// Layer federation hooks
export function useFederatedLayers() {
  const { federatedSources } = useFederation();

  const allLayers = federatedSources.flatMap(s => s.layers);
  const wmsLayers = allLayers.filter(l => l.type === CatalogItemType.WMS);
  const wfsLayers = allLayers.filter(l => l.type === CatalogItemType.WFS);
  const vectorLayers = allLayers.filter(l => 
    l.type === CatalogItemType.GeoJSON || 
    l.type === CatalogItemType.CSV ||
    l.type === CatalogItemType.KML
  );

  return {
    allLayers,
    wmsLayers,
    wfsLayers,
    vectorLayers,
    layerCount: allLayers.length,
    sourceCount: federatedSources.length
  };
}

// Helper function to fetch GeoServer layers
async function fetchGeoServerLayers(url: string, type: CatalogItemType): Promise<CatalogItem[]> {
  // Placeholder - actual implementation would parse GetCapabilities
  return [];
}

// Add federated source dialog
interface AddSourceDialogProps {
  onAdd: (source: Partial<FederatedSource>) => void;
  onClose: () => void;
}

export function AddSourceDialog({ onAdd, onClose }: AddSourceDialogProps) {
  const [sourceType, setSourceType] = useState<FederatedSourceType>(FederatedSourceType.GEOSERVER_WMS);
  const [url, setUrl] = useState('');

  const handleAdd = () => {
    onAdd({
      name: `${sourceType} - ${url}`,
      type: sourceType,
      url,
      layers: [],
      isConnected: false
    });
    onClose();
  };

  return (
    <div className="add-source-dialog">
      <h3>Add Data Source</h3>
      
      <select 
        value={sourceType} 
        onChange={(e) => setSourceType(e.target.value as FederatedSourceType)}
      >
        <option value={FederatedSourceType.GEOSERVER_WMS}>GeoServer WMS</option>
        <option value={FederatedSourceType.GEOSERVER_WFS}>GeoServer WFS</option>
        <option value={FederatedSourceType.POSTGIS}>PostGIS</option>
        <option value={FederatedSourceType.ARCIGIS}>ArcGIS</option>
      </select>
      
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Service URL"
      />
      
      <button onClick={handleAdd}>Add</button>
      <button onClick={onClose}>Cancel</button>
    </div>
  );
}
