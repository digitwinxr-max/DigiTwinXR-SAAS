import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import eventClient, { subscribe, handleEvent, EVENT_TYPES } from './eventClient';

describe('EventClient', () => {
  beforeEach(() => {
    eventClient.clearCache();
  });

  describe('Event Types', () => {
    it('should have all required event types', () => {
      expect(EVENT_TYPES.MEASUREMENT_CREATED).toBe('measurement.created');
      expect(EVENT_TYPES.THRESHOLD_EVALUATED).toBe('threshold.evaluated');
      expect(EVENT_TYPES.EVENT_CREATED).toBe('event.created');
      expect(EVENT_TYPES.EVENT_RESOLVED).toBe('event.resolved');
      expect(EVENT_TYPES.HEALTH_UPDATED).toBe('health.updated');
      expect(EVENT_TYPES.ASSET_UPDATED).toBe('asset.updated');
    });
  });

  describe('Subscribe', () => {
    it('should call callback when event is handled', () => {
      const callback = vi.fn();
      const event = {
        event_id: 'test-1',
        event_type: 'event.created',
        timestamp: new Date().toISOString(),
        source: 'TestService',
        payload: {},
      };

      const unsubscribe = subscribe(['event.created'], callback);
      handleEvent(event);

      expect(callback).toHaveBeenCalledTimes(1);
      expect(callback).toHaveBeenCalledWith(expect.objectContaining({
        event_id: 'test-1',
        event_type: 'event.created',
      }));

      unsubscribe();
    });

    it('should call callback for multiple event types', () => {
      const callback = vi.fn();
      const event1 = { event_id: '1', event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T' };
      const event2 = { event_id: '2', event_type: 'event.resolved', timestamp: new Date().toISOString(), source: 'T' };
      const event3 = { event_id: '3', event_type: 'health.updated', timestamp: new Date().toISOString(), source: 'T' };

      const unsubscribe = subscribe(
        ['event.created', 'event.resolved'],
        callback
      );

      handleEvent(event1);
      handleEvent(event2);
      handleEvent(event3);

      expect(callback).toHaveBeenCalledTimes(2);

      unsubscribe();
    });

    it('should filter by asset_id', () => {
      const callback = vi.fn();
      const event1 = { event_id: '1', event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T', asset_id: 'asset-1' };
      const event2 = { event_id: '2', event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T', asset_id: 'asset-2' };

      const unsubscribe = subscribe(['event.created'], callback, { asset_id: 'asset-1' });

      handleEvent(event1);
      handleEvent(event2);

      expect(callback).toHaveBeenCalledTimes(1);

      unsubscribe();
    });

    it('should unsubscribe correctly', () => {
      const callback = vi.fn();
      const event = { event_id: '1', event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T' };

      const unsubscribe = subscribe(['event.created'], callback);

      handleEvent(event);
      expect(callback).toHaveBeenCalledTimes(1);

      unsubscribe();

      handleEvent(event);
      expect(callback).toHaveBeenCalledTimes(1);
    });
  });

  describe('Deduplication', () => {
    it('should skip duplicate events with same event_id', () => {
      const callback = vi.fn();
      const event = { event_id: 'dup-1', event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T' };

      const unsubscribe = subscribe(['event.created'], callback);

      handleEvent(event);
      handleEvent(event);
      handleEvent(event);

      expect(callback).toHaveBeenCalledTimes(1);

      unsubscribe();
    });

    it('should allow same event type with different IDs', () => {
      const callback = vi.fn();
      const event1 = { event_id: 'id-1', event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T' };
      const event2 = { event_id: 'id-2', event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T' };

      const unsubscribe = subscribe(['event.created'], callback);

      handleEvent(event1);
      handleEvent(event2);

      expect(callback).toHaveBeenCalledTimes(2);

      unsubscribe();
    });
  });

  describe('Event Immutability', () => {
    it('should freeze events before passing to callback', () => {
      const callback = vi.fn();
      const event = { event_id: 'test-1', event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T', payload: { value: 1 } };

      const unsubscribe = subscribe(['event.created'], callback);

      handleEvent(event);

      const receivedEvent = callback.mock.calls[0][0];
      expect(Object.isFrozen(receivedEvent)).toBe(true);

      unsubscribe();
    });

    it('should prevent modification of received events', () => {
      const callback = vi.fn();
      const event = { event_id: 'test-1', event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T' };

      const unsubscribe = subscribe(['event.created'], callback);

      handleEvent(event);

      const receivedEvent = callback.mock.calls[0][0];
      
      expect(() => {
        receivedEvent.event_id = 'modified';
      }).toThrow();

      unsubscribe();
    });
  });

  describe('Event Cache', () => {
    it('should cache events', () => {
      const event = { event_id: 'cache-1', event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T' };
      handleEvent(event);

      const cached = eventClient.getCachedEvents('event.created');
      expect(cached.length).toBe(1);
      expect(cached[0].event_id).toBe('cache-1');
    });

    it('should limit cache size to 100 events', () => {
      for (let i = 0; i < 150; i++) {
        handleEvent({ event_id: `cache-${i}`, event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T' });
      }

      const cached = eventClient.getCachedEvents('event.created');
      expect(cached.length).toBeLessThanOrEqual(100);
    });

    it('should clear cache', () => {
      handleEvent({ event_id: '1', event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T' });
      handleEvent({ event_id: '2', event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T' });

      expect(eventClient.getCachedEvents().length).toBe(2);

      eventClient.clearCache();

      expect(eventClient.getCachedEvents().length).toBe(0);
    });

    it('should filter cached events by type', () => {
      handleEvent({ event_id: '1', event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T' });
      handleEvent({ event_id: '2', event_type: 'event.resolved', timestamp: new Date().toISOString(), source: 'T' });
      handleEvent({ event_id: '3', event_type: 'health.updated', timestamp: new Date().toISOString(), source: 'T' });

      const eventCreated = eventClient.getCachedEvents('event.created');
      expect(eventCreated.length).toBe(1);
      expect(eventCreated[0].event_id).toBe('1');
    });
  });

  describe('Event Normalization', () => {
    it('should normalize event timestamps', () => {
      const callback = vi.fn();
      const event = { 
        event_id: 'norm-1', 
        event_type: 'event.created', 
        timestamp: '2026-06-16T10:00:00Z', 
        source: 'T',
        asset_id: null,
        sensor_id: null,
      };

      const unsubscribe = subscribe(['event.created'], callback);
      handleEvent(event);

      const received = callback.mock.calls[0][0];
      expect(received.timestamp).toBeInstanceOf(Date);

      unsubscribe();
    });

    it('should handle missing payload gracefully', () => {
      const callback = vi.fn();
      const event = { 
        event_id: 'norm-2', 
        event_type: 'event.created', 
        timestamp: '2026-06-16T10:00:00Z', 
        source: 'T',
      };

      const unsubscribe = subscribe(['event.created'], callback);
      handleEvent(event);

      const received = callback.mock.calls[0][0];
      expect(received.payload).toEqual({});

      unsubscribe();
    });
  });

  describe('Out of Order Events', () => {
    it('should handle events arriving out of order', () => {
      const callback = vi.fn();
      
      const unsubscribe = subscribe(['event.created'], callback);

      // Events might arrive in any order
      handleEvent({ event_id: '3', event_type: 'event.created', timestamp: '2026-06-16T10:03:00Z', source: 'T' });
      handleEvent({ event_id: '1', event_type: 'event.created', timestamp: '2026-06-16T10:01:00Z', source: 'T' });
      handleEvent({ event_id: '2', event_type: 'event.created', timestamp: '2026-06-16T10:02:00Z', source: 'T' });

      expect(callback).toHaveBeenCalledTimes(3);

      unsubscribe();
    });
  });

  describe('Error Handling', () => {
    it('should catch errors in callbacks', () => {
      const errorCallback = vi.fn(() => {
        throw new Error('Test error');
      });
      const normalCallback = vi.fn();

      const unsubscribe1 = subscribe(['event.created'], errorCallback);
      const unsubscribe2 = subscribe(['event.created'], normalCallback);

      handleEvent({ event_id: 'err-1', event_type: 'event.created', timestamp: new Date().toISOString(), source: 'T' });

      // Normal callback should still be called
      expect(normalCallback).toHaveBeenCalledTimes(1);

      unsubscribe1();
      unsubscribe2();
    });
  });

  describe('Subscription Management', () => {
    it('should return correct subscription count', () => {
      expect(eventClient.getSubscriptionCount()).toBe(0);

      const unsub1 = subscribe(['event.created'], vi.fn());
      expect(eventClient.getSubscriptionCount()).toBe(1);

      const unsub2 = subscribe(['event.resolved'], vi.fn());
      expect(eventClient.getSubscriptionCount()).toBe(2);

      unsub1();
      expect(eventClient.getSubscriptionCount()).toBe(1);

      unsub2();
      expect(eventClient.getSubscriptionCount()).toBe(0);
    });
  });
});