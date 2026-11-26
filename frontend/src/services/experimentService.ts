import type { Experiment, GradeLevel, SubjectType } from '../types/experiment'
import { apiClient } from './apiClient'
import { MOCK_EXPERIMENTS } from './mockData'

function mapBackendExperimentToFrontend(backendExp: any): Experiment {
  const mock = MOCK_EXPERIMENTS.find((m) => m.slug === backendExp.slug || m.id === String(backendExp.id))

  const backendTools = (backendExp.available_tools || []).map((t: any) => ({
    id: t.id,
    name: t.name,
    category: (t.category || t.type || 'tool') as any,
    iconName: t.icon || t.iconName || 'flask',
    description: t.description || t.name,
    state: t.properties?.state || t.state || 'liquid',
    colorHex: t.colorHex || '#38BDF8',
    ph: t.properties?.pH || t.ph,
    isHazardous: t.isHazardous || false
  }))

  // در صورت وجود تعریف غنی در mockData، از آن به عنوان مرجع اصلی ابزارها استفاده می‌کنیم
  const tools = mock?.availableTools && mock.availableTools.length > 0 ? mock.availableTools : backendTools

  const steps = (backendExp.steps_config || []).map((s: any, idx: number) => {
    const mockStep = mock?.steps[idx]
    let targetItems: string[] = []

    if (Array.isArray(s.targetItems) && s.targetItems.length > 0) {
      targetItems = s.targetItems.filter((id: string) => id && id !== 'tool' && id !== 'tool-1')
    }

    if (targetItems.length === 0 && mockStep?.targetItems) {
      targetItems = mockStep.targetItems
    }

    return {
      index: s.index || idx + 1,
      title: s.title || mockStep?.title || `گام ${idx + 1}`,
      instruction: s.description || s.instruction || mockStep?.instruction || '',
      expectedAction: s.expectedAction || mockStep?.expectedAction || 'MIX',
      targetItems: targetItems,
      scientificConcept: s.hint || s.scientificConcept || mockStep?.scientificConcept || 'مفهوم درسی',
      hintLevels: s.hintLevels || mockStep?.hintLevels || {
        level1: s.hint || 'دقت کنید که کدام ابزار مناسب است.',
        level2: 'قوانین کتاب درسی را بازبینی نمایید.',
        level3: 'طبق دستور کار آزمایشگاه عمل کنید.'
      },
      prediction: s.prediction || mockStep?.prediction
    }
  })

  const finalSteps = steps.length > 0 ? steps : (mock?.steps || [])

  let svgType: 'flask' | 'circuit' | 'filter' | 'gauge' | 'leaf' | 'test-tube' = mock?.thumbnailSvgType || 'flask'
  if (backendExp.thumbnail_type === 'zap' || backendExp.subject === 'فیزیک') {
    svgType = 'circuit'
  } else if (backendExp.thumbnail_type === 'filter' || backendExp.slug?.includes('mixture')) {
    svgType = 'filter'
  }

  return {
    id: String(backendExp.id),
    slug: backendExp.slug,
    title: backendExp.title,
    subject: backendExp.subject,
    grade: backendExp.grade,
    difficulty: backendExp.difficulty || 'متوسط',
    durationMinutes: backendExp.duration_minutes || 15,
    status: backendExp.status || 'PUBLISHED',
    version: backendExp.version || 1,
    summary: backendExp.summary || mock?.summary || '',
    textbook: {
      book: backendExp.textbook_source?.book || mock?.textbook.book || 'علوم تجربی',
      grade: backendExp.textbook_source?.grade || backendExp.grade,
      chapter: backendExp.textbook_source?.chapter || mock?.textbook.chapter || 'فصل ۱',
      chapterNumber: backendExp.textbook_source?.chapterNumber || mock?.textbook.chapterNumber || 1,
      page: backendExp.textbook_source?.page || mock?.textbook.page || 1,
      curriculumCode: backendExp.textbook_source?.curriculumCode || mock?.textbook.curriculumCode
    },
    objectives: backendExp.objectives || mock?.objectives || [],
    safetyNotes: backendExp.safety_notes || mock?.safetyNotes || [],
    availableTools: tools,
    steps: finalSteps,
    featured: true,
    thumbnailSvgType: svgType,
    classCode: backendExp.class_code || undefined,
    isClassOnly: Boolean(backendExp.is_class_only),
    createdById: backendExp.created_by_id || undefined
  }
}

class ExperimentService {
  private localExperiments: Experiment[] = [...MOCK_EXPERIMENTS]

