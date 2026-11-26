import type { ExperimentAttempt } from '../types/attempt'
import type { UserProgressStats } from '../types/user'
import { apiClient } from './apiClient'
import { MOCK_ATTEMPTS, MOCK_STUDENT_STATS } from './mockData'

function mapBackendAttemptToFrontend(raw: any): ExperimentAttempt {
  return {
    id: raw.id,
    userId: String(raw.student_id || raw.user_id || 'usr-1'),
    experimentId: String(raw.experiment_id),
    experimentSlug: raw.experiment_slug || '',
    experimentTitle: raw.experiment_title || '',
    grade: raw.grade || 'هشتم',
    subject: raw.subject || 'شیمی',
    startedAt: raw.started_at,
    completedAt: raw.completed_at || undefined,
    status: raw.status || 'IN_PROGRESS',
    score: raw.score || 100,
    stepsCompleted: raw.steps_completed || 0,
    totalSteps: raw.total_steps || 3,
    actionsLog: (raw.action_logs || []).map((log: any) => ({
      stepIndex: log.step_index,
      timestamp: log.created_at,
      actionType: log.action_type,
      itemIds: log.item_ids || [],
      isValid: log.is_valid,
      errorCode: log.error_code,
      observationText: log.observation_text,
      feedbackText: log.feedback_text
    })),
    observations: raw.final_observations || [],
    hintsUsed: (raw.hint_usages || []).map((h: any) => ({
      stepIndex: h.step_index,
      level: h.hint_level,
      content: h.hint_content,
      requestedAt: h.created_at
    }))
  }
}

class AttemptService {
  private localAttempts: ExperimentAttempt[] = [...MOCK_ATTEMPTS]

  async getAttemptsByUser(userId: string): Promise<ExperimentAttempt[]> {
    try {
      const res = await apiClient.get<any[]>('/student/attempts')
      return res.map(mapBackendAttemptToFrontend)
    } catch (err) {
      console.warn('[AttemptService] استعلام تلاش‌ها از سرور با خطا مواجه شد، استفاده از داده محلی:', err)
      return this.localAttempts.filter((a) => a.userId === userId || userId === 'all')
    }
  }

  async getAttemptById(attemptId: string): Promise<ExperimentAttempt | null> {
    try {
      const res = await apiClient.get<any>(`/student/attempts/${attemptId}`)
      return mapBackendAttemptToFrontend(res)
    } catch (err) {
      console.warn(`[AttemptService] استعلام تلاش ${attemptId} از سرور با خطا مواجه شد:`, err)
      const found = this.localAttempts.find((a) => a.id === attemptId)
      return found || null
    }
  }

  async getStudentStats(): Promise<UserProgressStats> {
    try {
      const res = await apiClient.get<any>('/student/progress')
      return {
        completedExperiments: res.completed_experiments,
        totalAttempts: res.total_attempts,
        averageScore: res.average_score,
        hintsRequestedTotal: res.hints_requested_total,
        badges: (res.badges || []).map((b: any) => ({
          id: b.id,
          title: b.title,
          description: b.description,
          icon: b.icon,
          earnedAt: b.earned_at
        }))
      }
    } catch (err) {
      console.warn('[AttemptService] استعلام آمار پیشرفت از سرور ناموفق بود، استفاده از داده محلی:', err)
      return MOCK_STUDENT_STATS
    }
  }

  async saveAttempt(attempt: ExperimentAttempt): Promise<ExperimentAttempt> {
    const existingIdx = this.localAttempts.findIndex((a) => a.id === attempt.id)
    if (existingIdx >= 0) {
      this.localAttempts[existingIdx] = attempt
    } else {
      this.localAttempts.unshift(attempt)
    }
    return attempt
  }
}

export const attemptService = new AttemptService()
