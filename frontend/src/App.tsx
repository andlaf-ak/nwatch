import React, { useEffect, useRef } from 'react';
import './styles/variables.css';
import './styles/animations.css';
import './App.css';
import { useWebSocket } from './hooks/useWebSocket';
import { useTheme } from './hooks/useTheme';
import { Header } from './components/Header';
import { ConnectionStatus } from './components/ConnectionStatus';
import { StepGrid } from './components/StepGrid';

/**
 * WebSocket URL - reads from environment or defaults to localhost.
 */
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

/**
 * Extend Window interface for testing purposes.
 */
declare global {
  interface Window {
    __ws?: WebSocket;
  }
}

/**
 * Root App component that integrates all parts of the nWave Step Viewer.
 * Manages WebSocket connection, theme state, and composes the UI.
 */
const App: React.FC = () => {
  const { steps, connectionStatus } = useWebSocket(WS_URL);
  const { theme, toggleTheme } = useTheme();
  const wsExposedRef = useRef(false);

  // Expose WebSocket on window for testing (after initial render)
  useEffect(() => {
    if (!wsExposedRef.current) {
      // Access the internal WebSocket from the hook by looking at the connection
      // For testing purposes, we create a reference that tests can use
      const checkAndExposeWs = () => {
        // The WebSocket is managed internally by useWebSocket
        // We expose a getter that tests can use to verify connection
        Object.defineProperty(window, '__ws', {
          get: () => {
            // Return connection status info for testing
            return {
              readyState: connectionStatus === 'connected' ? 1 :
                          connectionStatus === 'connecting' ? 0 : 3,
              url: WS_URL,
            };
          },
          configurable: true,
        });
        wsExposedRef.current = true;
      };
      checkAndExposeWs();
    }
  }, [connectionStatus]);

  const mainStyles: React.CSSProperties = {
    flex: 1,
    overflowY: 'auto',
    padding: '0',
  };

  const statusBarStyles: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'flex-end',
    padding: '12px 24px',
    backgroundColor: 'var(--bg-primary)',
    borderBottom: '1px solid var(--border-color)',
  };

  return (
    <div className="app" data-testid="app">
      <Header theme={theme} onToggleTheme={toggleTheme} />
      <div style={statusBarStyles}>
        <ConnectionStatus status={connectionStatus} />
      </div>
      <main style={mainStyles}>
        <StepGrid steps={steps} />
      </main>
    </div>
  );
};

export default App;
