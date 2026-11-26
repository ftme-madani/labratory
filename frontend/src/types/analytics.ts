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
