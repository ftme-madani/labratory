import { apiRequest } from './apiClient'
import type {
  AITutorHintResponse,
  AIQuestionResponse,
  TeacherAIInsightsResponse
} from '../types/ai'

export const aiService = {
  /**
   * درخواست راهنمایی شخصی‌سازی‌شده و سه‌سطحی از معلم‌یار هوشمند
   */
  async requestAITutorHint(
    attemptId: string,
    errorCode: string,
    stepIndex: number = 1,
    actionSummary?: string,
    forcedLevel?: number
  ): Promise<AITutorHintResponse> {
    return apiRequest<AITutorHintResponse>(
      `/ai/tutor/hint?attempt_id=${encodeURIComponent(attemptId)}`,
      {
        method: 'POST',
        body: JSON.stringify({
          error_code: errorCode,
          step_index: stepIndex,
          action_summary: actionSummary,
          forced_level: forcedLevel
        })
      }
    )
  },

  /**
   * طرح پرسش مفهومی و آزاد از دستیار هوشمند در حین آزمایش
   */
  async askAITutorQuestion(
    attemptId: string,
    question: string,
    stepIndex: number = 1
  ): Promise<AIQuestionResponse> {
    return apiRequest<AIQuestionResponse>('/ai/tutor/ask', {
      method: 'POST',
      body: JSON.stringify({
        attempt_id: attemptId,
        question: question.trim(),
        step_index: stepIndex
      })
    })
  },

  /**
   * دریافت بینش‌های تحلیلی پداگوژیک و توصیه‌های تدریس برای دبیر
   */
  async getTeacherAIInsights(classCode?: string): Promise<TeacherAIInsightsResponse> {
    const endpoint = classCode
      ? `/ai/teacher/insights?class_code=${encodeURIComponent(classCode)}`
      : '/ai/teacher/insights'
    return apiRequest<TeacherAIInsightsResponse>(endpoint, {
      method: 'GET'
    })
  },

  /**
   * دریافت فایل صوتی MP3 از سرور برای خواندن متن به صوت طبیعی فارسی (Edge-TTS)
   */
  async getVoiceTTSAudio(text: string, voice: string = 'fa-IR-DilaraNeural'): Promise<Blob> {
    const baseUrl = (import.meta as any).env?.VITE_API_BASE_URL || '/api/v1'
    const token = localStorage.getItem('virtual_lab_auth_token')
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const res = await fetch(`${baseUrl}/ai/voice/tts`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ text, voice })
    })

    if (!res.ok) {
      throw new Error(`خطا در تولید صوت: ${res.status}`)
    }

    return await res.blob()
  }
}
