/**
 * Shared Viewer Types
 * Common types used across all map viewers
 */

// Camera state for all viewers
export interface CameraState {
  latitude: number;
  longitude: number;
  altitude?: number;
  heading?: number;
  pitch?: number;
  roll?: number;
  zoom?: number;
}

// Layer visibility state
export interface LayerVisibility {
  id: string;
  visible: boolean;
  opacity?: number;
  name?: string;
}

// Selection state
export interface SelectionState {
  selectedIds: string[];
  selectedType?: 'asset' | 'sensor' | 'event' | 'measurement';
}

// Sync state for cross-viewer synchronization
export interface ViewerSyncState {
  camera: CameraState | null;
  layers: LayerVisibility[];
  selection: SelectionState;
}

// Map view modes
export enum ViewerViewMode {
  MAPLIBRE_2D = 'maplibre_2d',
  MAPLIBRE_VECTOR = 'maplibre_vector',
  CESIUM_3D = 'cesium_3d',
  LEAFLET_2D = 'leaflet_2d',
  TERRA_FEDERATION = 'terra_federation',
  KEPLER_ANALYTICS = 'kepler_analytics',
}

// Base viewer interface
export interface BaseViewer {
  id: string;
  mode: ViewerViewMode;
  setCamera?: (camera: CameraState) => void;
  setLayers?: (layers: LayerVisibility[]) => void;
  setSelection?: (selection: SelectionState) => void;
  getCamera?: () => CameraState;
  getLayers?: () => LayerVisibility[];
  destroy?: () => void;
}

// Viewer registration
export interface ViewerRegistration {
  mode: ViewerViewMode;
  viewer: BaseViewer;
  priority?: number;
}

// Event types
export interface ViewerEvent {
  type: 'camera_change' | 'layer_change' | 'selection_change' | 'click' | 'hover';
  viewerId: string;
  timestamp: number;
  data?: any;
}

// Timeline state
export interface TimelineState {
  currentTime: Date;
  startTime: Date;
  endTime: Date;
  isPlaying: boolean;
  playbackSpeed: number;
}
