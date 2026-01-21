import React, { useEffect, useState } from 'react';
import { Step, StepStatus } from '../types/step';
import '../styles/animations.css';

/**
 * Props for the StepCard component.
 */
export interface StepCardProps {
  step: Step;
  isPulsing: boolean;
}

/**
 * Maps step status to display color name.
 */
const statusColorMap: Record<StepStatus, string> = {
  pending: 'gray',
  in_progress: 'yellow',
  completed: 'green',
  failed: 'red',
  skipped: 'blue',
};

/**
 * Maps status color names to actual CSS color values.
 */
const colorValues: Record<string, { background: string; text: string }> = {
  gray: { background: '#9CA3AF', text: '#FFFFFF' },
  yellow: { background: '#F59E0B', text: '#000000' },
  green: { background: '#10B981', text: '#FFFFFF' },
  red: { background: '#EF4444', text: '#FFFFFF' },
  blue: { background: '#3B82F6', text: '#FFFFFF' },
};

/**
 * Formats status text for display.
 */
const formatStatus = (status: StepStatus): string => {
  return status.replace('_', ' ').toUpperCase();
};

/**
 * StepCard displays a single workflow step with status indication.
 * Shows task ID, phase name, and a color-coded status badge.
 */
export const StepCard: React.FC<StepCardProps> = ({ step, isPulsing }) => {
  const [isDarkMode, setIsDarkMode] = useState(true);

  useEffect(() => {
    const checkTheme = () => {
      const theme = document.documentElement.dataset.theme;
      setIsDarkMode(theme !== 'light');
    };
    checkTheme();

    // Watch for theme changes
    const observer = new MutationObserver(checkTheme);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme'],
    });
    return () => observer.disconnect();
  }, []);

  const colorName = statusColorMap[step.status];
  const colors = colorValues[colorName];

  const cardStyles: React.CSSProperties = {
    border: `1px solid ${isDarkMode ? '#334155' : '#E2E8F0'}`,
    borderRadius: '8px',
    padding: '16px',
    backgroundColor: isDarkMode ? '#1E293B' : '#F1F5F9',
    boxShadow: `0 1px 3px ${isDarkMode ? 'rgba(0,0,0,0.3)' : 'rgba(0,0,0,0.1)'}`,
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    width: '100%',
    maxWidth: '400px',
    minWidth: '280px',
    boxSizing: 'border-box',
  };

  const headerStyles: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    flexWrap: 'wrap',
    gap: '8px',
  };

  const taskIdStyles: React.CSSProperties = {
    fontSize: '16px',
    fontWeight: 600,
    color: isDarkMode ? '#FFFFFF' : '#0F172A',
    margin: 0,
    wordBreak: 'break-word',
  };

  const phaseStyles: React.CSSProperties = {
    fontSize: '14px',
    color: isDarkMode ? '#94A3B8' : '#64748B',
    margin: 0,
  };

  const descriptionStyles: React.CSSProperties = {
    fontSize: '14px',
    fontWeight: 600,
    color: isDarkMode ? '#00FFFF' : '#000000',
    margin: '8px 0 0 0',
    lineHeight: '1.4',
    wordBreak: 'break-word',
  };

  const badgeStyles: React.CSSProperties = {
    display: 'inline-block',
    padding: '4px 12px',
    borderRadius: '9999px',
    fontSize: '12px',
    fontWeight: 500,
    backgroundColor: colors.background,
    color: colors.text,
    whiteSpace: 'nowrap',
  };

  return (
    <div
      data-testid={`step-card step-card-${step.taskId}`}
      className={isPulsing ? 'pulse' : ''}
      style={cardStyles}
    >
      <div style={headerStyles}>
        <div>
          <p data-testid="task-id" style={taskIdStyles}>
            {step.taskId}
          </p>
          <p data-testid="phase-name" style={phaseStyles}>
            {step.phase}
          </p>
        </div>
        <span
          data-testid="status-badge"
          data-color={colorName}
          style={badgeStyles}
        >
          {formatStatus(step.status)}
        </span>
      </div>
      <p data-testid="description" style={descriptionStyles}>
        {step.description}
      </p>
    </div>
  );
};

export default StepCard;
