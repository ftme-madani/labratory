export interface AITutorHintResponse {
  attempt_id: string
  error_code: string
  category: string
  level: 1 | 2 | 3
  can_escalate: boolean
  content: string
  scientific_rationale?: string
  is_ai_generated: boolean
  model_used?: string
}

export interface AIQuestionResponse {
  attempt_id: string
  question: string
  answer: string
  experiment_title: string
  is_ai_generated: boolean
}

export interface TeacherAIInsightsResponse {
  class_code?: string
  total_errors_analyzed: number
  top_misconceptions: Array<{
    error_code: string
    error_title: string
    experiment_title: string
    occurrence_count: number
    scientific_concept: string
    remediation: string
  }>
  ai_pedagogical_remediation: string
  is_ai_generated: boolean
}

export interface ChatMessage {
  id: string
  sender: 'user' | 'ai'
  text: string
  level?: 1 | 2 | 3
  timestamp: string
  isAiGenerated?: boolean
}
