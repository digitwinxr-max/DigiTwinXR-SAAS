/**
 * Style Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { MapStyle, ThemeConfig } from './maplibre_types';

interface StyleContextValue {
  currentStyle: MapStyle | null;
  currentTheme: ThemeConfig | null;
  themes: ThemeConfig[];
  setCurrentStyle: (style: MapStyle) => void;
  setCurrentTheme: (theme: ThemeConfig) => void;
  addTheme: (theme: ThemeConfig) => void;
  removeTheme: (id: string) => void;
}

const defaultThemes: ThemeConfig[] = [
  {
    id: 'light',
    name: 'Light',
    primaryColor: '#1976D2',
    secondaryColor: '#424242',
    backgroundColor: '#FFFFFF',
    textColor: '#212121',
    mapStyle: 'https://demotiles.maplibre.org/style.json'
  },
  {
    id: 'dark',
    name: 'Dark',
    primaryColor: '#90CAF9',
    secondaryColor: '#BDBDBD',
    backgroundColor: '#121212',
    textColor: '#FFFFFF',
    mapStyle: 'https://demotiles.maplibre.org/style.json'
  }
];

const StyleContext = createContext<StyleContextValue | undefined>(undefined);

interface StyleProviderProps {
  children: ReactNode;
}

export function StyleProvider({ children }: StyleProviderProps) {
  const [currentStyle, setCurrentStyle] = useState<MapStyle | null>(null);
  const [currentTheme, setCurrentTheme] = useState<ThemeConfig | null>(defaultThemes[0]);
  const [themes, setThemes] = useState<ThemeConfig[]>(defaultThemes);

  const addTheme = (theme: ThemeConfig) => {
    setThemes(prev => [...prev, theme]);
  };

  const removeTheme = (id: string) => {
    setThemes(prev => prev.filter(t => t.id !== id));
  };

  const value: StyleContextValue = {
    currentStyle,
    currentTheme,
    themes,
    setCurrentStyle,
    setCurrentTheme,
    addTheme,
    removeTheme
  };

  return (
    <StyleContext.Provider value={value}>
      {children}
    </StyleContext.Provider>
  );
}

export function useStyle() {
  const context = useContext(StyleContext);
  if (!context) {
    throw new Error('useStyle must be used within a StyleProvider');
  }
  return context;
}

// Style operations
export function useStyleOperations() {
  const { setCurrentStyle, setCurrentTheme } = useStyle();

  const loadStyle = async (url: string) => {
    const response = await fetch(url);
    const style = await response.json();
    setCurrentStyle(style);
    return style;
  };

  const applyTheme = (theme: ThemeConfig) => {
    setCurrentTheme(theme);
    loadStyle(theme.mapStyle);
  };

  const updateLayerVisibility = (layerId: string, visible: boolean) => {
    // Update style visibility
    console.log('Update layer visibility:', layerId, visible);
  };

  const updateLayerOpacity = (layerId: string, opacity: number) => {
    // Update style opacity
    console.log('Update layer opacity:', layerId, opacity);
  };

  return {
    loadStyle,
    applyTheme,
    updateLayerVisibility,
    updateLayerOpacity
  };
}

// Predefined styles
export const PREDEFINED_STYLES = {
  STREET: 'https://demotiles.maplibre.org/style.json',
  SATELLITE: 'https://api.maptiler.com/tiles/satellite-v2/style.json',
  OUTDOOR: 'https://api.maptiler.com/tiles/outdoor-v2/style.json'
};
