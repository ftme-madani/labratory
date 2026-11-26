import { apiClient } from './apiClient'

export interface SimulationErrorPayload {
  code: string
  category: string
  title: string
  description: string
  scientific_rationale: string
  recommended_action: string
}

export interface ActionExecuteResponse {
  success: boolean
  step_index: number
  is_step_completed: boolean
  error?: SimulationErrorPayload | null
  observations: string[]
  measurements: Record<string, any>
  state_snapshot: Record<string, any>
  is_terminal: boolean
}

export interface HintResponse {
  error_code: string
  category: string
  level: 1 | 2 | 3
  can_escalate: boolean
  content: string
  scientific_rationale: string
}

export interface StartAttemptResponse {
  attempt_id: string
  experiment_id: number
  experiment_slug: string
  experiment_title: string
  total_steps: number
  current_step: number
  status: string
}

export interface FinishAttemptResponse {
  attempt_id: string
  status: string
  score: number
  total_steps: number
  steps_completed: number
  observations_count: number
}

class SimulationService {
  async startAttempt(experimentSlug: string, classCode?: string): Promise<StartAttemptResponse> {
    return apiClient.post<StartAttemptResponse>('/simulation/attempts/start', {
      experiment_slug: experimentSlug,
      class_code: classCode
    })
  }

  async executeAction(
    attemptId: string,
    action: {
      action_type: string
      source_id: string
      target_id?: string
      parameters?: Record<string, any>
    }
  ): Promise<ActionExecuteResponse> {
    return apiClient.post<ActionExecuteResponse>(
      `/simulation/attempts/${attemptId}/action`,
      action
    )
  }

  async requestHint(
    attemptId: string,
    stepIndex: number,
    errorCode: string,
    forcedLevel?: number
  ): Promise<HintResponse> {
    return apiClient.post<HintResponse>(
      `/simulation/attempts/${attemptId}/hint`,
      {
        step_index: stepIndex,
        error_code: errorCode,
        forced_level: forcedLevel
      }
    )
  }

  async finishAttempt(attemptId: string): Promise<FinishAttemptResponse> {
    return apiClient.post<FinishAttemptResponse>(
      `/simulation/attempts/${attemptId}/finish`
    )
  }

  async getAttemptState(attemptId: string): Promise<any> {
    return apiClient.get<any>(`/simulation/attempts/${attemptId}/state`)
  }
}

export const simulationService = new SimulationService()
