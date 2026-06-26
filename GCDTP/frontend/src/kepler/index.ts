/**
 * Kepler.gl Module
 * 
 * Provides analytical visualization capabilities.
 */

// Types
export * from './kepler_types';

// Context providers
export { KeplerProvider, useKepler, useDatasets, useKeplerCamera } from './KeplerContext';
export { DatasetProvider, useDatasetManager, useDatasetOperations, SUPPORTED_DATASET_TYPES } from './DatasetManager';
export { HeatmapProvider, useHeatmap, useHeatmapOperations, HEATMAP_COLOR_RANGES } from './HeatmapManager';
export { ClusterProvider, useCluster, useClusterOperations, CLUSTER_COLOR_SCHEMES } from './ClusterManager';
export { FlowMapProvider, useFlowMap, useFlowMapOperations, FLOWMAP_COLOR_SCHEMES } from './FlowMapManager';
export { TrajectoryProvider, useTrajectory, useTrajectoryOperations } from './TrajectoryManager';
export { TemporalProvider, useTemporal, useTemporalOperations, useTimelineSync } from './TemporalDatasetManager';
export { AggregationProvider, useAggregation, useAggregationOperations, HEX_COLOR_SCHEMES } from './AggregationManager';
export { AnalyticsLayerProvider, useAnalyticsLayer, useAnalyticsLayerOperations } from './AnalyticsLayerManager';
export { FilterProvider, useFilter, useFilterOperations } from './FilterManager';
export { KeplerSyncProvider, useKeplerSync, useLeafletSync, useMapLibreSync, useCesiumSync, useTerriaSync } from './SynchronizationManager';

// Components
export { KeplerViewer, KeplerViewerControls, KeplerLayerPanel, KeplerDatasetPanel, KeplerFilterPanel } from './KeplerViewer';

// Constants
export { AnalyticsViewMode } from './kepler_types';
