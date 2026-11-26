import { create } from 'zustand'
import type { Experiment, EquipmentItem } from '../types/experiment'
import type { StepActionLog, HintRecord, ExperimentAttempt } from '../types/attempt'
import { attemptService } from '../services/attemptService'
import { simulationService } from '../services/simulationService'

interface FeedbackState {
  type: 'success' | 'warning' | 'error' | 'info' | 'hint'
  title: string
  message: string
}

interface LabStoreState {
  experiment: Experiment | null
  attemptId: string | null
  lastErrorCode: string | null
  workbenchItems: EquipmentItem[]
  currentStepIndex: number
  actionsLog: StepActionLog[]
  observations: string[]
  hintsUsed: HintRecord[]
  currentHintLevel: 1 | 2 | 3
  feedback: FeedbackState | null
  isCompleted: boolean
  score: number
  isSimulating: boolean
  labMode: 'inquiry' | 'guided'
  currentPredictionIndex: number | null
  predictionsLog: Array<{
    stepIndex: number
    question: string
    selectedOption: string
    isCorrect: boolean
    explanation: string
  }>
  activeClassCode: string | null

  setLabMode: (mode: 'inquiry' | 'guided') => void
  setCurrentPredictionIndex: (idx: number | null) => void
  initExperiment: (exp: Experiment, classCode?: string) => void
  addItemToWorkbench: (item: EquipmentItem) => void
  removeItemFromWorkbench: (itemId: string) => void
  resetWorkbench: () => void
  nextStep: () => void
  executeCurrentAction: () => { success: boolean; message: string }
  requestHint: () => { level: 1 | 2 | 3; content: string }
  finishAttempt: (userId: string) => Promise<ExperimentAttempt | null>
}

