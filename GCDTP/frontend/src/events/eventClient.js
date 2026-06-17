/**
 * Unified Event Client for GCDTP Frontend
 * 
 * Provides single subscribe() function for all event types.
 * Features:
 * - Normalized event payload parsing
 * - Deduplication using event_id
 * - Internal event cache (last 100 events)
 * - Event immutability enforcement
 */

// Event type constants (must match backend)
export const EVENT_TYPES = {
  MEASUREMENT_CREATED: 'measurement.created',
  THRESHOLD_EVALUATED: 'threshold.evaluated',
  EVENT_CREATED: 'event.created',
  EVENT_RESOLVED: 'event.resolved',
  HEALTH_UPDATED: 'health.updated',
  ASSET_UPDATED: 'asset.updated',
  SENSOR_CREATED: 'sensor.created',
  SENSOR_UPDATED: 'sensor.updated',
  SENSOR_DELETED: 'sensor.deleted',
};

const MAX_CACHE_SIZE = 100;

class EventClient {
  constructor() {
    this.subscribers = new Map();
    this.eventCache = [];
    this.seenEventIds = new Set();
  }

  /**
   * Normalize event payload to standard format
   * @param {Object} event - Raw event from backend
   * @returns {Object} Normalized event
   */
  normalizeEvent(event) {
    return {
      event_id: event.event_id,
      event_type: event.event_type,
      timestamp: new Date(event.timestamp),
      source: event.source,
      correlation_id: event.correlation_id,
      asset_id: event.asset_id,
      sensor_id: event.sensor_id,
      payload: event.payload || {},
    };
  }

  /**
   * Check if event has been seen before (deduplication)
   * @param {string} eventId - Event ID
   * @returns {boolean} True if already seen
   */
  isDuplicate(eventId) {
    return this.seenEventIds.has(eventId);
  }

  /**
   * Mark event as seen
   * @param {string} eventId - Event ID
   */
  markAsSeen(eventId) {
    this.seenEventIds.add(eventId);
    
    // Trim seen IDs if cache exceeds limit
    if (this.seenEventIds.size > MAX_CACHE_SIZE) {
      const iterator = this.seenEventIds.values();
      this.seenEventIds.delete(iterator.next().value);
    }
  }

  /**
   * Add event to internal cache
   * @param {Object} event - Normalized event
   */
  addToCache(event) {
    this.eventCache.push(event);
    
    // Trim cache if exceeds limit
    if (this.eventCache.length > MAX_CACHE_SIZE) {
      const removed = this.eventCache.shift();
      if (removed && removed.event_id) {
        this.seenEventIds.delete(removed.event_id);
      }
    }
  }

  /**
   * Subscribe to events
   * 
   * @param {string|string[]} eventTypes - Event type(s) to subscribe to
   * @param {Function} callback - Callback function called with normalized event
   * @param {Object} options - Subscription options
   * @param {string} options.asset_id - Filter by asset ID
   * @param {string} options.sensor_id - Filter by sensor ID
   * 
   * @returns {Function} Unsubscribe function
   */
  subscribe(eventTypes, callback, options = {}) {
    const types = Array.isArray(eventTypes) ? eventTypes : [eventTypes];
    const subscriptionId = Symbol();
    
    const subscription = {
      id: subscriptionId,
      types,
      callback: this.wrapCallback(callback),
      assetId: options.asset_id,
      sensorId: options.sensor_id,
    };
    
    this.subscribers.set(subscriptionId, subscription);
    
    // Return unsubscribe function
    return () => {
      this.subscribers.delete(subscriptionId);
    };
  }

  /**
   * Wrap callback to handle deduplication and immutability
   * @param {Function} callback - Original callback
   * @returns {Function} Wrapped callback
   */
  wrapCallback(callback) {
    return (event) => {
      // Normalize event
      const normalized = this.normalizeEvent(event);
      
      // Skip duplicates
      if (this.isDuplicate(normalized.event_id)) {
        return;
      }
      
      // Mark as seen and cache
      this.markAsSeen(normalized.event_id);
      this.addToCache(normalized);
      
      // Make event immutable (frozen)
      const frozen = Object.freeze({ ...normalized });
      
      // Call original callback
      try {
        callback(frozen);
      } catch (error) {
        console.error('Error in event callback:', error);
      }
    };
  }

  /**
   * Handle incoming event from any source
   * @param {Object} event - Raw event from backend
   */
  handleEvent(event) {
    // Normalize and deduplicate
    const normalized = this.normalizeEvent(event);
    
    if (this.isDuplicate(normalized.event_id)) {
      return; // Skip duplicate
    }
    
    this.markAsSeen(normalized.event_id);
    this.addToCache(normalized);
    
    // Notify matching subscribers
    for (const subscription of this.subscribers.values()) {
      // Check event type match
      if (!subscription.types.includes(normalized.event_type)) {
        continue;
      }
      
      // Check asset_id filter
      if (subscription.assetId && normalized.asset_id !== subscription.assetId) {
        continue;
      }
      
      // Check sensor_id filter
      if (subscription.sensorId && normalized.sensor_id !== subscription.sensorId) {
        continue;
      }
      
      // Make event immutable and deliver
      const frozen = Object.freeze({ ...normalized });
      
      try {
        subscription.callback(frozen);
      } catch (error) {
        console.error('Error in event subscriber:', error);
      }
    }
  }

  /**
   * Get cached events
   * @param {string} eventType - Optional filter by event type
   * @param {number} limit - Maximum number of events
   * @returns {Object[]} Cached events (frozen)
   */
  getCachedEvents(eventType = null, limit = 100) {
    let events = this.eventCache;
    
    if (eventType) {
      events = events.filter(e => e.event_type === eventType);
    }
    
    return events
      .slice(-limit)
      .map(e => Object.freeze({ ...e }));
  }

  /**
   * Clear event cache
   */
  clearCache() {
    this.eventCache = [];
    this.seenEventIds.clear();
  }

  /**
   * Get subscription count
   * @returns {number} Number of active subscriptions
   */
  getSubscriptionCount() {
    return this.subscribers.size;
  }
}

// Singleton instance
const eventClient = new EventClient();

export default eventClient;

// Convenience exports
export const subscribe = (types, callback, options) => 
  eventClient.subscribe(types, callback, options);

export const handleEvent = (event) => 
  eventClient.handleEvent(event);

export const getCachedEvents = (type, limit) => 
  eventClient.getCachedEvents(type, limit);

export const clearCache = () => 
  eventClient.clearCache();