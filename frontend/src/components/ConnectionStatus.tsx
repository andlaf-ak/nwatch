import React from 'react';
import { ConnectionStatus as ConnectionStatusType } from '../hooks/useWebSocket';

/**
 * Props for the ConnectionStatus component.
 */
export interface ConnectionStatusProps {
  status: ConnectionStatusType;
}

/**
 * Configuration for status display including label and color.
 */
interface StatusConfig {
  label: string;
  color: string;
  bgColor: string;
}

/**
 * Maps connection status to display configuration.
 */
const statusConfigs: Record<ConnectionStatusType, StatusConfig> = {
  connected: {
    label: 'Connected',
    color: 'var(--status-completed)',
    bgColor: 'rgba(16, 185, 129, 0.1)',
  },
  disconnected: {
    label: 'Disconnected',
    color: 'var(--status-failed)',
    bgColor: 'rgba(239, 68, 68, 0.1)',
  },
  connecting: {
    label: 'Reconnecting...',
    color: 'var(--status-in-progress)',
    bgColor: 'rgba(245, 158, 11, 0.1)',
  },
};

/**
 * ConnectionStatus displays the current WebSocket connection state.
 * Shows a colored indicator dot and status text.
 */
export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ status }) => {
  const config = statusConfigs[status];

  const containerStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 16px',
    borderRadius: '20px',
    backgroundColor: config.bgColor,
    fontSize: '14px',
    fontWeight: 500,
  };

  const dotStyles: React.CSSProperties = {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    backgroundColor: config.color,
  };

  const labelStyles: React.CSSProperties = {
    color: config.color,
  };

  // Add pulse class for connecting state
  const dotClassName = status === 'connecting' ? 'pulse' : '';

  return (
    <div
      data-testid="connection-status"
      data-status={status}
      style={containerStyles}
    >
      <span
        className={dotClassName}
        style={dotStyles}
        aria-hidden="true"
      />
      <span style={labelStyles}>{config.label}</span>
    </div>
  );
};

export default ConnectionStatus;
