/**
 * Filter Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { FilterConfig, FilterType } from './kepler_types';

interface FilterContextValue {
  filters: FilterConfig[];
  addFilter: (filter: FilterConfig) => void;
  removeFilter: (id: string) => void;
  updateFilter: (id: string, updates: Partial<FilterConfig>) => void;
  getFilter: (id: string) => FilterConfig | undefined;
  clearFilters: () => void;
}

const FilterContext = createContext<FilterContextValue | undefined>(undefined);

interface FilterProviderProps {
  children: ReactNode;
}

export function FilterProvider({ children }: FilterProviderProps) {
  const [filters, setFilters] = useState<FilterConfig[]>([]);

  const addFilter = (filter: FilterConfig) => {
    setFilters(prev => [...prev, filter]);
  };

  const removeFilter = (id: string) => {
    setFilters(prev => prev.filter(f => f.id !== id));
  };

  const updateFilter = (id: string, updates: Partial<FilterConfig>) => {
    setFilters(prev => prev.map(f => f.id === id ? { ...f, ...updates } : f));
  };

  const getFilter = (id: string) => {
    return filters.find(f => f.id === id);
  };

  const clearFilters = () => {
    setFilters([]);
  };

  const value: FilterContextValue = {
    filters,
    addFilter,
    removeFilter,
    updateFilter,
    getFilter,
    clearFilters
  };

  return (
    <FilterContext.Provider value={value}>
      {children}
    </FilterContext.Provider>
  );
}

export function useFilter() {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilter must be used within a FilterProvider');
  }
  return context;
}

// Filter operations
export function useFilterOperations() {
  const { addFilter, removeFilter, updateFilter, clearFilters } = useFilter();

  const createSpatialFilter = (name: string, bounds: [number, number, number, number]) => {
    const filter: FilterConfig = {
      id: `filter-${Date.now()}`,
      name,
      type: FilterType.SPATIAL,
      field: 'geometry',
      value: bounds
    };
    addFilter(filter);
    return filter;
  };

  const createAttributeFilter = (name: string, field: string, value: any) => {
    const filter: FilterConfig = {
      id: `filter-${Date.now()}`,
      name,
      type: FilterType.ATTRIBUTE,
      field,
      value
    };
    addFilter(filter);
    return filter;
  };

  const createTimeFilter = (name: string, field: string, start: string, end: string) => {
    const filter: FilterConfig = {
      id: `filter-${Date.now()}`,
      name,
      type: FilterType.TIME,
      field,
      value: null,
      range: [start, end]
    };
    addFilter(filter);
    return filter;
  };

  const createRangeFilter = (name: string, field: string, min: number, max: number) => {
    const filter: FilterConfig = {
      id: `filter-${Date.now()}`,
      name,
      type: FilterType.RANGE,
      field,
      value: null,
      range: [min, max]
    };
    addFilter(filter);
    return filter;
  };

  const updateFilterValue = (id: string, value: any) => {
    updateFilter(id, { value });
  };

  const updateFilterRange = (id: string, range: [any, any]) => {
    updateFilter(id, { range });
  };

  const deleteFilter = (id: string) => {
    removeFilter(id);
  };

  return {
    createSpatialFilter,
    createAttributeFilter,
    createTimeFilter,
    createRangeFilter,
    updateFilterValue,
    updateFilterRange,
    deleteFilter,
    clearFilters
  };
}