export const useLabStore = create<LabStoreState>((set, get) => ({
  experiment: null,
  attemptId: null,
  lastErrorCode: null,
  workbenchItems: [],
  currentStepIndex: 1,
  actionsLog: [],
  observations: [],
  hintsUsed: [],
  currentHintLevel: 1,
  feedback: null,
  isCompleted: false,
  score: 100,
  isSimulating: false,
  labMode: 'inquiry',
  currentPredictionIndex: null,
  predictionsLog: [],
  activeClassCode: null,

  setLabMode: (mode: 'inquiry' | 'guided') => set({ labMode: mode }),
  setCurrentPredictionIndex: (idx: number | null) => set({ currentPredictionIndex: idx }),

  initExperiment: (exp: Experiment, classCode?: string) => {
    const codeToUse = classCode || exp.classCode || null
    set({
      experiment: exp,
      attemptId: null,
      lastErrorCode: null,
      workbenchItems: [],
      currentStepIndex: 1,
      actionsLog: [],
      observations: [],
      hintsUsed: [],
      currentHintLevel: 1,
      currentPredictionIndex: null,
      predictionsLog: [],
      activeClassCode: codeToUse,
      feedback: {
        type: 'info',
        title: 'آماده‌سازی آزمایش (حالت کاوشگر)',
        message: `آزمایش «${exp.title}» بارگذاری شد. به عنوان یک کاوشگر علمی، دستورالعمل را بخوانید و وسایل مورد نیاز را خودتان انتخاب کنید.`
      },
      isCompleted: false,
      score: 100
    })

    // ایجاد یک نشست و تلاش رسمی در بک‌اند FastAPI
    simulationService
      .startAttempt(exp.slug, codeToUse || undefined)
      .then((res) => {
        set({ attemptId: res.attempt_id })
      })
      .catch((err) => {
        console.warn('[LabStore] راه‌اندازی تلاش روی سرور ناموفق بود؛ شبیه‌ساز محلی فعال است:', err)
      })
  },

  addItemToWorkbench: (item: EquipmentItem) => {
    const { workbenchItems, attemptId } = get()
    if (workbenchItems.some((i) => i.id === item.id)) {
      set({
        feedback: {
          type: 'warning',
          title: 'وسیله از قبل موجود است',
          message: `وسیلهٔ «${item.name}» از قبل روی میز کار قرار دارد.`
        }
      })
      return
    }

    set({
      workbenchItems: [...workbenchItems, item],
      feedback: {
        type: 'info',
        title: 'افزوده شد به میز',
        message: `«${item.name}» روی سطح آزمایشگاه قرار گرفت.`
      }
    })

    // ارسال کنش به سرور شبیه‌سازی در پس‌زمینه
    if (attemptId) {
      simulationService
        .executeAction(attemptId, { action_type: 'ADD_TOOL', source_id: item.id })
        .catch(() => {})
    }
  },

  removeItemFromWorkbench: (itemId: string) => {
    const { workbenchItems, attemptId } = get()
    set({
      workbenchItems: workbenchItems.filter((i) => i.id !== itemId),
      feedback: null
    })

    if (attemptId) {
      simulationService
        .executeAction(attemptId, { action_type: 'REMOVE_TOOL', source_id: itemId })
        .catch(() => {})
    }
  },

  resetWorkbench: () => {
    const { experiment } = get()
    if (experiment) {
      get().initExperiment(experiment)
    }
  },

  nextStep: () => {
    const { experiment, currentStepIndex } = get()
    if (!experiment) return

    if (currentStepIndex < experiment.steps.length) {
      set({
        currentStepIndex: currentStepIndex + 1,
        currentHintLevel: 1,
        lastErrorCode: null,
        feedback: {
          type: 'info',
          title: `مرحله ${currentStepIndex + 1}`,
          message: experiment.steps[currentStepIndex].instruction
        }
      })
    } else {
      set({ isCompleted: true })
    }
  },

  executeCurrentAction: () => {
    const {
      experiment,
      attemptId,
      currentStepIndex,
      workbenchItems,
      actionsLog,
      observations,
      score
    } = get()
    if (!experiment) return { success: false, message: 'آزمایش بارگذاری نشده است.' }

    const stepDef = experiment.steps[currentStepIndex - 1]
    if (!stepDef) return { success: false, message: 'مرحله تعریف نشده است.' }

    // بررسی پیش‌نیاز فرضیه‌سازی در صورت وجود پیش‌بینی
    if (stepDef.prediction && get().currentPredictionIndex === null) {
      set({
        feedback: {
          type: 'warning',
          title: 'فرضیه‌سازی علمی الزامی است 🔍',
          message: 'دانشمند گرامی، پیش از اجرای آزمایش، ابتدا فرضیه و پیش‌بینی علمی خود را از کادر بالا انتخاب نمایید.'
        }
      })
      return { success: false, message: 'لطفاً ابتدا فرضیه علمی خود را ثبت نمایید.' }
    }

    const workbenchIds = workbenchItems.map((i) => i.id)
    const missingItems = (stepDef.targetItems || [])
      .filter((tid) => tid && tid !== 'tool' && tid !== 'tool-1')
      .filter((tid) => {
        const norm = tid.replace(/-/g, '_').toLowerCase()
        return !workbenchIds.some((wid) => wid === tid || wid.replace(/-/g, '_').toLowerCase() === norm)
      })

    // ۱. بررسی پیش‌نیاز حضور ابزارها
    if (missingItems.length > 0) {
      const { labMode } = get()
      const isGuided = labMode === 'guided'

      const missingNames = missingItems
        .map((id) => {
          const norm = id.replace(/-/g, '_').toLowerCase()
          const tool = experiment.availableTools.find(
            (t) => t.id === id || t.id.replace(/-/g, '_').toLowerCase() === norm
          )
          return tool?.name || id
        })
        .join(' و ')

      const feedbackTitle = isGuided
        ? 'پیش‌نیاز مرحله رعایت نشده است'
        : 'ابزارهای روی میز برای اجرای این مرحله کافی نیست 🎯'

      const feedbackMessage = isGuided
        ? `برای اجرای این مرحله، ابتدا باید «${missingNames}» را از قفسه به میز کار اضافه کنید.`
        : `برای دستیابی به هدف این مرحله («${stepDef.title}»)، به ابزار یا ماده دیگری از قفسه نیاز دارید. صورت مسئله و دستورالعمل را بازخوانی کرده و ابزار مکمل را خودتان انتخاب کنید.`

      const failLog: StepActionLog = {
        stepIndex: currentStepIndex,
        timestamp: new Date().toISOString(),
        actionType: 'MIX',
        itemIds: workbenchIds,
        isValid: false,
        feedbackText: `پیش‌نیاز رعایت نشد: ابزار «${missingNames}» روی میز کار وجود ندارد.`,
        errorCode: 'ERR_MISSING_PRECONDITION_ITEMS'
      }

      set({
        actionsLog: [...actionsLog, failLog],
        lastErrorCode: 'ERR_MISSING_PRECONDITION_ITEMS',
        score: Math.max(0, score - (isGuided ? 3 : 5)),
        feedback: {
          type: 'error',
          title: feedbackTitle,
          message: feedbackMessage
        }
      })

      return { success: false, message: failLog.feedbackText }
    }

    // ۲. بررسی خطاهای علمی اختصاصی بر اساس قوانین برنامه درسی
    if (experiment.slug === 'acid-base-indicators') {
      if (
        currentStepIndex === 1 &&
        (workbenchIds.includes('litmus_red') || workbenchIds.includes('litmus-red')) &&
        !workbenchIds.includes('litmus_blue') &&
        !workbenchIds.includes('litmus-blue')
      ) {
        const errCode = 'ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID'
        const failLog: StepActionLog = {
          stepIndex: currentStepIndex,
          timestamp: new Date().toISOString(),
          actionType: 'DIP_INDICATOR',
          itemIds: workbenchIds,
          isValid: false,
          feedbackText: 'خطای علمی شناساگر: کاغذ تورنسل سرخ در محیط اسیدی تغییر رنگ نمی‌دهد و نمی‌تواند اسیدی بودن را اثبات نماید.',
          errorCode: errCode
        }

        set({
          actionsLog: [...actionsLog, failLog],
          lastErrorCode: errCode,
          score: Math.max(0, score - 5),
          feedback: {
            type: 'error',
            title: 'شناساگر برای اثبات خصلت اسیدی مناسب نیست',
            message: 'کاغذ تورنسل سرخ در محیط اسیدی (pH < 7) تغییر رنگ نمی‌دهد. برای اثبات اسیدی بودن آب‌لیمو، باید کاغذ تورنسل آبی را انتخاب کنید.'
          }
        })

        if (attemptId) {
          simulationService
            .executeAction(attemptId, {
              action_type: 'DIP_INDICATOR',
              source_id: 'litmus-red',
              target_id: 'beaker-lemon'
            })
            .catch(() => {})
        }

        return { success: false, message: failLog.feedbackText }
      }
    }

    // ۳. اجرای کنش موفق و ارزیابی فرضیه علمی
    let obsText = `مشاهده مرحله ${currentStepIndex}: پدیده علمی منطبق بر ${stepDef.scientificConcept}`
    let bonusScore = 0
    let feedbackTitle = 'گام انجام شد'
    let feedbackMsg = `مرحلهٔ «${stepDef.title}» با موفقیت تایید و قوانین علمی ثبت شد.`

    const predIdx = get().currentPredictionIndex
    if (stepDef.prediction && predIdx !== null) {
      const isCorrect = predIdx === stepDef.prediction.correctOptionIndex
      const chosenText = stepDef.prediction.options[predIdx]

      if (isCorrect) {
        bonusScore = 10
        obsText += ` | 🎯 فرضیه شما («${chosenText}») کاملاً صحیح بود!`
        feedbackTitle = 'آفرین! فرضیه شما تایید شد 🎯'
        feedbackMsg = `مشاهده آزمایش، فرضیه شما را اثبات کرد: ${stepDef.prediction.explanation}`
      } else {
        obsText += ` | 💡 فرضیه اولیه شما («${chosenText}») با نتیجه واقعی تفاوت داشت: ${stepDef.prediction.explanation}`
        feedbackTitle = 'کشف علمی و تحلیل فرضیه 💡'
        feedbackMsg = `نتیجه واقعی با پیش‌بینی اولیه شما متفاوت بود: ${stepDef.prediction.explanation}`
      }

      set({
        predictionsLog: [
          ...get().predictionsLog,
          {
            stepIndex: currentStepIndex,
            question: stepDef.prediction.question,
            selectedOption: chosenText,
            isCorrect,
            explanation: stepDef.prediction.explanation
          }
        ],
        currentPredictionIndex: null
      })
    }

    const successLog: StepActionLog = {
      stepIndex: currentStepIndex,
      timestamp: new Date().toISOString(),
      actionType: stepDef.expectedAction || 'MIX',
      itemIds: stepDef.targetItems,
      isValid: true,
      observationText: obsText,
      feedbackText: feedbackMsg
    }

    const nextIdx = currentStepIndex + 1
    const isNowCompleted = nextIdx > experiment.steps.length
    if (isNowCompleted) {
      feedbackTitle = 'آزمایش به پایان رسید'
    }

    set({
      actionsLog: [...actionsLog, successLog],
      observations: [...observations, obsText],
      currentStepIndex: isNowCompleted ? currentStepIndex : nextIdx,
      isCompleted: isNowCompleted,
      currentHintLevel: 1,
      lastErrorCode: null,
      score: Math.min(100, Math.max(0, score + bonusScore)),
      feedback: {
        type: 'success',
        title: feedbackTitle,
        message: feedbackMsg
      }
    })

    // ارسال به موتور شبیه‌سازی پایتون در بک‌اند
    if (attemptId) {
      let simActionType = 'MIX'
      let src = stepDef.targetItems[0] || 'tool-1'
      let tgt: string | undefined = stepDef.targetItems[1]

      if (experiment.slug === 'acid-base-indicators') {
        if (currentStepIndex === 1) {
          simActionType = 'DIP_INDICATOR'
          src = 'litmus-blue'
          tgt = 'beaker-lemon'
        } else if (currentStepIndex === 2) {
          simActionType = 'DIP_INDICATOR'
          src = 'litmus-red'
          tgt = 'beaker-soda'
        } else {
          simActionType = 'MEASURE_PH'
          src = 'ph-meter'
          tgt = 'beaker-lemon'
        }
      }

      simulationService
        .executeAction(attemptId, {
          action_type: simActionType,
          source_id: src,
          target_id: tgt
        })
        .then((res) => {
          if (res.observations && res.observations.length > 0) {
            set((state) => ({
              observations: Array.from(new Set([...state.observations, ...res.observations]))
            }))
          }
        })
        .catch((err) => {
          console.warn('[LabStore] خطای ناهمگام در سرور شبیه‌سازی:', err)
        })
    }

    return { success: true, message: successLog.feedbackText }
  },

  requestHint: () => {
    const {
      experiment,
      attemptId,
      currentStepIndex,
      currentHintLevel,
      hintsUsed,
      lastErrorCode,
      score
    } = get()

    if (!experiment) return { level: 1, content: 'راهنمایی در دسترس نیست.' }

    const stepDef = experiment.steps[currentStepIndex - 1]
    const lvlKey = `level${currentHintLevel}` as keyof typeof stepDef.hintLevels
    const content = stepDef?.hintLevels?.[lvlKey] || 'قوانین کتاب درسی را مرور کنید.'

    const newRecord: HintRecord = {
      stepIndex: currentStepIndex,
      level: currentHintLevel,
      content,
      requestedAt: new Date().toISOString()
    }

    const nextLvl = (Math.min(3, currentHintLevel + 1) as 1 | 2 | 3)

    set({
      hintsUsed: [...hintsUsed, newRecord],
      currentHintLevel: nextLvl,
      score: Math.max(50, score - 2),
      feedback: {
        type: 'hint',
        title: `راهنمای هوشمند پداگوژیک (سطح ${currentHintLevel})`,
        message: content
      }
    })

    // ارسال درخواست ثبت راهنما به سرویس بک‌اند
    if (attemptId) {
      const errToPass = lastErrorCode || 'ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID'
      simulationService
        .requestHint(attemptId, currentStepIndex, errToPass, currentHintLevel)
        .then((res) => {
          if (res.content) {
            set({
              feedback: {
                type: 'hint',
                title: `راهنمای هوشمند (سطح ${res.level})`,
                message: res.content
              }
            })
          }
        })
        .catch(() => {})
    }

    return { level: currentHintLevel, content }
  },

  finishAttempt: async (userId: string) => {
    const { experiment, attemptId, actionsLog, observations, hintsUsed, score } = get()
    if (!experiment) return null

    if (attemptId) {
      simulationService.finishAttempt(attemptId).catch(() => {})
    }

    const attempt: ExperimentAttempt = {
      id: attemptId || `att-${Date.now()}`,
      userId,
      experimentId: experiment.id,
      experimentSlug: experiment.slug,
      experimentTitle: experiment.title,
      grade: experiment.grade,
      subject: experiment.subject,
      startedAt: actionsLog[0]?.timestamp || new Date().toISOString(),
      completedAt: new Date().toISOString(),
      status: 'COMPLETED',
      score,
      stepsCompleted: experiment.steps.length,
      totalSteps: experiment.steps.length,
      classCode: get().activeClassCode || experiment.classCode || undefined,
      actionsLog,
      observations,
      hintsUsed
    }

    await attemptService.saveAttempt(attempt)
    return attempt
  }
}))
