export interface FrequentErrorStat {
  errorCode: string
  errorTitle: string
  experimentTitle: string
  occurrenceCount: number
  scientificConcept: string
  recommendedRemediation: string
}

export interface ClassPerformanceStat {
  experimentId: string
  experimentTitle: string
  totalAttempts: number
  completionRatePercent: number
  averageScorePercent: number
  averageHintsUsed: number
}

export interface TeacherAnalyticsData {
  totalStudents: number
  activeExperimentsCount: number
  averageCompletionRate: number
  frequentErrors: FrequentErrorStat[]
  experimentStats: ClassPerformanceStat[]
}

export interface AnalyticsOverview {
  totalAttempts: number
  completedAttempts: number
  overallSuccessRate: number
  activeStudentsCount: number
  averageScore: number
  totalHintsUsed: number
  totalErrorsRecorded: number
}

export interface MisconceptionItem {
  errorCode: string
  errorTitle: string
  experimentTitle: string
  scientificConcept: string
  recommendedRemediation: string
  occurrenceCount: number
  percentage: number
  affectedStudentsCount: number
}

export interface TeacherStudentItem {
  studentId: number
  fullName: string
  email: string
  grade?: string
  schoolName?: string
  classCode?: string
  totalAttempts: number
  completedAttempts: number
  successRate: number
  averageScore: number
  errorsCount: number
  hintsCount: number
  lastActivity?: string
}

export interface StudentActionLog {
  id: number
  attemptId: string
  experimentId: number
  experimentTitle: string
  stepIndex: number
  actionType: string
  itemIds: string[]
  parameters?: Record<string, any>
  isValid: boolean
  errorCode?: string
  errorTitle?: string
  observationText?: string
  feedbackText: string
  createdAt: string
}

export interface StudentLogsData {
  studentId: number
  fullName: string
  totalLogs: number
  logs: StudentActionLog[]
}
