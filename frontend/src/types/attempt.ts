export type AttemptStatus = 'IN_PROGRESS' | 'COMPLETED' | 'FAILED'

export type LabActionType =
  | 'ADD_ITEM'
  | 'REMOVE_ITEM'
  | 'ADD_TOOL'
  | 'REMOVE_TOOL'
  | 'MIX'
  | 'HEAT'
  | 'MEASURE'
  | 'MEASURE_PH'
  | 'CONNECT'
  | 'DIP_INDICATOR'
  | 'DISSOLVE'
  | 'FILTER'
  | 'EVAPORATE'
  | (string & {})

export interface StepActionLog {
  stepIndex: number
  timestamp: string
  actionType: LabActionType
  itemIds: string[]
  isValid: boolean
  observationText?: string
  feedbackText: string
  errorCode?: string
}

export interface HintRecord {
  stepIndex: number
  level: 1 | 2 | 3
  content: string
  requestedAt: string
}

export interface ExperimentAttempt {
  id: string
  userId: string
  experimentId: string
  experimentSlug: string
  experimentTitle: string
  grade: string
  subject: string
  startedAt: string
  completedAt?: string
  status: AttemptStatus
  score: number // 0 to 100
  stepsCompleted: number
  totalSteps: number
  studentName?: string
  studentGrade?: string
  studentSchool?: string
  classCode?: string
  teacherFeedback?: string
  hintsCount?: number
  errorsCount?: number
  actionsLog: StepActionLog[]
  observations: string[]
  hintsUsed: HintRecord[]
}
