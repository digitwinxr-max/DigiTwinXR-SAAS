/**
 * Kepler.gl Type Definitions
 */

export interface KeplerConfig {
  appName: string;
  mapboxApiAccessToken?: string;
  maplibreApiAccessToken?: string;
}

export interface KeplerDataset {
  id: string;
  label: string;
  type: DatasetType;
  data: KeplerData;
  color?: string;
}

export enum DatasetType {
  GEOJSON = 'geojson',
  CSV = 'csv',
  TIMESERIES = 'timeseries',
  TELEMETRY = 'telemetry'
}

export interface KeplerData {
  fields: KeplerField[];
  rows: KeplerRow[];
}

export interface KeplerField {
  name: string;
  type: FieldType;
  format?: string;
}

export enum FieldType {
  STRING = 'string',
  FLOAT = 'float',
  INT = 'int',
  BOOLEAN = 'boolean',
  TIMESTAMP = 'timestamp',
  GEOJSON = 'geojson'
}

export type KeplerRow = Record<string, any>;

export interface HeatmapLayer {
  id: string;
  datasetId: string;
  type: 'heatmap';
  config: HeatmapConfig;
}

export interface HeatmapConfig {
  radiusPixels?: number;
  intensity?: number;
  threshold?: number;
  weightField?: string;
  colorRange?: string[];
}

export interface ClusterLayer {
  id: string;
  datasetId: string;
  type: 'cluster';
  config: ClusterConfig;
}

export interface ClusterConfig {
  radiusPixels?: number;
  minZoom?: number;
  maxZoom?: number;
  colorRange?: string[];
}

export interface FlowMapLayer {
  id: string;
  datasetId: string;
  type: 'flow';
  config: FlowMapConfig;
}

export interface FlowMapConfig {
  sourceLatField: string;
  sourceLngField: string;
  targetLatField: string;
  targetLngField: string;
  weightField?: string;
  colorRange?: string[];
  opacity?: number;
}

export interface TrajectoryLayer {
  id: string;
  datasetId: string;
  type: 'trajectory';
  config: TrajectoryConfig;
}

export interface TrajectoryConfig {
  latField: string;
  lngField: string;
  timestampField: string;
  idField?: string;
  colorField?: string;
  thickness?: number;
  opacity?: number;
}

export interface HexBinLayer {
  id: string;
  datasetId: string;
  type: 'hexbin';
  config: HexBinConfig;
}

export interface HexBinConfig {
  coverage?: number;
  elevationScale?: number;
  extruded?: boolean;
  radius?: number;
  colorRange?: string[];
  colorField?: string;
  elevationField?: string;
}

export interface FilterConfig {
  id: string;
  name: string;
  type: FilterType;
  field: string;
  value: any;
  range?: [any, any];
  domain?: [any, any];
}

export enum FilterType {
  SPATIAL = 'spatial',
  ATTRIBUTE = 'attribute',
  TIME = 'time',
  RANGE = 'range'
}

export interface TimeWindow {
  start: string;
  end: string;
  step?: number;
}

export interface AggregationConfig {
  type: AggregationType;
  field: string;
  method: AggregationMethod;
}

export enum AggregationType {
  HEX_BIN = 'hexbin',
  GRID = 'grid',
  CLUSTER = 'cluster'
}

export enum AggregationMethod {
  COUNT = 'count',
  SUM = 'sum',
  AVG = 'avg',
  MIN = 'min',
  MAX = 'max'
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
  filters: FilterConfig[];
  timeWindow: TimeWindow | null;
}

export enum AnalyticsViewMode {
  LEAFLET_2D = 'leaflet-2d',
  MAPLIBRE_VECTOR = 'maplibre-vector',
  CESIUM_3D = 'cesium-3d',
  TERRA_FEDERATION = 'terria-federation',
  KEPLER_ANALYTICS = 'kepler-analytics'
}

export interface KeplerMapState {
  datasets: KeplerDataset[];
  layers: AnalyticsLayer[];
  filters: FilterConfig[];
  interactionConfig: any;
  layerBlending: string;
}

export type AnalyticsLayer = HeatmapLayer | ClusterLayer | FlowMapLayer | TrajectoryLayer | HexBinLayer;
