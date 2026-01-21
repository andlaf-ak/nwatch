/**
 * Step status represents the current state of a workflow step.
 */
export type StepStatus = 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped';

/**
 * Step represents a single workflow step in the nWave methodology.
 * Matches the backend Step struct.
 */
export interface Step {
  taskId: string;
  projectId: string;
  phase: string;
  description: string;
  status: StepStatus;
  majorVersion: number;
  minorVersion: number;
}

/**
 * WebSocket message types for real-time step updates.
 */
export type WebSocketMessageType = 'init' | 'update' | 'remove';

/**
 * Base WebSocket message structure.
 */
export interface BaseWebSocketMessage {
  type: WebSocketMessageType;
}

/**
 * InitMessage is sent when a client first connects.
 * Contains the current state of all steps.
 */
export interface InitMessage extends BaseWebSocketMessage {
  type: 'init';
  steps: Step[];
}

/**
 * UpdateMessage is sent when a step is created or updated.
 */
export interface UpdateMessage extends BaseWebSocketMessage {
  type: 'update';
  step: Step;
}

/**
 * RemoveMessage is sent when a step is removed.
 */
export interface RemoveMessage extends BaseWebSocketMessage {
  type: 'remove';
  taskId: string;
  projectId: string;
}

/**
 * Union type for all WebSocket messages.
 */
export type WebSocketMessage = InitMessage | UpdateMessage | RemoveMessage;

/**
 * Type guard to check if a message is an InitMessage.
 */
export function isInitMessage(message: WebSocketMessage): message is InitMessage {
  return message.type === 'init';
}

/**
 * Type guard to check if a message is an UpdateMessage.
 */
export function isUpdateMessage(message: WebSocketMessage): message is UpdateMessage {
  return message.type === 'update';
}

/**
 * Type guard to check if a message is a RemoveMessage.
 */
export function isRemoveMessage(message: WebSocketMessage): message is RemoveMessage {
  return message.type === 'remove';
}
