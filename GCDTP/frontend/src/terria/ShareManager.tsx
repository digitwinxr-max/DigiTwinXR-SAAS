/**
 * Share Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { ShareState, CameraPosition, LayerState } from './terria_types';

interface ShareContextValue {
  shareUrl: string;
  shareState: ShareState | null;
  generateShareUrl: () => string;
  generateShareState: () => ShareState;
  parseShareUrl: (url: string) => ShareState | null;
  saveBookmark: (name: string) => void;
  bookmarks: { name: string; state: ShareState }[];
  loadBookmark: (name: string) => void;
}

const ShareContext = createContext<ShareContextValue | undefined>(undefined);

interface ShareProviderProps {
  children: ReactNode;
  baseUrl?: string;
}

export function ShareProvider({ children, baseUrl = '' }: ShareProviderProps) {
  const [shareState, setShareState] = useState<ShareState | null>(null);
  const [bookmarks, setBookmarks] = useState<{ name: string; state: ShareState }[]>([]);

  const generateShareUrl = (): string => {
    const state = generateShareState();
    setShareState(state);
    const encoded = btoa(JSON.stringify(state));
    return `${baseUrl}?share=${encoded}`;
  };

  const generateShareState = (): ShareState => {
    // Get current state from map
    return {
      camera: null,
      layers: [],
      stories: [],
      time: new Date().toISOString()
    };
  };

  const parseShareUrl = (url: string): ShareState | null => {
    try {
      const params = new URL(url).searchParams;
      const encoded = params.get('share');
      if (!encoded) return null;
      return JSON.parse(atob(encoded));
    } catch {
      return null;
    }
  };

  const saveBookmark = (name: string) => {
    const state = generateShareState();
    setBookmarks(prev => [...prev, { name, state }]);
  };

  const loadBookmark = (name: string) => {
    const bookmark = bookmarks.find(b => b.name === name);
    if (bookmark) {
      setShareState(bookmark.state);
    }
  };

  const value: ShareContextValue = {
    shareUrl: '',
    shareState,
    generateShareUrl,
    generateShareState,
    parseShareUrl,
    saveBookmark,
    bookmarks,
    loadBookmark
  };

  return (
    <ShareContext.Provider value={value}>
      {children}
    </ShareContext.Provider>
  );
}

export function useShare() {
  const context = useContext(ShareContext);
  if (!context) {
    throw new Error('useShare must be used within a ShareProvider');
  }
  return context;
}

// Share button component
interface ShareButtonProps {
  onGenerate?: () => void;
}

export function ShareButton({ onGenerate }: ShareButtonProps) {
  const { generateShareUrl } = useShare();
  const [showModal, setShowModal] = useState(false);
  const [shareUrl, setShareUrl] = useState('');

  const handleShare = () => {
    const url = generateShareUrl();
    setShareUrl(url);
    setShowModal(true);
    onGenerate?.();
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <>
      <button onClick={handleShare} className="share-button">
        Share
      </button>
      
      {showModal && (
        <div className="share-modal">
          <h3>Share This View</h3>
          <input 
            type="text" 
            value={shareUrl} 
            readOnly 
            className="share-url-input"
          />
          <button onClick={copyToClipboard} className="copy-btn">
            Copy
          </button>
          <button onClick={() => setShowModal(false)} className="close-btn">
            Close
          </button>
        </div>
      )}
    </>
  );
}

// Bookmark manager
interface BookmarkManagerProps {
  onLoad?: (state: ShareState) => void;
}

export function BookmarkManager({ onLoad }: BookmarkManagerProps) {
  const { bookmarks, saveBookmark, loadBookmark } = useShare();
  const [newName, setNewName] = useState('');

  const handleSave = () => {
    if (newName.trim()) {
      saveBookmark(newName.trim());
      setNewName('');
    }
  };

  return (
    <div className="bookmark-manager">
      <h4>Camera Bookmarks</h4>
      
      <div className="save-bookmark">
        <input
          type="text"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="Bookmark name"
          className="bookmark-input"
        />
        <button onClick={handleSave} className="save-btn">Save</button>
      </div>
      
      <div className="bookmark-list">
        {bookmarks.map((bookmark, i) => (
          <div key={i} className="bookmark-item">
            <span>{bookmark.name}</span>
            <button onClick={() => {
              loadBookmark(bookmark.name);
              onLoad?.(bookmark.state);
            }}>
              Load
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
