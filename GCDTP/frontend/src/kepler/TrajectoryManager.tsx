/**
 * Trajectory Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { TrajectoryLayer, TrajectoryConfig } from './kepler_types';

interface TrajectoryContextValue {
  trajectories: TrajectoryLayer[];
  addTrajectory: (trajectory: TrajectoryLayer) => void;
  removeTrajectory: (id: string) => void;
  updateTrajectory: (id: string, updates: Partial<TrajectoryLayer>) => void;
  getTrajectory: (id: string) => TrajectoryLayer | undefined;
}

const TrajectoryContext = createContext<TrajectoryContextValue | undefined>(undefined);

interface TrajectoryProviderProps {
  children: ReactNode;
}

export function TrajectoryProvider({ children }: TrajectoryProviderProps) {
  const [trajectories, setTrajectories] = useState<TrajectoryLayer[]>([]);

  const addTrajectory = (trajectory: TrajectoryLayer) => {
    setTrajectories(prev => [...prev, trajectory]);
  };

  const removeTrajectory = (id: string) => {
    setTrajectories(prev => prev.filter(t => t.id !== id));
  };

  const updateTrajectory = (id: string, updates: Partial<TrajectoryLayer>) => {
    setTrajectories(prev => prev.map(t => t.id === id ? { ...t, ...updates } : t));
  };

  const getTrajectory = (id: string) => {
    return trajectories.find(t => t.id === id);
  };

  const value: TrajectoryContextValue = {
    trajectories,
    addTrajectory,
    removeTrajectory,
    updateTrajectory,
    getTrajectory
  };

  return (
    <TrajectoryContext.Provider value={value}>
      {children}
    </TrajectoryContext.Provider>
  );
}

export function useTrajectory() {
  const context = useContext(TrajectoryContext);
  if (!context) {
    throw new Error('useTrajectory must be used within a TrajectoryProvider');
  }
  return context;
}

// Trajectory operations
export function useTrajectoryOperations() {
  const { addTrajectory, removeTrajectory, updateTrajectory } = useTrajectory();

  const createVehicleTrajectory = (datasetId: string, config?: Partial<TrajectoryConfig>) => {
    const trajectory: TrajectoryLayer = {
      id: `trajectory-${Date.now()}`,
      datasetId,
      type: 'trajectory',
      config: {
        latField: config?.latField || 'latitude',
        lngField: config?.lngField || 'longitude',
        timestampField: config?.timestampField || 'timestamp',
        idField: config?.idField || 'vehicle_id',
        colorField: config?.colorField,
        thickness: config?.thickness || 2,
        opacity: config?.opacity || 0.8
      }
    };
    addTrajectory(trajectory);
    return trajectory;
  };

  const createAssetMovement = (datasetId: string, config?: Partial<TrajectoryConfig>) => {
    const trajectory: TrajectoryLayer = {
      id: `trajectory-${Date.now()}`,
      datasetId,
      type: 'trajectory',
      config: {
        latField: config?.latField || 'lat',
        lngField: config?.lngField || 'lng',
        timestampField: config?.timestampField || 'time',
        idField: config?.idField || 'asset_id',
        thickness: 2,
        opacity: 0.8
      }
    };
    addTrajectory(trajectory);
    return trajectory;
  };

  const setTrajectoryThickness = (id: string, thickness: number) => {
    const trajectory = useTrajectory().getTrajectory(id);
    if (trajectory) {
      updateTrajectory(id, {
        config: { ...trajectory.config, thickness }
      });
    }
  };

  const setTrajectoryOpacity = (id: string, opacity: number) => {
    const trajectory = useTrajectory().getTrajectory(id);
    if (trajectory) {
      updateTrajectory(id, {
        config: { ...trajectory.config, opacity }
      });
    }
  };

  const deleteTrajectory = (id: string) => {
    removeTrajectory(id);
  };

  return {
    createVehicleTrajectory,
    createAssetMovement,
    setTrajectoryThickness,
    setTrajectoryOpacity,
    deleteTrajectory
  };
}
