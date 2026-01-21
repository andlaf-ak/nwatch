import React from 'react';
import { Step } from '../types/step';
import { StepCard } from './StepCard';

/**
 * Props for the PhaseRow component.
 */
export interface PhaseRowProps {
  phaseName: string;
  steps: Step[];
  pulsingTaskId: string | null;
}

/**
 * PhaseRow displays a horizontal row of steps for a single phase.
 * Shows the phase label on the left with connecting lines between cards.
 */
export const PhaseRow: React.FC<PhaseRowProps> = ({ phaseName, steps, pulsingTaskId }) => {
  // Sort steps by minorVersion ascending
  const sortedSteps = [...steps].sort((a, b) => a.minorVersion - b.minorVersion);

  const containerStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    marginBottom: '24px',
  };

  const labelStyles: React.CSSProperties = {
    fontSize: '18px',
    fontWeight: 600,
    color: 'var(--text-primary)',
    margin: 0,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  };

  const stepsContainerStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    gap: '0',
    overflowX: 'auto',
    paddingBottom: '8px',
  };

  const stepWrapperStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    flexShrink: 0,
  };

  const connectorStyles: React.CSSProperties = {
    width: '32px',
    height: '2px',
    backgroundColor: 'var(--border-color)',
    flexShrink: 0,
  };

  return (
    <div
      data-testid={`phase-row phase-row-${phaseName}`}
      style={containerStyles}
    >
      <h3 style={labelStyles}>{phaseName}</h3>
      <div style={stepsContainerStyles}>
        {sortedSteps.map((step, index) => (
          <div key={step.taskId} style={stepWrapperStyles}>
            <StepCard
              step={step}
              isPulsing={step.taskId === pulsingTaskId}
            />
            {index < sortedSteps.length - 1 && (
              <div
                data-testid="step-connector"
                style={connectorStyles}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default PhaseRow;