  async getAllExperiments(filters?: {
    search?: string
    grade?: GradeLevel | 'all'
    subject?: SubjectType | 'all'
    status?: string
    classCode?: string
    onlyMine?: boolean
  }): Promise<Experiment[]> {
    try {
      const params = new URLSearchParams()
      if (filters?.grade && filters.grade !== 'all') params.append('grade', filters.grade)
      if (filters?.subject && filters.subject !== 'all') params.append('subject', filters.subject)
      if (filters?.status) params.append('status', filters.status)
      if (filters?.classCode) params.append('class_code', filters.classCode)
      if (filters?.onlyMine) params.append('only_mine', 'true')

      const queryString = params.toString() ? `?${params.toString()}` : ''
      const res = await apiClient.get<any[]>(`/experiments${queryString}`)

      let experiments = res.map(mapBackendExperimentToFrontend)

      if (filters?.search) {
        const q = filters.search.trim().toLowerCase()
        experiments = experiments.filter(
          (exp) =>
            exp.title.toLowerCase().includes(q) ||
            exp.summary.toLowerCase().includes(q) ||
            exp.textbook.book.toLowerCase().includes(q)
        )
      }

      return experiments
    } catch (err) {
      console.warn('[ExperimentService] دریافت آزمایش‌ها از سرور با خطا مواجه شد، استفاده از داده‌های پیش‌فرض:', err)
      // حالت آفلاین
      let result = [...this.localExperiments]
      if (filters?.search) {
        const q = filters.search.trim().toLowerCase()
        result = result.filter(
          (exp) =>
            exp.title.toLowerCase().includes(q) ||
            exp.summary.toLowerCase().includes(q) ||
            exp.textbook.book.toLowerCase().includes(q)
        )
      }
      if (filters?.grade && filters.grade !== 'all') {
        result = result.filter((exp) => exp.grade === filters.grade)
      }
      if (filters?.subject && filters.subject !== 'all') {
        result = result.filter((exp) => exp.subject === filters.subject)
      }
      return result
    }
  }

  async getFeaturedExperiments(): Promise<Experiment[]> {
    const all = await this.getAllExperiments()
    return all.filter((e) => e.featured)
  }

  async getExperimentBySlug(slug: string): Promise<Experiment | null> {
    try {
      const res = await apiClient.get<any>(`/experiments/${slug}`)
      return mapBackendExperimentToFrontend(res)
    } catch (err) {
      console.warn(`[ExperimentService] خطا در دریافت جزئیات ${slug} از سرور:`, err)
      const found = this.localExperiments.find((e) => e.slug === slug || e.id === slug)
      return found || null
    }
  }

  async saveExperimentDraft(exp: Partial<Experiment>): Promise<Experiment> {
    try {
      const payload = {
        slug: exp.slug || `exp-custom-${Date.now()}`,
        title: exp.title || 'آزمایش جدید',
        subject: exp.subject || 'شیمی',
        grade: exp.grade || 'هشتم',
        difficulty: exp.difficulty || 'متوسط',
        duration_minutes: exp.durationMinutes || 15,
        summary: exp.summary || 'توضیحات پیش‌نویس آزمایش',
        textbook_source: exp.textbook || {
          book: 'علوم تجربی دوره اول متوسطه',
          grade: 'هشتم',
          chapter: 'پیشنویس آزمایش',
          chapterNumber: 1,
          page: 1
        },
        objectives: exp.objectives || ['هدف آموزشی ۱'],
        safety_notes: exp.safetyNotes || ['رعایت نکات ایمنی'],
        available_tools: exp.availableTools || [],
        steps_config: exp.steps || [],
        thumbnail_type: exp.thumbnailSvgType === 'circuit' ? 'zap' : (exp.thumbnailSvgType || 'flask'),
        status: exp.status || 'DRAFT',
        class_code: exp.classCode || undefined,
        is_class_only: Boolean(exp.isClassOnly)
      }

      const res = await apiClient.post<any>('/experiments', payload)
      return mapBackendExperimentToFrontend(res)
    } catch (err) {
      console.warn('[ExperimentService] ذخیره در سرور با خطا مواجه شد، ذخیره در حافظه محلی:', err)
      const newExp: Experiment = {
        id: exp.id || `exp-${Date.now()}`,
        slug: exp.slug || `exp-custom-${Date.now()}`,
        title: exp.title || 'آزمایش جدید',
        subject: exp.subject || 'شیمی',
        grade: exp.grade || 'هشتم',
        difficulty: exp.difficulty || 'متوسط',
        durationMinutes: exp.durationMinutes || 15,
        status: exp.status || 'DRAFT',
        version: exp.version || 1,
        thumbnailSvgType: exp.thumbnailSvgType || 'flask',
        textbook: exp.textbook || {
          book: 'علوم تجربی دوره اول متوسطه',
          grade: 'هشتم',
          chapter: 'پیشنویس آزمایش',
          chapterNumber: 1,
          page: 1
        },
        summary: exp.summary || 'توضیحات پیش‌نویس آزمایش',
        objectives: exp.objectives || ['هدف آموزشی ۱'],
        safetyNotes: exp.safetyNotes || ['رعایت نکات ایمنی'],
        availableTools: exp.availableTools || [],
        steps: exp.steps || []
      }
      this.localExperiments.unshift(newExp)
      return newExp
    }
  }

  async updateStatus(id: string, status: Experiment['status']): Promise<boolean> {
    try {
      await apiClient.put(`/experiments/${id}/status`, { status })
      return true
    } catch (err) {
      console.warn(`[ExperimentService] خطا در تغییر وضعیت آزمایش ${id}:`, err)
      const found = this.localExperiments.find((e) => e.id === id)
      if (found) {
        found.status = status
        return true
      }
      return false
    }
  }

  async joinClassExperiment(classCode: string, studentName?: string): Promise<Experiment> {
    try {
      const res = await apiClient.post<any>('/experiments/join-class', {
        class_code: classCode,
        student_name: studentName
      })
      return mapBackendExperimentToFrontend(res)
    } catch (err: any) {
      // بررسی لوکال در صورت نبود سرور
      const found = this.localExperiments.find(
        (e) => (e.classCode && e.classCode.toLowerCase() === classCode.trim().toLowerCase()) || e.slug === classCode.trim()
      )
      if (found) return found
      throw err
    }
  }
}

export const experimentService = new ExperimentService()
