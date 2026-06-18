/**
 * Catalog Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { CatalogItem, DatasetCatalog } from './terria_types';

interface CatalogContextValue {
  catalogItems: CatalogItem[];
  datasetCatalogs: DatasetCatalog[];
  addCatalogItem: (item: CatalogItem) => void;
  removeCatalogItem: (id: string) => void;
  updateCatalogItem: (id: string, updates: Partial<CatalogItem>) => void;
  getCatalogItem: (id: string) => CatalogItem | undefined;
  addDatasetCatalog: (catalog: DatasetCatalog) => void;
  getEnabledItems: () => CatalogItem[];
}

const CatalogContext = createContext<CatalogContextValue | undefined>(undefined);

interface CatalogProviderProps {
  children: ReactNode;
}

export function CatalogProvider({ children }: CatalogProviderProps) {
  const [catalogItems, setCatalogItems] = useState<CatalogItem[]>([]);
  const [datasetCatalogs, setDatasetCatalogs] = useState<DatasetCatalog[]>([]);

  const addCatalogItem = (item: CatalogItem) => {
    setCatalogItems(prev => [...prev, item]);
  };

  const removeCatalogItem = (id: string) => {
    setCatalogItems(prev => prev.filter(item => item.id !== id));
  };

  const updateCatalogItem = (id: string, updates: Partial<CatalogItem>) => {
    setCatalogItems(prev =>
      prev.map(item => item.id === id ? { ...item, ...updates } : item)
    );
  };

  const getCatalogItem = (id: string) => {
    return catalogItems.find(item => item.id === id);
  };

  const addDatasetCatalog = (catalog: DatasetCatalog) => {
    setDatasetCatalogs(prev => [...prev, catalog]);
  };

  const getEnabledItems = () => {
    return catalogItems.filter(item => item.isEnabled);
  };

  const value: CatalogContextValue = {
    catalogItems,
    datasetCatalogs,
    addCatalogItem,
    removeCatalogItem,
    updateCatalogItem,
    getCatalogItem,
    addDatasetCatalog,
    getEnabledItems
  };

  return (
    <CatalogContext.Provider value={value}>
      {children}
    </CatalogContext.Provider>
  );
}

export function useCatalogManager() {
  const context = useContext(CatalogContext);
  if (!context) {
    throw new Error('useCatalogManager must be used within a CatalogProvider');
  }
  return context;
}

// Hook for layer operations
export function useLayerCatalog() {
  const { catalogItems, updateCatalogItem, getEnabledItems } = useCatalogManager();
  
  return {
    layers: catalogItems,
    enabledLayers: getEnabledItems(),
    enableLayer: (id: string) => updateCatalogItem(id, { isEnabled: true }),
    disableLayer: (id: string) => updateCatalogItem(id, { isEnabled: false }),
    toggleLayer: (id: string) => {
      const item = catalogItems.find(i => i.id === id);
      if (item) {
        updateCatalogItem(id, { isEnabled: !item.isEnabled });
      }
    }
  };
}

// Hook for dataset operations
export function useDatasetCatalog() {
  const { datasetCatalogs, addDatasetCatalog } = useCatalogManager();
  
  return {
    catalogs: datasetCatalogs,
    addCatalog: addDatasetCatalog,
    getById: (id: string) => datasetCatalogs.find(c => c.id === id),
    getByCategory: (category: string) => {
      return datasetCatalogs.filter(c => c.categories.includes(category));
    }
  };
}
