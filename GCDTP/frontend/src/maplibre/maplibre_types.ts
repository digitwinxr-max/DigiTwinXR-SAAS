/**
 * MapLibre Type Definitions
 */

export interface MapLibreConfig {
  style: string;
  center?: [number, number];
  zoom?: number;
  bearing?: number;
  pitch?: number;
  maxZoom?: number;
  minZoom?: number;
}

export interface VectorTileSource {
  id: string;
  type: 'vector';
  url: string;
  tiles?: string[];
  bounds?: [number, number, number, number];
  minzoom?: number;
  maxzoom?: number;
}

export interface RasterTileSource {
  id: string;
  type: 'raster';
  url: string;
  tiles?: string[];
  tileSize?: number;
  bounds?: [number, number, number, number];
}

export interface GeoJSONSource {
  id: string;
  type: 'geojson';
  data: GeoJSON.FeatureCollection | string;
  buffer?: number;
  tolerance?: number;
}

export type TileSource = VectorTileSource | RasterTileSource | GeoJSONSource;

export interface VectorLayer {
  id: string;
  source: string;
  sourceLayer?: string;
  type: 'fill' | 'line' | 'symbol' | 'circle' | 'fill-extrusion' | 'heatmap' | 'hillshade';
  paint?: any;
  layout?: any;
  filter?: any[];
  minzoom?: number;
  maxzoom?: number;
}

export interface RasterLayer {
  id: string;
  source: string;
  type: 'raster';
  paint?: any;
  minzoom?: number;
  maxzoom?: number;
}

export interface MapStyle {
  version: number;
  name: string;
  metadata?: any;
  sources: Record<string, TileSource>;
  layers: VectorLayer[];
  sprite?: string;
  glyphs?: string;
}

export interface PMTilesInfo {
  id: string;
  name: string;
  description?: string;
  bounds: [number, number, number, number];
  center: [number, number];
  minZoom: number;
  maxZoom: number;
  layers: string[];
  tileType: string;
}

export interface OfflineRegion {
  id: string;
  name: string;
  bounds: [number, number, number, number];
  minZoom: number;
  maxZoom: number;
  status: OfflineStatus;
  progress: number;
  createdAt: string;
}

export enum OfflineStatus {
  PENDING = 'pending',
  DOWNLOADING = 'downloading',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export interface TileCacheStats {
  hits: number;
  misses: number;
  size: number;
  maxSize: number;
  entries: number;
}

export interface CameraState {
  center: [number, number];
  zoom: number;
  bearing: number;
  pitch: number;
}

export interface LayerVisibility {
  layerId: string;
  visible: boolean;
  opacity: number;
}

export interface SyncState {
  camera: CameraState | null;
  layers: LayerVisibility[];
  selection: string[];
}

export enum MapViewMode {
  LEAFLET_2D = 'leaflet-2d',
  MAPLIBRE_VECTOR = 'maplibre-vector',
  CESIUM_3D = 'cesium-3d',
  TERRA_FEDERATION = 'terria-federation'
}

export interface ThemeConfig {
  id: string;
  name: string;
  primaryColor: string;
  secondaryColor: string;
  backgroundColor: string;
  textColor: string;
  mapStyle: string;
}
