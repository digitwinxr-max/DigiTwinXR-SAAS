/**
 * useSystemEvents - Standardized event hook for GCDTP
 * 
 * Replaces useEventBus with standardized event handling.
 * Features:
 * - Subscribe to specific event types
 * - Filter by asset_id
 * - Automatic cleanup on unmount
 * - Event consistency handling
 */

import { useEffect, useCallback, useRef, useState } from 'react';
import eventClient, { EVENT_TYPES } from '../events/eventClient';

/**
 * Hook to subscribe to system events
 * 
 * @param {string[]} eventTypes - Array of event types to subscribe to
 * @param {Function} callback - Callback function called with event
 * @param {Object} options - Subscription options
 * @param {string} options.asset_id - Filter by asset ID
 * @param {string} options.sensor_id - Filter by sensor ID
 * 
 * @returns {Object} Event state and utilities
 */
export function useSystemEvents(eventTypes, callback, options = {}) {
  const callbackRef = useRef(callback);
  const optionsRef = useRef(options);
  const [lastEvent, setLastEvent] = useState(null);
  
  // Update refs when they change
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);
  
  useEffect(() => {
    optionsRef.current = options;
  }, [options]);
  
  // Subscribe to events
  useEffect(() => {
    if (!eventTypes || eventTypes.length === 0) {
      return;
    }
    
    const wrappedCallback = (event) => {
      setLastEvent(event);
      callbackRef.current(event);
    };
    
    const unsubscribe = eventClient.subscribe(
      eventTypes,
      wrappedCallback,
      {
        asset_id: optionsRef.current?.asset_id,
        sensor_id: optionsRef.current?.sensor_id,
      }
    );
    
    // Cleanup on unmount
    return () => {
      unsubscribe();
    };
  }, [eventTypes]);
  
  // Get cached events
  const getCachedEvents = useCallback((eventType, limit) => {
    return eventClient.getCachedEvents(eventType, limit);
  }, []);
  
  return {
    lastEvent,
    getCachedEvents,
    subscribe: eventClient.subscribe,
    handleEvent: eventClient.handleEvent,
  };
}

/**
 * Hook to subscribe to all events for a specific asset
 * 
 * @param {string} assetId - Asset ID to watch
 * @param {Function} callback - Callback function
 * @returns {Object} Event state
 */
export function useAssetEvents(assetId, callback) {
  const callbackRef = useRef(callback);
  const [events, setEvents] = useState([]);
  
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);
  
  useEffect(() => {
    if (!assetId) {
      return;
    }
    
    const wrappedCallback = (event) => {
      setEvents(prev => {
        // Events may arrive out of order, sort by timestamp
        const updated = [...prev, event];
        return updated.sort((a, b) => a.timestamp - b.timestamp);
      });
      callbackRef.current(event);
    };
    
    const unsubscribe = eventClient.subscribe(
      Object.values(EVENT_TYPES),
      wrappedCallback,
      { asset_id: assetId }
    );
    
    return () => {
      unsubscribe();
    };
  }, [assetId]);
  
  return { events };
}

/**
 * Hook to watch specific event types
 * 
 * @param {string|string[]} types - Event type(s) to watch
 * @returns {Object} Event state
 */
export function useEventWatch(types) {
  const typesRef = useRef(types);
  const [events, setEvents] = useState([]);
  
  useEffect(() => {
    typesRef.current = types;
  }, [types]);
  
  useEffect(() => {
    const eventTypes = Array.isArray(types) ? types : [types];
    
    if (eventTypes.length === 0) {
      return;
    }
    
    const wrappedCallback = (event) => {
      setEvents(prev => {
        // Events may arrive out of order
        const updated = [...prev, event];
        return updated.sort((a, b) => a.timestamp - b.timestamp);
      });
    };
    
    const unsubscribe = eventClient.subscribe(eventTypes, wrappedCallback);
    
    return () => {
      unsubscribe();
    };
  }, [types]);
  
  return { events };
}

// Event type constants export
export { EVENT_TYPES };

// Re-export for backwards compatibility
export const useEventBus = useSystemEvents;

export default useSystemEvents;