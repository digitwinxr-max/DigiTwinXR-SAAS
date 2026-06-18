/**
 * Story Map Manager
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { StoryChapter, StoryMap, CameraPosition, LayerState } from './terria_types';

interface StoryContextValue {
  stories: StoryMap[];
  currentStory: StoryMap | null;
  currentChapter: StoryChapter | null;
  createStory: (title: string, description?: string) => StoryMap;
  addChapter: (storyId: string, chapter: Omit<StoryChapter, 'id'>) => void;
  updateChapter: (storyId: string, chapterId: string, updates: Partial<StoryChapter>) => void;
  deleteChapter: (storyId: string, chapterId: string) => void;
  deleteStory: (storyId: string) => void;
  setCurrentStory: (storyId: string) => void;
  setCurrentChapter: (chapterId: string) => void;
  getNextChapter: () => StoryChapter | null;
  getPreviousChapter: () => StoryChapter | null;
}

const StoryContext = createContext<StoryContextValue | undefined>(undefined);

interface StoryProviderProps {
  children: ReactNode;
}

export function StoryProvider({ children }: StoryProviderProps) {
  const [stories, setStories] = useState<StoryMap[]>([]);
  const [currentStoryId, setCurrentStoryId] = useState<string | null>(null);
  const [currentChapterId, setCurrentChapterId] = useState<string | null>(null);

  const currentStory = currentStoryId 
    ? stories.find(s => s.id === currentStoryId) || null 
    : null;
  
  const currentChapter = currentStory && currentChapterId
    ? currentStory.chapters.find(c => c.id === currentChapterId) || null
    : null;

  const createStory = (title: string, description?: string): StoryMap => {
    const story: StoryMap = {
      id: `story-${Date.now()}`,
      title,
      description,
      chapters: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    setStories(prev => [...prev, story]);
    return story;
  };

  const addChapter = (storyId: string, chapterData: Omit<StoryChapter, 'id'>) => {
    const chapter: StoryChapter = {
      ...chapterData,
      id: `chapter-${Date.now()}`
    };
    setStories(prev => prev.map(story => {
      if (story.id === storyId) {
        return {
          ...story,
          chapters: [...story.chapters, chapter],
          updatedAt: new Date().toISOString()
        };
      }
      return story;
    }));
  };

  const updateChapter = (storyId: string, chapterId: string, updates: Partial<StoryChapter>) => {
    setStories(prev => prev.map(story => {
      if (story.id === storyId) {
        return {
          ...story,
          chapters: story.chapters.map(chapter =>
            chapter.id === chapterId ? { ...chapter, ...updates } : chapter
          ),
          updatedAt: new Date().toISOString()
        };
      }
      return story;
    }));
  };

  const deleteChapter = (storyId: string, chapterId: string) => {
    setStories(prev => prev.map(story => {
      if (story.id === storyId) {
        return {
          ...story,
          chapters: story.chapters.filter(c => c.id !== chapterId),
          updatedAt: new Date().toISOString()
        };
      }
      return story;
    }));
  };

  const deleteStory = (storyId: string) => {
    setStories(prev => prev.filter(s => s.id !== storyId));
    if (currentStoryId === storyId) {
      setCurrentStoryId(null);
      setCurrentChapterId(null);
    }
  };

  const setCurrentStoryFn = (storyId: string) => {
    setCurrentStoryId(storyId);
    const story = stories.find(s => s.id === storyId);
    if (story && story.chapters.length > 0) {
      setCurrentChapterId(story.chapters[0].id);
    }
  };

  const setCurrentChapterFn = (chapterId: string) => {
    setCurrentChapterId(chapterId);
  };

  const getNextChapter = (): StoryChapter | null => {
    if (!currentStory || !currentChapterId) return null;
    const currentIndex = currentStory.chapters.findIndex(c => c.id === currentChapterId);
    if (currentIndex >= 0 && currentIndex < currentStory.chapters.length - 1) {
      return currentStory.chapters[currentIndex + 1];
    }
    return null;
  };

  const getPreviousChapter = (): StoryChapter | null => {
    if (!currentStory || !currentChapterId) return null;
    const currentIndex = currentStory.chapters.findIndex(c => c.id === currentChapterId);
    if (currentIndex > 0) {
      return currentStory.chapters[currentIndex - 1];
    }
    return null;
  };

  const value: StoryContextValue = {
    stories,
    currentStory,
    currentChapter,
    createStory,
    addChapter,
    updateChapter,
    deleteChapter,
    deleteStory,
    setCurrentStory: setCurrentStoryFn,
    setCurrentChapter: setCurrentChapterFn,
    getNextChapter,
    getPreviousChapter
  };

  return (
    <StoryContext.Provider value={value}>
      {children}
    </StoryContext.Provider>
  );
}

export function useStoryMap() {
  const context = useContext(StoryContext);
  if (!context) {
    throw new Error('useStoryMap must be used within a StoryProvider');
  }
  return context;
}

// Story playback hook
export function useStoryPlayback() {
  const { currentChapter, getNextChapter, getPreviousChapter, setCurrentChapter } = useStoryMap();
  
  return {
    currentChapter,
    playNext: () => {
      const next = getNextChapter();
      if (next) setCurrentChapter(next.id);
    },
    playPrevious: () => {
      const prev = getPreviousChapter();
      if (prev) setCurrentChapter(prev.id);
    },
    hasNext: !!getNextChapter(),
    hasPrevious: !!getPreviousChapter()
  };
}

// Story editor hook
export function useStoryEditor() {
  const { currentStory, addChapter, updateChapter, deleteChapter } = useStoryMap();
  
  return {
    story: currentStory,
    addChapter: (chapter: Omit<StoryChapter, 'id'>) => {
      if (currentStory) {
        addChapter(currentStory.id, chapter);
      }
    },
    updateChapter: (chapterId: string, updates: Partial<StoryChapter>) => {
      if (currentStory) {
        updateChapter(currentStory.id, chapterId, updates);
      }
    },
    deleteChapter: (chapterId: string) => {
      if (currentStory) {
        deleteChapter(currentStory.id, chapterId);
      }
    }
  };
}
