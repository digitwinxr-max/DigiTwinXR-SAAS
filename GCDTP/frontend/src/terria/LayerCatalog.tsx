/**
 * Layer Catalog Component
 */

import React, { useState } from 'react';
import type { CatalogItem, LayerCatalog as LayerCatalogType } from './terria_types';

interface LayerCatalogProps {
  catalogs: LayerCatalogType[];
  onItemSelect?: (item: CatalogItem) => void;
  onItemToggle?: (item: CatalogItem) => void;
}

export function LayerCatalog({ catalogs, onItemSelect, onItemToggle }: LayerCatalogProps) {
  const [expandedCatalogs, setExpandedCatalogs] = useState<Set<string>>(new Set());

  const toggleCatalog = (catalogId: string) => {
    setExpandedCatalogs(prev => {
      const next = new Set(prev);
      if (next.has(catalogId)) {
        next.delete(catalogId);
      } else {
        next.add(catalogId);
      }
      return next;
    });
  };

  return (
    <div className="layer-catalog">
      {catalogs.map(catalog => (
        <div key={catalog.id} className="catalog-group">
          <div 
            className="catalog-header"
            onClick={() => toggleCatalog(catalog.id)}
          >
            <span className="catalog-icon">
              {expandedCatalogs.has(catalog.id) ? '▼' : '▶'}
            </span>
            <span className="catalog-name">{catalog.name}</span>
            <span className="catalog-count">
              {catalog.items.length} items
            </span>
          </div>
          
          {expandedCatalogs.has(catalog.id) && (
            <div className="catalog-items">
              {catalog.items.map(item => (
                <LayerItemRow
                  key={item.id}
                  item={item}
                  onSelect={onItemSelect}
                  onToggle={onItemToggle}
                />
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

interface LayerItemRowProps {
  item: CatalogItem;
  onSelect?: (item: CatalogItem) => void;
  onToggle?: (item: CatalogItem) => void;
}

function LayerItemRow({ item, onSelect, onToggle }: LayerItemRowProps) {
  return (
    <div className="layer-item-row">
      <input
        type="checkbox"
        checked={item.isEnabled}
        onChange={() => onToggle?.(item)}
        className="layer-checkbox"
      />
      <div 
        className="layer-info"
        onClick={() => onSelect?.(item)}
      >
        <span className="layer-name">{item.name}</span>
        <span className="layer-type">{item.type}</span>
      </div>
    </div>
  );
}

// Layer list component
interface LayerListProps {
  items: CatalogItem[];
  selectedId?: string;
  onSelect?: (item: CatalogItem) => void;
}

export function LayerList({ items, selectedId, onSelect }: LayerListProps) {
  return (
    <div className="layer-list">
      {items.map(item => (
        <div
          key={item.id}
          className={`layer-list-item ${selectedId === item.id ? 'selected' : ''}`}
          onClick={() => onSelect?.(item)}
        >
          <span className="layer-icon">
            {item.isEnabled ? '●' : '○'}
          </span>
          <span className="layer-name">{item.name}</span>
        </div>
      ))}
    </div>
  );
}

// Search layers
interface LayerSearchProps {
  items: CatalogItem[];
  onFilter: (filtered: CatalogItem[]) => void;
}

export function LayerSearch({ items, onFilter }: LayerSearchProps) {
  const [query, setQuery] = useState('');

  const handleSearch = (value: string) => {
    setQuery(value);
    if (!value.trim()) {
      onFilter(items);
      return;
    }
    const filtered = items.filter(item => 
      item.name.toLowerCase().includes(value.toLowerCase()) ||
      item.description?.toLowerCase().includes(value.toLowerCase())
    );
    onFilter(filtered);
  };

  return (
    <div className="layer-search">
      <input
        type="text"
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="Search layers..."
        className="search-input"
      />
    </div>
  );
}
