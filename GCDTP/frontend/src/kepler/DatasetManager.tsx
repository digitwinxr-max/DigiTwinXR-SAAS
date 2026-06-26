/**
 * Dataset Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { KeplerDataset, KeplerData, DatasetType, KeplerField } from './kepler_types';

interface DatasetContextValue {
  datasets: KeplerDataset[];
  addDataset: (dataset: KeplerDataset) => void;
  removeDataset: (id: string) => void;
  updateDataset: (id: string, updates: Partial<KeplerDataset>) => void;
  getDataset: (id: string) => KeplerDataset | undefined;
  getDatasetByLabel: (label: string) => KeplerDataset | undefined;
}

const DatasetContext = createContext<DatasetContextValue | undefined>(undefined);

interface DatasetProviderProps {
  children: ReactNode;
}

export function DatasetProvider({ children }: DatasetProviderProps) {
  const [datasets, setDatasets] = useState<KeplerDataset[]>([]);

  const addDataset = (dataset: KeplerDataset) => {
    setDatasets(prev => [...prev, dataset]);
  };

  const removeDataset = (id: string) => {
    setDatasets(prev => prev.filter(d => d.id !== id));
  };

  const updateDataset = (id: string, updates: Partial<KeplerDataset>) => {
    setDatasets(prev => prev.map(d => d.id === id ? { ...d, ...updates } : d));
  };

  const getDataset = (id: string) => {
    return datasets.find(d => d.id === id);
  };

  const getDatasetByLabel = (label: string) => {
    return datasets.find(d => d.label === label);
  };

  const value: DatasetContextValue = {
    datasets,
    addDataset,
    removeDataset,
    updateDataset,
    getDataset,
    getDatasetByLabel
  };

  return (
    <DatasetContext.Provider value={value}>
      {children}
    </DatasetContext.Provider>
  );
}

export function useDatasetManager() {
  const context = useContext(DatasetContext);
  if (!context) {
    throw new Error('useDatasetManager must be used within a DatasetProvider');
  }
  return context;
}

// Dataset operations
export function useDatasetOperations() {
  const { addDataset, removeDataset, getDataset } = useDatasetManager();

  const loadGeoJSON = async (id: string, label: string, geojson: any) => {
    const dataset: KeplerDataset = {
      id,
      label,
      type: DatasetType.GEOJSON,
      data: convertGeoJSONToKepler(geojson),
      color: generateColor()
    };
    addDataset(dataset);
    return dataset;
  };

  const loadCSV = async (id: string, label: string, csvData: string) => {
    const dataset: KeplerDataset = {
      id,
      label,
      type: DatasetType.CSV,
      data: parseCSV(csvData),
      color: generateColor()
    };
    addDataset(dataset);
    return dataset;
  };

  const loadTimeseries = async (id: string, label: string, data: any[]) => {
    const dataset: KeplerDataset = {
      id,
      label,
      type: DatasetType.TIMESERIES,
      data: { fields: [], rows: data },
      color: generateColor()
    };
    addDataset(dataset);
    return dataset;
  };

  const loadTelemetry = async (id: string, label: string, telemetryData: any[]) => {
    const dataset: KeplerDataset = {
      id,
      label,
      type: DatasetType.TELEMETRY,
      data: { fields: [], rows: telemetryData },
      color: generateColor()
    };
    addDataset(dataset);
    return dataset;
  };

  const unloadDataset = (id: string) => {
    removeDataset(id);
  };

  return {
    loadGeoJSON,
    loadCSV,
    loadTimeseries,
    loadTelemetry,
    unloadDataset,
    getDataset
  };
}

// Helper functions
function convertGeoJSONToKepler(geojson: any): KeplerData {
  const fields: KeplerField[] = [];
  const rows: any[] = [];
  
  if (geojson.features && geojson.features.length > 0) {
    const sample = geojson.features[0];
    if (sample.properties) {
      Object.keys(sample.properties).forEach(key => {
        fields.push({ name: key, type: 'string' });
      });
    }
    
    geojson.features.forEach((feature: any) => {
      rows.push(feature.properties || {});
    });
  }
  
  return { fields, rows };
}

function parseCSV(csvData: string): KeplerData {
  const lines = csvData.split('\n');
  if (lines.length < 2) return { fields: [], rows: [] };
  
  const headers = lines[0].split(',');
  const fields: KeplerField[] = headers.map(h => ({ name: h.trim(), type: 'string' }));
  
  const rows: any[] = [];
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',');
    const row: any = {};
    headers.forEach((h, idx) => {
      row[h.trim()] = values[idx]?.trim() || '';
    });
    rows.push(row);
  }
  
  return { fields, rows };
}

function generateColor(): string {
  const colors = ['#48C9B0', '#AF7AC5', '#F5B041', '#5DADE2', '#EC7063'];
  return colors[Math.floor(Math.random() * colors.length)];
}

// Supported dataset types
export const SUPPORTED_DATASET_TYPES = {
  GEOJSON: 'application/geo+json',
  CSV: 'text/csv',
  TIMESERIES: 'application/json',
  TELEMETRY: 'application/json'
};
