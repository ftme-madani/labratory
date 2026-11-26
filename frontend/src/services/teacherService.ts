import type { TeacherAnalyticsData } from '../types/analytics'
import type { ExperimentAttempt } from '../types/attempt'
import { apiClient } from './apiClient'
import { MOCK_TEACHER_ANALYTICS, MOCK_ATTEMPTS } from './mockData'

class TeacherService {
  async getAnalytics(): Promise<TeacherAnalyticsData> {
    try {
      const res = await apiClient.get<any>('/teacher/analytics')
      return {
        totalStudents: res.total_students,
        activeExperimentsCount: res.active_experiments_count,
        averageCompletionRate: res.average_completion_rate,
        frequentErrors: (res.frequent_errors || []).map((err: any) => ({
          errorCode: err.error_code,
          errorTitle: err.error_title,
          experimentTitle: err.experiment_title,
          occurrenceCount: err.occurrence_count,
          scientificConcept: err.scientific_concept,
          recommendedRemediation: err.recommended_remediation
        })),
        experimentStats: (res.experiment_stats || []).map((stat: any) => ({
          experimentId: String(stat.experiment_id),
          experimentTitle: stat.experiment_title,
          totalAttempts: stat.total_attempts,
          completionRatePercent: stat.completion_rate_percent,
          averageScorePercent: stat.average_score_percent,
          averageHintsUsed: stat.average_hints_used
        }))
      }
    } catch (err) {
      console.warn('[TeacherService] دریافت آمار تحلیلی معلم از سرور ناموفق بود، استفاده از داده محلی:', err)
      return MOCK_TEACHER_ANALYTICS
    }
  }

  async getAllStudentAttempts(filters?: {
    experimentId?: number
    status?: string
    studentId?: number
    classCode?: string
    onlyMyStudents?: boolean
  }): Promise<ExperimentAttempt[]> {
    try {
      const params = new URLSearchParams()
      if (filters?.experimentId) params.append('experiment_id', String(filters.experimentId))
      if (filters?.status && filters.status !== 'all') params.append('status', filters.status)
      if (filters?.studentId) params.append('student_id', String(filters.studentId))
      if (filters?.classCode) params.append('class_code', filters.classCode)
      if (filters?.onlyMyStudents) params.append('only_my_students', 'true')

      const q = params.toString() ? `?${params.toString()}` : ''
      const res = await apiClient.get<any[]>(`/teacher/students/attempts${q}`)
      return res.map((raw: any) => ({
        id: raw.id,
        userId: String(raw.student_id),
        studentName: raw.student_name,
        studentGrade: raw.student_grade || 'هشتم',
        studentSchool: raw.student_school,
        classCode: raw.class_code,
        teacherFeedback: raw.teacher_feedback,
        experimentId: String(raw.experiment_id),
        experimentSlug: '',
        experimentTitle: raw.experiment_title || '',
        grade: raw.student_grade || 'هشتم',
        subject: 'علوم تجربی',
        startedAt: raw.started_at,
        completedAt: raw.completed_at || undefined,
        status: raw.status || 'IN_PROGRESS',
        score: raw.score || 100,
        stepsCompleted: raw.steps_completed || 0,
        totalSteps: raw.total_steps || 3,
        hintsCount: raw.hints_count || 0,
        errorsCount: raw.errors_count || 0,
        actionsLog: [],
        observations: [],
        hintsUsed: []
      }))
    } catch (err) {
      console.warn('[TeacherService] دریافت گزارش تلاش‌های کلاس از سرور با خطا مواجه شد، استفاده از داده محلی:', err)
      return MOCK_ATTEMPTS
    }
  }

  async getStudentAttemptAudit(attemptId: string): Promise<any> {
    try {
      return await apiClient.get<any>(`/teacher/students/attempts/${attemptId}`)
    } catch (err) {
      console.warn(`[TeacherService] استعلام لاگ‌های ممیزی تلاش ${attemptId} ناموفق بود:`, err)
      return null
    }
  }

  async submitFeedback(attemptId: string, feedback: string): Promise<any> {
    try {
      return await apiClient.put<any>(`/teacher/students/attempts/${attemptId}/feedback`, {
        teacher_feedback: feedback
      })
    } catch (err) {
      console.warn(`[TeacherService] ثبت بازخورد معلم برای ${attemptId} با خطا مواجه شد:`, err)
      return { status: 'mock_success', teacher_feedback: feedback }
    }
  }
}

export const teacherService = new TeacherService()
