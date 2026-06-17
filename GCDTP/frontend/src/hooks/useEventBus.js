import { useState, useEffect, useCallback, createContext, useContext } from 'react';

const EventBusContext = createContext(null);

export function EventBusProvider({ children }) {
  const [listeners, setListeners] = useState({});

  const subscribe = useCallback((event, callback) => {
    setListeners(prev => ({
      ...prev,
      [event]: [...(prev[event] || []), callback],
    }));

    return () => {
      setListeners(prev => ({
        ...prev,
        [event]: (prev[event] || []).filter(cb => cb !== callback),
      }));
    };
  }, []);

  const publish = useCallback((event, data) => {
    const callbacks = listeners[event] || [];
    callbacks.forEach(callback => {
      try {
        callback(data);
      } catch (err) {
        console.error(`Error in event listener for ${event}:`, err);
      }
    });
  }, [listeners]);

  const value = { subscribe, publish };

  return (
    <EventBusContext.Provider value={value}>
      {children}
    </EventBusContext.Provider>
  );
}

export function useEventBus() {
  const context = useContext(EventBusContext);
  if (!context) {
    throw new Error('useEventBus must be used within EventBusProvider');
  }
  return context;
}

export function useEventSubscription(event, callback) {
  const { subscribe } = useEventBus();

  useEffect(() => {
    const unsubscribe = subscribe(event, callback);
    return unsubscribe;
  }, [event, callback, subscribe]);
}

export const EVENTS = {
  EVENT_CREATED: 'event.created',
  EVENT_RESOLVED: 'event.resolved',
  HEALTH_UPDATED: 'health.updated',
  ASSET_UPDATED: 'asset.updated',
  SENSOR_UPDATED: 'sensor.updated',
};

export default useEventBus;