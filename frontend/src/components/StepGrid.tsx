import React from 'react';
import { Step } from '../types/step';
import { PhaseRow } from './PhaseRow';

/**
 * Props for the StepGrid component.
 */
export interface StepGridProps {
  steps: Step[];
}

/**
 * Groups steps by their majorVersion (phase number).
 * Returns a map of majorVersion to array of steps.
 */
const groupStepsByPhase = (steps: Step[]): Map<number, Step[]> => {
  const phaseMap = new Map<number, Step[]>();

  for (const step of steps) {
    const existing = phaseMap.get(step.majorVersion) || [];
    existing.push(step);
    phaseMap.set(step.majorVersion, existing);
  }

  return phaseMap;
};

/**
 * Finds the first in_progress step across all phases.
 * Phases are searched in majorVersion order, steps in minorVersion order.
 */
const findFirstInProgressTaskId = (steps: Step[]): string | null => {
  // Sort all steps by majorVersion, then minorVersion
  const sortedSteps = [...steps].sort((a, b) => {
    if (a.majorVersion !== b.majorVersion) {
      return a.majorVersion - b.majorVersion;
    }
    return a.minorVersion - b.minorVersion;
  });

  // Find first in_progress step
  const inProgressStep = sortedSteps.find(step => step.status === 'in_progress');
  return inProgressStep ? inProgressStep.taskId : null;
};

/**
 * StepGrid displays a grid layout grouping steps by phase.
 * Each phase is rendered as a PhaseRow with steps sorted by version.
 */
export const StepGrid: React.FC<StepGridProps> = ({ steps }) => {
  // Handle empty state
  if (!steps || steps.length === 0) {
    return (
      <div
        data-testid="step-grid empty-state"
        style={emptyStateStyles}
      >
        <p style={emptyTextStyles}>No steps to display</p>
      </div>
    );
  }

  // Group steps by phase (majorVersion)
  const phaseMap = groupStepsByPhase(steps);

  // Sort phase keys (majorVersion) ascending
  const sortedPhaseKeys = Array.from(phaseMap.keys()).sort((a, b) => a - b);

  // Find the first in_progress step for pulsing
  const pulsingTaskId = findFirstInProgressTaskId(steps);

  const gridStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    padding: '16px',
  };

  return (
    <div data-testid="step-grid" style={gridStyles}>
      {sortedPhaseKeys.map(majorVersion => {
        const phaseSteps = phaseMap.get(majorVersion) || [];
        // Use the phase name from the first step in this group
        const phaseName = phaseSteps[0]?.phase || `Phase ${majorVersion}`;

        return (
          <PhaseRow
            key={majorVersion}
            phaseName={phaseName}
            steps={phaseSteps}
            pulsingTaskId={pulsingTaskId}
          />
        );
      })}
    </div>
  );
};

const emptyStateStyles: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  minHeight: '200px',
  backgroundColor: '#F9FAFB',
  borderRadius: '8px',
  border: '1px dashed #D1D5DB',
  margin: '16px',
};

const emptyTextStyles: React.CSSProperties = {
  fontSize: '16px',
  color: '#6B7280',
  margin: 0,
};

export default StepGrid;
