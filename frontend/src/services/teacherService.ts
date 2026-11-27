import type {
  TeacherAnalyticsData,
  AnalyticsOverview,
  MisconceptionItem,
  TeacherStudentItem,
  StudentLogsData
} from '../types/analytics'
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

  // --- Endpoints جدید ردیابی کج‌فهمی‌ها و داشبورد معلم ---

  async getOverview(filters?: {
    experimentId?: number
    classCode?: string
    dateFrom?: string
    dateTo?: string
  }): Promise<AnalyticsOverview> {
    try {
      const params = new URLSearchParams()
      if (filters?.experimentId) params.append('experiment_id', String(filters.experimentId))
      if (filters?.classCode) params.append('class_code', filters.classCode)
      if (filters?.dateFrom) params.append('date_from', filters.dateFrom)
      if (filters?.dateTo) params.append('date_to', filters.dateTo)

      const q = params.toString() ? `?${params.toString()}` : ''
      const res = await apiClient.get<any>(`/teacher/analytics/overview${q}`)
      return {
        totalAttempts: res.total_attempts ?? 0,
        completedAttempts: res.completed_attempts ?? 0,
        overallSuccessRate: res.overall_success_rate ?? 0,
        activeStudentsCount: res.active_students_count ?? 0,
        averageScore: res.average_score ?? 0,
        totalHintsUsed: res.total_hints_used ?? 0,
        totalErrorsRecorded: res.total_errors_recorded ?? 0
      }
    } catch (err) {
      console.warn('[TeacherService] دریافت خلاصه عملکرد از سرور ناموفق بود:', err)
      return {
        totalAttempts: 24,
        completedAttempts: 19,
        overallSuccessRate: 79.2,
        activeStudentsCount: 15,
        averageScore: 84.5,
        totalHintsUsed: 31,
        totalErrorsRecorded: 18
      }
    }
  }

  async getMisconceptions(filters?: {
    experimentId?: number
    classCode?: string
    dateFrom?: string
    dateTo?: string
  }): Promise<{ totalErrors: number; misconceptions: MisconceptionItem[] }> {
    try {
      const params = new URLSearchParams()
      if (filters?.experimentId) params.append('experiment_id', String(filters.experimentId))
      if (filters?.classCode) params.append('class_code', filters.classCode)
      if (filters?.dateFrom) params.append('date_from', filters.dateFrom)
      if (filters?.dateTo) params.append('date_to', filters.dateTo)

      const q = params.toString() ? `?${params.toString()}` : ''
      const res = await apiClient.get<any>(`/teacher/analytics/misconceptions${q}`)
      return {
        totalErrors: res.total_errors ?? 0,
        misconceptions: (res.misconceptions || []).map((m: any) => ({
          errorCode: m.error_code,
          errorTitle: m.error_title,
          experimentTitle: m.experiment_title,
          scientificConcept: m.scientific_concept,
          recommendedRemediation: m.recommended_remediation,
          occurrenceCount: m.occurrence_count,
          percentage: m.percentage,
          affectedStudentsCount: m.affected_students_count
        }))
      }
    } catch (err) {
      console.warn('[TeacherService] استعلام کج‌فهمی‌ها ناموفق بود، فال‌بک نمونه:', err)
      return {
        totalErrors: 6,
        misconceptions: [
          {
            errorCode: 'ERR_CIRCUIT_WITHOUT_LOAD',
            errorTitle: 'اتصال کوتاه باتری بدون مصرف‌کننده',
            experimentTitle: 'مدار الکتریکی ساده و قانون اهم',
            scientificConcept: 'لزوم وجود مقاومت در مدار جهت جلوگیری از جریان بی‌نهایت و آسیب باتری',
            recommendedRemediation: 'مرور مبحث مقاومت الکتریکی و جهت جریان در مدار بسته',
            occurrenceCount: 8,
            percentage: 44.4,
            affectedStudentsCount: 7
          },
          {
            errorCode: 'ERR_WRONG_INDICATOR',
            errorTitle: 'استفاده از شناساگر نامناسب برای محلول',
            experimentTitle: 'شناساگرهای اسید و باز',
            scientificConcept: 'تغییر رنگ کاغذ تورنسل متناسب با pH محیط اسیدی یا بازی',
            recommendedRemediation: 'آزمایش شناساگر با آب مقطر قبل از محلول اصلی',
            occurrenceCount: 5,
            percentage: 27.8,
            affectedStudentsCount: 5
          },
          {
            errorCode: 'ERR_SAND_SALT_HEATING_FIRST',
            errorTitle: 'حرارت دادن مستقیم قبل از انحلال و صاف کردن',
            experimentTitle: 'جداسازی مخلوط ماسه و نمک',
            scientificConcept: 'جداسازی فاز جامد-مایع با فیلتراسیون قبل از فرآیند تبخیر',
            recommendedRemediation: 'مرور تفاوت قابلیت انحلال نمک و ماسه در آب',
            occurrenceCount: 5,
            percentage: 27.8,
            affectedStudentsCount: 4
          }
        ]
      }
    }
  }

  async getStudentsAnalytics(filters?: {
    classCode?: string
    experimentId?: number
    dateFrom?: string
    dateTo?: string
  }): Promise<TeacherStudentItem[]> {
    try {
      const params = new URLSearchParams()
      if (filters?.classCode) params.append('class_code', filters.classCode)
      if (filters?.experimentId) params.append('experiment_id', String(filters.experimentId))
      if (filters?.dateFrom) params.append('date_from', filters.dateFrom)
      if (filters?.dateTo) params.append('date_to', filters.dateTo)

      const q = params.toString() ? `?${params.toString()}` : ''
      const res = await apiClient.get<any[]>(`/teacher/analytics/students${q}`)
      return res.map((s: any) => ({
        studentId: s.student_id,
        fullName: s.full_name,
        email: s.email,
        grade: s.grade,
        schoolName: s.school_name,
        classCode: s.class_code,
        totalAttempts: s.total_attempts,
        completedAttempts: s.completed_attempts,
        successRate: s.success_rate,
        averageScore: s.average_score,
        errorsCount: s.errors_count,
        hintsCount: s.hints_count,
        lastActivity: s.last_activity
      }))
    } catch (err) {
      console.warn('[TeacherService] دریافت وضعیت دانش‌آموزان با خطا مواجه شد:', err)
      return [
        {
          studentId: 1,
          fullName: 'علیرضا حسینی',
          email: 'alireza@school.ir',
          grade: 'هشتم',
          schoolName: 'مدرسه شهید بهشتی',
          classCode: 'CLASS-8A',
          totalAttempts: 5,
          completedAttempts: 4,
          successRate: 80,
          averageScore: 92,
          errorsCount: 2,
          hintsCount: 3,
          lastActivity: new Date().toISOString()
        },
        {
          studentId: 2,
          fullName: 'محمد رسولی',
          email: 'm.rasooli@school.ir',
          grade: 'هشتم',
          schoolName: 'مدرسه نمونه دولتی',
          classCode: 'CLASS-8A',
          totalAttempts: 3,
          completedAttempts: 3,
          successRate: 100,
          averageScore: 98,
          errorsCount: 0,
          hintsCount: 1,
          lastActivity: new Date(Date.now() - 3600000 * 2).toISOString()
        },
        {
          studentId: 3,
          fullName: 'سارا کریمی',
          email: 'sara.k@school.ir',
          grade: 'هشتم',
          schoolName: 'مدرسه فرزانگان',
          classCode: 'CLASS-8B',
          totalAttempts: 4,
          completedAttempts: 2,
          successRate: 50,
          averageScore: 68,
          errorsCount: 6,
          hintsCount: 5,
          lastActivity: new Date(Date.now() - 3600000 * 24).toISOString()
        }
      ]
    }
  }

  async getStudentLogs(studentId: number, filters?: {
    experimentId?: number
    dateFrom?: string
    dateTo?: string
  }): Promise<StudentLogsData> {
    try {
      const params = new URLSearchParams()
      if (filters?.experimentId) params.append('experiment_id', String(filters.experimentId))
      if (filters?.dateFrom) params.append('date_from', filters.dateFrom)
      if (filters?.dateTo) params.append('date_to', filters.dateTo)

      const q = params.toString() ? `?${params.toString()}` : ''
      const res = await apiClient.get<any>(`/teacher/analytics/student/${studentId}/logs${q}`)
      return {
        studentId: res.student_id,
        fullName: res.full_name,
        totalLogs: res.total_logs,
        logs: (res.logs || []).map((l: any) => ({
          id: l.id,
          attemptId: l.attempt_id,
          experimentId: l.experiment_id,
          experimentTitle: l.experiment_title,
          stepIndex: l.step_index,
          actionType: l.action_type,
          itemIds: l.item_ids || [],
          parameters: l.parameters || {},
          isValid: l.is_valid,
          errorCode: l.error_code,
          errorTitle: l.error_title,
          observationText: l.observation_text,
          feedbackText: l.feedback_text,
          createdAt: l.created_at
        }))
      }
    } catch (err) {
      console.warn(`[TeacherService] دریافت لاگ‌های دانش‌آموز ${studentId} ناموفق بود:`, err)
      return {
        studentId,
        fullName: 'دانش‌آموز',
        totalLogs: 0,
        logs: []
      }
    }
  }

  // --- دریافت فایل CSV گزارش کلاس و دانش‌آموز ---

  async downloadClassReportCsv(classCode?: string, experimentId?: number): Promise<void> {
    const params = new URLSearchParams()
    if (classCode) params.append('class_code', classCode)
    if (experimentId) params.append('experiment_id', String(experimentId))
    const q = params.toString() ? `?${params.toString()}` : ''
    
    // دانلود مستقیم فایل
    window.open(`/api/v1/teacher/reports/class/csv${q}`, '_blank')
  }

  async downloadStudentReportCsv(studentId: number): Promise<void> {
    window.open(`/api/v1/teacher/reports/student/${studentId}/csv`, '_blank')
  }
}

export const teacherService = new TeacherService()
