/**
 * TerriaJS Type Definitions
 */

export interface TerriaConfig {
  appName: string;
  cesiumIonAccessToken?: string;
  cesiumBaseUrl?: string;
  terriaCesiumBaseUrl?: string;
  terriaMapV8Url?: string;
  useCesiumIonTerrain?: boolean;
  geocoderUrl?: string;
  proxyUrl?: string;
  shareUrl?: string;
}

export interface CatalogItem {
  id: string;
  name: string;
  type: CatalogItemType;
  description?: string;
  url?: string;
  isEnabled: boolean;
  showOnTimeline: boolean;
  metadataUrl?: string;
  legendUrl?: string;
  cacheDuration?: string;
}

export enum CatalogItemType {
  WMS = "wms",
  WFS = "wfs",
  CSW = "csw",
  GeoJSON = "geojson",
  CSV = "csv",
  KML = "kml",
  KMZ = "kmz",
  GPKG = "gpkg",
  TERRAIN = "terrain",
  VECTOR_TILE = "vectorTile"
}

export interface LayerCatalog {
  id: string;
  name: string;
  items: CatalogItem[];
  isOpen: boolean;
}

export interface DatasetCatalog {
  id: string;
  name: string;
  description?: string;
  categories: string[];
  layers: CatalogItem[];
  source?: string;
}

export interface StoryChapter {
  id: string;
  title: string;
  narrative: string;
  cameraPosition: CameraPosition;
  layerStates: LayerState[];
  duration?: number;
}

export interface CameraPosition {
  longitude: number;
  latitude: number;
  height?: number;
  pitch?: number;
  heading?: number;
  roll?: number;
}

export interface LayerState {
  layerId: string;
  isEnabled: boolean;
  opacity: number;
  time?: string;
}

export interface StoryMap {
  id: string;
  title: string;
  description?: string;
  chapters: StoryChapter[];
  createdAt: string;
  updatedAt: string;
}

export interface LayerMetadata {
  id: string;
  name: string;
  description?: string;
  keywords?: string[];
  CRS?: string[];
  boundingBox?: BoundingBox;
  extent?: string;
  license?: string;
  attribution?: string;
}

export interface BoundingBox {
  west: number;
  south: number;
  east: number;
  north: number;
}

export interface ShareState {
  camera?: CameraPosition;
  layers?: LayerState[];
  stories?: string[];
  time?: string;
}

export interface TimeInterval {
  start: string;
  end: string;
  isContinuous: boolean;
}

export interface TimeEnabledLayer {
  layerId: string;
  currentTime?: string;
  availableIntervals?: TimeInterval[];
  timeMultiplier?: number;
}

export enum ViewMode {
  LEAFLET_2D = "leaflet-2d",
  CESIUM_3D = "cesium-3d",
  TERRA_FEDERATION = "terria-federation"
}

export interface FederationConfig {
  geoserverUrl?: string;
  postgisConnection?: string;
  enableTerrain: boolean;
  enable3dTiles: boolean;
}

export interface LegendData {
  title?: string;
  items: LegendItem[];
}

export interface LegendItem {
  color: string;
  label: string;
}
