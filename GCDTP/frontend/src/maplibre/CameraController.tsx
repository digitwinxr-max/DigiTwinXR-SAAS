/**
 * Camera Controller
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { CameraState } from './maplibre_types';

interface CameraContextValue {
  camera: CameraState;
  setCamera: (camera: CameraState) => void;
  flyTo: (center: [number, number], zoom?: number, bearing?: number, pitch?: number) => void;
  panBy: (dx: number, dy: number) => void;
  zoomBy: (delta: number) => void;
  rotateBy: (bearing: number) => void;
  tiltBy: (pitch: number) => void;
  resetCamera: () => void;
  getCameraHistory: () => CameraState[];
}

const defaultCamera: CameraState = {
  center: [0, 0],
  zoom: 2,
  bearing: 0,
  pitch: 0
};

const CameraContext = createContext<CameraContextValue | undefined>(undefined);

interface CameraProviderProps {
  children: ReactNode;
}

export function CameraProvider({ children }: CameraProviderProps) {
  const [camera, setCamera] = useState<CameraState>(defaultCamera);
  const [history, setHistory] = useState<CameraState[]>([defaultCamera]);

  const flyTo = (center: [number, number], zoom?: number, bearing?: number, pitch?: number) => {
    const newCamera: CameraState = {
      center,
      zoom: zoom ?? camera.zoom,
      bearing: bearing ?? camera.bearing,
      pitch: pitch ?? camera.pitch
    };
    setCamera(newCamera);
    setHistory(prev => [...prev, newCamera]);
  };

  const panBy = (dx: number, dy: number) => {
    const newCenter: [number, number] = [
      camera.center[0] + dx,
      camera.center[1] + dy
    ];
    flyTo(newCenter);
  };

  const zoomBy = (delta: number) => {
    const newZoom = Math.max(0, Math.min(22, camera.zoom + delta));
    flyTo(camera.center, newZoom);
  };

  const rotateBy = (bearing: number) => {
    flyTo(camera.center, camera.zoom, bearing, camera.pitch);
  };

  const tiltBy = (pitch: number) => {
    const newPitch = Math.max(0, Math.min(85, pitch));
    flyTo(camera.center, camera.zoom, camera.bearing, newPitch);
  };

  const resetCamera = () => {
    setCamera(defaultCamera);
    setHistory(prev => [...prev, defaultCamera]);
  };

  const getCameraHistory = () => history;

  const value: CameraContextValue = {
    camera,
    setCamera,
    flyTo,
    panBy,
    zoomBy,
    rotateBy,
    tiltBy,
    resetCamera,
    getCameraHistory
  };

  return (
    <CameraContext.Provider value={value}>
      {children}
    </CameraContext.Provider>
  );
}

export function useCamera() {
  const context = useContext(CameraContext);
  if (!context) {
    throw new Error('useCamera must be used within a CameraProvider');
  }
  return context;
}

// Camera controls
export function useCameraControls() {
  const { flyTo, zoomBy, resetCamera } = useCamera();

  return {
    zoomIn: () => zoomBy(1),
    zoomOut: () => zoomBy(-1),
    resetView: resetCamera,
    goHome: () => flyTo([0, 0], 2),
    goToLocation: (lng: number, lat: number, zoom?: number) => {
      flyTo([lng, lat], zoom);
    }
  };
}

// Bookmark camera positions
interface CameraBookmark {
  id: string;
  name: string;
  camera: CameraState;
}

export function useCameraBookmarks() {
  const [bookmarks, setBookmarks] = useState<CameraBookmark[]>([]);
  const { flyTo } = useCamera();

  const saveBookmark = (name: string, camera: CameraState) => {
    const bookmark: CameraBookmark = {
      id: `bookmark-${Date.now()}`,
      name,
      camera
    };
    setBookmarks(prev => [...prev, bookmark]);
    return bookmark;
  };

  const loadBookmark = (id: string) => {
    const bookmark = bookmarks.find(b => b.id === id);
    if (bookmark) {
      flyTo(bookmark.camera.center, bookmark.camera.zoom, bookmark.camera.bearing, bookmark.camera.pitch);
    }
  };

  const deleteBookmark = (id: string) => {
    setBookmarks(prev => prev.filter(b => b.id !== id));
  };

  return {
    bookmarks,
    saveBookmark,
    loadBookmark,
    deleteBookmark
  };
}
