import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Step,
  WebSocketMessage,
  isInitMessage,
  isUpdateMessage,
  isRemoveMessage,
} from '../types/step';

/**
 * Connection status for WebSocket.
 */
export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected';

/**
 * Return type for useWebSocket hook.
 */
export interface UseWebSocketResult {
  steps: Step[];
  connectionStatus: ConnectionStatus;
}

/**
 * Configuration for exponential backoff reconnection.
 */
const RECONNECT_CONFIG = {
  initialDelayMs: 1000,
  maxDelayMs: 30000,
  multiplier: 2,
};

/**
 * Custom hook for WebSocket connection and state management.
 * Handles real-time step updates with automatic reconnection.
 *
 * @param url - WebSocket server URL
 * @returns Object containing steps array and connection status
 */
export function useWebSocket(url: string): UseWebSocketResult {
  const [steps, setSteps] = useState<Step[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');

  // Refs to persist across renders without causing re-renders
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectDelayRef = useRef<number>(RECONNECT_CONFIG.initialDelayMs);
  const mountedRef = useRef<boolean>(true);

  /**
   * Clears any pending reconnect timer.
   */
  const clearReconnectTimer = useCallback(() => {
    if (reconnectTimerRef.current !== null) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  }, []);

  /**
   * Schedules a reconnection attempt with exponential backoff.
   */
  const scheduleReconnect = useCallback((connect: () => void) => {
    if (!mountedRef.current) return;

    clearReconnectTimer();

    const delay = reconnectDelayRef.current;
    reconnectTimerRef.current = setTimeout(() => {
      if (mountedRef.current) {
        connect();
      }
    }, delay);

    // Increase delay for next attempt with exponential backoff
    reconnectDelayRef.current = Math.min(
      reconnectDelayRef.current * RECONNECT_CONFIG.multiplier,
      RECONNECT_CONFIG.maxDelayMs
    );
  }, [clearReconnectTimer]);

  /**
   * Resets reconnect delay to initial value (called on successful connection).
   */
  const resetReconnectDelay = useCallback(() => {
    reconnectDelayRef.current = RECONNECT_CONFIG.initialDelayMs;
  }, []);

  /**
   * Handles incoming WebSocket messages.
   */
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      console.log('WebSocket message received:', message.type, message);

      if (isInitMessage(message)) {
        // Initialize with all steps from server
        console.log('Init: setting', message.steps.length, 'steps');
        setSteps(message.steps);
      } else if (isUpdateMessage(message)) {
        // Update or add a single step
        console.log('Update: step', message.step.taskId, 'status:', message.step.status);
        setSteps((prevSteps) => {
          const existingIndex = prevSteps.findIndex(
            (s) => s.taskId === message.step.taskId
          );

          if (existingIndex >= 0) {
            // Update existing step
            const newSteps = [...prevSteps];
            newSteps[existingIndex] = message.step;
            console.log('Updated existing step at index', existingIndex);
            return newSteps;
          } else {
            // Add new step
            console.log('Added new step');
            return [...prevSteps, message.step];
          }
        });
      } else if (isRemoveMessage(message)) {
        // Remove step from list
        console.log('Remove: step', message.taskId);
        setSteps((prevSteps) =>
          prevSteps.filter((s) => s.taskId !== message.taskId)
        );
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;

    /**
     * Creates and configures WebSocket connection.
     */
    const connect = () => {
      if (!mountedRef.current) return;

      // Close existing connection if any
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }

      setConnectionStatus('connecting');

      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mountedRef.current) {
          ws.close();
          return;
        }
        setConnectionStatus('connected');
        resetReconnectDelay();
      };

      ws.onmessage = handleMessage;

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;

        setConnectionStatus('disconnected');
        wsRef.current = null;

        // Schedule reconnection attempt
        scheduleReconnect(connect);
      };
    };

    // Initial connection
    connect();

    // Cleanup on unmount
    return () => {
      mountedRef.current = false;
      clearReconnectTimer();

      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [url, handleMessage, scheduleReconnect, resetReconnectDelay, clearReconnectTimer]);

  return { steps, connectionStatus };
}
