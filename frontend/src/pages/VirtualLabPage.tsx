import React, { useEffect, useState } from 'react'
import { useParams, useNavigate, Link, useSearchParams } from 'react-router-dom'
import { experimentService } from '../services/experimentService'
import { useLabStore } from '../store/useLabStore'
import { useAuthStore } from '../store/useAuthStore'
import { useThemeStore } from '../store/useThemeStore'
import {
  Button,
  Badge,
  Modal,
  StatusAlert,
  Skeleton
} from '../components/ui'
import {
  FlaskConical,
  Beaker,
  TestTube,
  Flame,
  Zap,
  RotateCcw,
  HelpCircle,
  CheckCircle2,
  X,
  Play,
  ArrowRight,
  Award,
  Compass,
  Sparkles
} from 'lucide-react'
import { VinegarReactionSimulation } from '../components/simulations/VinegarReactionSimulation'
import { PendulumSimulation } from '../components/simulations/PendulumSimulation'
import { PlantTransportSimulation } from '../components/simulations/PlantTransportSimulation'
import { DensityColumnSimulation } from '../components/simulations/DensityColumnSimulation'
import { WaterFiltrationSimulation } from '../components/simulations/WaterFiltrationSimulation'
import { VoiceAssistantWidget } from '../components/simulations/VoiceAssistantWidget'

export const VirtualLabPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>()
  const [searchParams] = useSearchParams()
  const classCodeParam = searchParams.get('class_code') || searchParams.get('code')
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { theme } = useThemeStore()
  const isLight = theme === 'light'

  const {
    experiment,
    attemptId,
    lastErrorCode,
    workbenchItems,
    currentStepIndex,
    observations,
    hintsUsed,
    feedback,
    isCompleted,
    score,
    labMode,
    currentPredictionIndex,
    predictionsLog,
    setLabMode,
    setCurrentPredictionIndex,
    initExperiment,
    addItemToWorkbench,
    removeItemFromWorkbench,
    resetWorkbench,
    executeCurrentAction,
    requestHint,
    finishAttempt
  } = useLabStore()

  const [loading, setLoading] = useState(true)
  const [hintModalOpen, setHintModalOpen] = useState(false)
  const [activeHintLevel, setActiveHintLevel] = useState<1 | 2 | 3>(1)
  const [hintContent, setHintContent] = useState('')
  const [completionModalOpen, setCompletionModalOpen] = useState(false)

  useEffect(() => {
    if (slug) {
      experimentService.getExperimentBySlug(slug).then((exp) => {
        if (exp) {
          initExperiment(exp, classCodeParam || undefined)
        }
        setLoading(false)
      })
    }
  }, [slug, initExperiment, classCodeParam])

  useEffect(() => {
    if (isCompleted) {
      setCompletionModalOpen(true)
      if (user) {
        finishAttempt(user.id)
      }
    }
  }, [isCompleted, finishAttempt, user])

  if (loading || !experiment) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-12 space-y-6">
        <Skeleton className="h-10 w-1/4" />
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  const currentStep = experiment.steps[currentStepIndex - 1]
  const progressPercent = Math.round(
    ((currentStepIndex - (isCompleted ? 0 : 1)) / experiment.steps.length) * 100
  )

  const handleOpenHint = () => {
    const hintRes = requestHint()
    setActiveHintLevel(hintRes.level)
    setHintContent(hintRes.content)
    setHintModalOpen(true)
  }

  const handleNextHintLevel = () => {
    const hintRes = requestHint()
    setActiveHintLevel(hintRes.level)
    setHintContent(hintRes.content)
  }

  // Visual simulation helper according to workbench items
  const renderLabSimulationGraphics = () => {
    const itemIds = workbenchItems.map((i) => i.id)

    // Experiment 1: Acid & Base Indicator visual
    if (experiment.slug === 'acid-base-indicators') {
      const hasLemon = itemIds.includes('beaker_lemon')
      const hasSoap = itemIds.includes('beaker_soap')
      const hasLitmusBlue = itemIds.includes('litmus_blue')
      const hasLitmusRed = itemIds.includes('litmus_red')

      return (
        <div className="flex flex-wrap items-end justify-center gap-8 py-6">
          {/* Lemon Beaker */}
          {hasLemon && (
            <div className="flex flex-col items-center animate-in fade-in duration-300">
              <span className={`text-[11px] font-bold mb-1 ${isLight ? 'text-amber-800' : 'text-amber-300'}`}>بشر آب‌لیمو (اسید)</span>
              <div className={`relative w-32 h-44 border-4 border-t-0 rounded-b-3xl flex flex-col justify-end p-2 transition-all ${
                isLight
                  ? 'border-slate-300 bg-white/70 shadow-md backdrop-blur-xs'
                  : 'border-slate-500/80 bg-slate-900/60 shadow-xl'
              }`}>
                <div className={`w-full h-24 rounded-b-2xl relative overflow-hidden ${
                  isLight
                    ? 'bg-gradient-to-t from-amber-500/90 to-yellow-300/80'
                    : 'bg-gradient-to-t from-amber-600/80 to-amber-400/60'
                }`}>
                  <span className={`absolute bottom-1 right-2 text-[10px] font-mono font-bold ${
                    isLight ? 'text-amber-950' : 'text-amber-200'
                  }`}>pH ≈ 2.5</span>
                </div>
                {/* Litmus Strip dipping */}
                {hasLitmusBlue && (
                  <div className="absolute top-2 left-10 w-5 h-36 bg-blue-500 border border-blue-400 rounded-sm shadow-md transition-all duration-700 animate-in slide-in-from-top-4">
                    <div className="absolute bottom-0 w-full h-16 bg-rose-500 border-t border-rose-400 flex items-center justify-center">
                      <span className="text-[7px] text-white font-mono rotate-90">سرخ</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Soap Beaker */}
          {hasSoap && (
            <div className="flex flex-col items-center animate-in fade-in duration-300">
              <span className={`text-[11px] font-bold mb-1 ${isLight ? 'text-teal-800' : 'text-teal-300'}`}>بشر آب‌صابون (باز)</span>
              <div className={`relative w-32 h-44 border-4 border-t-0 rounded-b-3xl flex flex-col justify-end p-2 transition-all ${
                isLight
                  ? 'border-slate-300 bg-white/70 shadow-md backdrop-blur-xs'
                  : 'border-slate-500/80 bg-slate-900/60 shadow-xl'
              }`}>
                <div className={`w-full h-24 rounded-b-2xl relative overflow-hidden ${
                  isLight
                    ? 'bg-gradient-to-t from-teal-400/90 to-sky-300/80'
                    : 'bg-gradient-to-t from-teal-600/80 to-teal-400/60'
                }`}>
                  <span className={`absolute bottom-1 right-2 text-[10px] font-mono font-bold ${
                    isLight ? 'text-teal-950' : 'text-teal-200'
                  }`}>pH ≈ 9.5</span>
                </div>
                {/* Litmus Strip dipping */}
                {hasLitmusRed && (
                  <div className="absolute top-2 left-10 w-5 h-36 bg-rose-500 border border-rose-400 rounded-sm shadow-md transition-all duration-700 animate-in slide-in-from-top-4">
                    <div className="absolute bottom-0 w-full h-16 bg-blue-500 border-t border-blue-400 flex items-center justify-center">
                      <span className="text-[7px] text-white font-mono rotate-90">آبی</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {!hasLemon && !hasSoap && (
            <div className={`text-center text-xs p-8 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              برای شروع آزمایش، بشر محلول‌ها و کاغذهای تورنسل را از قفسه راست به میز کار اضافه کنید. 🧪
            </div>
          )}
        </div>
      )
    }

    // Experiment 2: Mixture separation visual
    if (experiment.slug === 'mixture-separation-sand-salt') {
      const hasMixture = itemIds.includes('beaker_sand_salt')
      const hasWater = itemIds.includes('wash_bottle_water')
      const hasFunnel = itemIds.includes('funnel_filter_paper')
      const hasBurner = itemIds.includes('bunsen_burner')
      const hasDish = itemIds.includes('evaporating_dish')

      return (
        <div className="flex flex-wrap items-end justify-center gap-6 py-6">
          {hasMixture && (
            <div className="flex flex-col items-center">
              <span className={`text-[11px] font-bold mb-1 ${isLight ? 'text-slate-700' : 'text-slate-300'}`}>مخلوط نمک و ماسه</span>
              <div className={`relative w-28 h-36 border-4 border-t-0 rounded-b-2xl flex flex-col justify-end p-1.5 transition-all ${
                isLight ? 'border-slate-300 bg-white/70 shadow-md backdrop-blur-xs' : 'border-slate-500/80 bg-slate-900/60 shadow-lg'
              }`}>
                <div className={`w-full ${hasWater ? (isLight ? 'h-24 bg-sky-200/60' : 'h-24 bg-blue-900/40') : 'h-10'} rounded-b-xl relative overflow-hidden`}>
                  <div className="absolute bottom-0 w-full h-6 bg-amber-800/80 flex items-center justify-center text-[8px] text-amber-100 font-bold">
                    ماسه ته‌نشین
                  </div>
                  {hasWater && (
                    <div className={`text-[8px] text-center pt-1 font-bold ${isLight ? 'text-sky-800' : 'text-cyan-200'}`}>
                      محلول آب‌نمک
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {hasFunnel && (
            <div className="flex flex-col items-center">
              <span className={`text-[11px] font-bold mb-1 ${isLight ? 'text-teal-800' : 'text-teal-300'}`}>قیف و کاغذ صافی</span>
              <div className={`w-24 h-32 border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-2 text-center text-xs transition-all ${
                isLight
                  ? 'border-teal-400 bg-teal-50/70 text-teal-900 shadow-sm'
                  : 'border-teal-500/60 bg-slate-900/60 text-teal-200'
              }`}>
                <span className="font-bold">فیلتراسیون ماسه</span>
                <span className={`text-[10px] mt-1 ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>جداسازی فاز جامد</span>
              </div>
            </div>
          )}

          {hasDish && (
            <div className="flex flex-col items-center">
              <span className={`text-[11px] font-bold mb-1 ${isLight ? 'text-amber-800' : 'text-amber-300'}`}>کپسول چینی تبخیر</span>
              <div className={`relative w-28 h-20 border-2 rounded-b-full flex items-center justify-center transition-all ${
                isLight
                  ? 'border-slate-300 bg-amber-50/80 shadow-md text-amber-950 font-bold'
                  : 'border-slate-400 bg-slate-900/80 shadow-lg text-white'
              }`}>
                <span className="text-[10px]">
                  {hasBurner ? 'تبخیر آب و نمک ♨️' : 'محلول آب‌نمک'}
                </span>
              </div>
              {hasBurner && (
                <div className="mt-1 flex items-center gap-1 text-xs text-rose-500 font-bold animate-pulse">
                  <Flame className="w-4 h-4 text-orange-500" />
                  <span>شعله چراغ بونزن</span>
                </div>
              )}
            </div>
          )}

          {!hasMixture && !hasFunnel && !hasDish && (
            <div className={`text-center text-xs p-8 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              وسایل مربوط به جداسازی (بشر، پیست آب، قیف و کپسول چینی) را از قفسه به میز اضافه نمایید. 🧪
            </div>
          )}
        </div>
      )
    }

    // Experiment 3: Simple circuit visual
    if (experiment.slug === 'simple-electric-circuit-ohm') {
      const hasBattery = itemIds.includes('battery_cell')
      const hasSwitch = itemIds.includes('switch_key')
      const hasBulb = itemIds.includes('light_bulb')
      const hasWires = itemIds.includes('connecting_wires')
      const isCircuitClosed = hasBattery && hasSwitch && hasBulb && hasWires

      return (
        <div className="flex flex-col items-center py-6 space-y-4">
          <div className={`p-6 rounded-3xl border-2 relative w-80 h-52 flex flex-col justify-between transition-all ${
            isLight
              ? 'border-amber-300 bg-gradient-to-b from-amber-50 to-orange-50/40 shadow-md'
              : 'border-cyan-500/40 bg-slate-900/60 shadow-xl'
          }`}>
            {/* Top Wire & Switch */}
            <div className="flex items-center justify-between">
              <div className={`flex items-center gap-1 text-xs font-bold ${isLight ? 'text-sky-700' : 'text-cyan-300'}`}>
                <Zap className="w-4 h-4 text-amber-500" />
                <span>باتری ۱.۵ ولت قلمی</span>
              </div>
              <div className={`text-xs font-bold ${
                hasSwitch
                  ? (isLight ? 'text-emerald-700' : 'text-emerald-300')
                  : (isLight ? 'text-slate-600' : 'text-slate-300')
              }`}>
                {hasSwitch ? 'کلید: بسته [ON] ⚡' : 'کلید: مدار باز'}
              </div>
            </div>

            {/* Center Bulb Visual */}
            <div className="flex items-center justify-center">
              <div
                className={`w-20 h-20 rounded-full border-2 flex items-center justify-center transition-all duration-500 ${
                  isCircuitClosed
                    ? 'bg-amber-400 border-amber-300 shadow-2xl shadow-amber-400 text-slate-950 animate-pulse'
                    : isLight
                    ? 'bg-slate-100 border-slate-300 text-slate-400'
                    : 'bg-slate-800 border-slate-700 text-slate-500'
                }`}
              >
                <Zap className="w-8 h-8" />
              </div>
            </div>

            {/* Bottom Status */}
            <div className={`text-center text-[11px] font-mono font-bold ${
              isCircuitClosed
                ? (isLight ? 'text-emerald-700' : 'text-emerald-300')
                : (isLight ? 'text-slate-500' : 'text-slate-400')
            }`}>
              {isCircuitClosed ? 'جریان برقرار است: I = 0.15A | لامپ روشن شد 💡' : 'مدار ناقص است یا کلید باز است'}
            </div>
          </div>
        </div>
      )
    }

    // ۵ آزمایش جدید با مؤلفه‌های اختصاصی و تعاملی
    if (experiment.slug === 'vinegar-baking-soda-reaction') {
      return <VinegarReactionSimulation attemptId={attemptId} />
    }

    if (experiment.slug === 'simple-pendulum-motion') {
      return <PendulumSimulation attemptId={attemptId} />
    }

    if (experiment.slug === 'plant-water-transport-celery') {
      return <PlantTransportSimulation attemptId={attemptId} />
    }

    if (experiment.slug === 'liquid-density-column') {
      return <DensityColumnSimulation attemptId={attemptId} />
    }

    if (experiment.slug === 'water-filtration-column') {
      return <WaterFiltrationSimulation attemptId={attemptId} />
    }

    return null
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Top Header & Breadcrumbs */}
      <div className={`flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl transition-all ${
        isLight
          ? 'border border-slate-200/90 bg-white shadow-sm shadow-slate-200/50'
          : 'border border-indigo-500/25 bg-gradient-to-r from-indigo-950/70 via-slate-900/80 to-purple-950/60 shadow-xl shadow-indigo-950/30 backdrop-blur-md'
      }`}>
        <div className="space-y-1.5">
          <div className={`flex items-center gap-2 text-xs ${isLight ? 'text-slate-500' : 'text-indigo-300'}`}>
            <Link to="/experiments" className={`flex items-center gap-1 transition-colors ${isLight ? 'hover:text-sky-600' : 'hover:text-cyan-300'}`}>
              <ArrowRight className="w-3.5 h-3.5" />
              کاتالوگ آزمایش‌ها
            </Link>
            <span>/</span>
            <span className={`truncate font-medium ${isLight ? 'text-slate-700' : 'text-slate-200'}`}>{experiment.title}</span>
          </div>
          <h1 className={`text-xl sm:text-2xl font-black flex items-center gap-2.5 ${isLight ? 'text-slate-900' : 'text-white'}`}>
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-400 to-emerald-400 p-0.5 shadow-md shadow-emerald-500/20 flex items-center justify-center">
              <FlaskConical className="w-5 h-5 text-slate-950" />
            </div>
            <span>{experiment.title}</span>
          </h1>

          {/* اطلاعات اتصال به کلاس دبیر و مشخصات دانش‌آموز ارزیابی‌شونده */}
          <div className="flex flex-wrap items-center gap-2 mt-2">
            {(classCodeParam || experiment.classCode) && (
              <Badge variant={isLight ? 'indigo' : 'indigo'} size="sm" className="font-mono font-bold">
                🔒 کلاس دبیر: {classCodeParam || experiment.classCode}
              </Badge>
            )}
            {user && (
              <span className={`text-[11px] px-3 py-1 rounded-full font-medium ${
                isLight
                  ? 'bg-amber-50 border border-amber-200 text-amber-900'
                  : 'bg-slate-800/80 border border-slate-700/60 text-slate-300'
              }`}>
                دانش‌آموز کوشا: <strong className={isLight ? 'text-amber-700' : 'text-amber-300'}>{user.fullName}</strong> ({user.schoolName || 'مدرسه'}) ⭐
              </span>
            )}
          </div>
        </div>

        {/* Action Controls & Mode Switcher */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Lab Mode Toggle: Inquiry vs Guided */}
          <div className={`flex items-center p-1 rounded-2xl text-xs shadow-inner ${
            isLight ? 'bg-slate-100 border border-slate-200' : 'bg-slate-950/80 border border-indigo-500/30'
          }`}>
            <button
              type="button"
              onClick={() => setLabMode('inquiry')}
              className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl font-black transition-all ${
                labMode === 'inquiry'
                  ? 'bg-gradient-to-r from-amber-400 to-yellow-400 text-slate-950 shadow-md shadow-amber-400/30 scale-105'
                  : isLight
                  ? 'text-slate-600 hover:text-slate-900'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
              title="حالت کاوشگری و چالش علمی بدون لو رفتن ابزارها"
            >
              <Compass className="w-4 h-4" />
              <span>حالت کاوشگر 🎯</span>
            </button>
            <button
              type="button"
              onClick={() => setLabMode('guided')}
              className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl font-black transition-all ${
                labMode === 'guided'
                  ? 'bg-gradient-to-r from-teal-500 to-emerald-400 text-white shadow-md shadow-teal-500/30 scale-105'
                  : isLight
                  ? 'text-slate-600 hover:text-slate-900'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
              title="حالت آموزشی با چک‌لیست و راهنمای مستقیم ابزارها"
            >
              <HelpCircle className="w-4 h-4" />
              <span>حالت راهنما 💡</span>
            </button>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={resetWorkbench}
            rightIcon={<RotateCcw className="w-4 h-4" />}
            className={`font-bold rounded-xl ${
              isLight ? 'border-slate-300 text-slate-700 hover:bg-slate-100' : 'border-slate-700 hover:bg-slate-800'
            }`}
          >
            بازنشانی میز
          </Button>
          <Button
            variant={isLight ? 'cyan' : 'cyan'}
            size="sm"
            onClick={handleOpenHint}
            rightIcon={<HelpCircle className="w-4 h-4" />}
            className="font-bold rounded-xl shadow-sm"
          >
            راهنمای سقراطی (سطح {hintsUsed.length + 1}) 💡
          </Button>
        </div>
      </div>

      {/* Step Tracker Progress Bar */}
      <div className={`rounded-3xl p-5 space-y-4 transition-all ${
        isLight
          ? 'border border-slate-200/90 bg-white shadow-sm shadow-slate-200/40 text-slate-800'
          : 'border border-indigo-500/30 bg-gradient-to-r from-slate-900/95 via-indigo-950/70 to-slate-900/95 shadow-xl shadow-indigo-950/20 text-white'
      }`}>
        <div className="flex items-center justify-between text-xs">
          <span className={`font-black flex items-center gap-2.5 text-sm ${isLight ? 'text-slate-900' : 'text-white'}`}>
            <span className="w-6 h-6 rounded-full bg-gradient-to-br from-amber-400 to-yellow-500 text-slate-950 flex items-center justify-center font-black text-xs shadow-md shadow-amber-400/20">
              {isCompleted ? '✓' : currentStepIndex}
            </span>
            <span>{isCompleted ? '🎉 تبریک! آزمایش به پایان رسید' : currentStep?.title}</span>
          </span>
          <span className={`font-mono font-black text-sm px-2.5 py-0.5 rounded-full ${
            isLight
              ? 'text-sky-800 bg-sky-50 border border-sky-200'
              : 'text-cyan-300 bg-cyan-950/60 border border-cyan-400/30'
          }`}>
            {progressPercent}٪ پیشرفت 🚀
          </span>
        </div>

        <div className={`w-full h-3 rounded-full overflow-hidden p-0.5 border shadow-inner ${
          isLight ? 'bg-slate-100 border-slate-200' : 'bg-slate-950/90 border-indigo-500/30'
        }`}>
          <div
            className="h-full bg-gradient-to-r from-amber-400 via-emerald-400 to-sky-400 transition-all duration-500 rounded-full shadow-md shadow-emerald-400/30"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {!isCompleted && currentStep && (
          <div className={`space-y-3 pt-1 border-t mt-2 ${isLight ? 'border-slate-200' : 'border-slate-800/60'}`}>
            <p className={`text-xs leading-relaxed p-3 rounded-2xl border ${
              isLight ? 'text-slate-800 bg-amber-50/50 border-amber-200/60 font-medium' : 'text-slate-200 bg-slate-950/40 border-slate-800'
            }`}>
              <strong>دستورالعمل مرحله جاری:</strong> {currentStep.instruction}
            </p>

            {/* در حالت کاوشگر: چالش و تفکر مستقل دانش‌آموز */}
            {labMode === 'inquiry' ? (
              <div className={`p-3 rounded-xl border flex items-start gap-2.5 text-xs ${
                isLight
                  ? 'bg-amber-50 border-amber-200 text-amber-950'
                  : 'bg-gradient-to-r from-amber-950/30 to-slate-900/60 border-amber-600/30 text-amber-200'
              }`}>
                <Compass className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold">چالش کاوشگری علمی:</span>
                    <Badge variant="amber" size="sm">تفکر مستقل</Badge>
                  </div>
                  <p className={`text-[11px] leading-relaxed ${isLight ? 'text-slate-700' : 'text-slate-300'}`}>
                    با تکیه بر اطلاعات کتاب درسی و دستورالعمل بالا، خودتان ابزارها و مواد مناسب را از قفسه انتخاب کرده و روی میز کار قرار دهید.
                  </p>
                </div>
              </div>
            ) : (
              /* در حالت راهنما: چک‌لیست آموزشی ابزارها */
              currentStep.targetItems && currentStep.targetItems.length > 0 && (
                <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
                  <span className={`text-[11px] font-bold ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>وسایل و مواد پیش‌نیاز این مرحله:</span>
                  <div className="flex flex-wrap items-center gap-1.5">
                    {currentStep.targetItems
                      .filter((tid) => tid && tid !== 'tool' && tid !== 'tool-1')
                      .map((tid) => {
                        const tool =
                          experiment.availableTools.find((t) => t.id === tid) ||
                          experiment.availableTools.find(
                            (t) => t.id.replace(/-/g, '_') === tid.replace(/-/g, '_')
                          )
                        const name = tool?.name || tid
                        const isReady = workbenchItems.some(
                          (i) =>
                            i.id === tid ||
                            i.id.replace(/-/g, '_') === tid.replace(/-/g, '_')
                        )
                        return (
                          <button
                            key={tid}
                            type="button"
                            onClick={() => {
                              if (!isReady && tool) {
                                addItemToWorkbench(tool)
                              }
                            }}
                            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all ${
                              isReady
                                ? isLight
                                  ? 'bg-emerald-100 border border-emerald-300 text-emerald-800'
                                  : 'bg-emerald-950/70 border border-emerald-500/50 text-emerald-300'
                                : isLight
                                ? 'bg-amber-100 border border-amber-300 text-amber-900 hover:bg-amber-200 cursor-pointer animate-pulse'
                                : 'bg-amber-950/50 border border-amber-500/50 text-amber-200 hover:bg-amber-900/60 cursor-pointer animate-pulse'
                            }`}
                            title={isReady ? 'این وسیله روی میز کار قرار دارد' : 'برای افزودن به میز کار کلیک کنید'}
                          >
                            <span className="font-bold">{isReady ? '✓' : '+'}</span>
                            <span>{name}</span>
                            <span className="text-[10px] opacity-75">
                              ({isReady ? 'روی میز' : 'کلیک برای افزودن'})
                            </span>
                          </button>
                        )
                      })}
                  </div>
                </div>
              )
            )}

            {/* بخش فرضیه‌سازی و پیش‌بینی علمی قبل از اجرا */}
            {currentStep.prediction && (
              <div className={`p-3.5 rounded-2xl border space-y-2.5 animate-in fade-in duration-300 ${
                isLight ? 'bg-sky-50/70 border-sky-200' : 'bg-cyan-950/30 border-cyan-500/40'
              }`}>
                <div className="flex items-center justify-between text-xs">
                  <div className={`flex items-center gap-2 font-bold ${isLight ? 'text-sky-800' : 'text-cyan-300'}`}>
                    <Sparkles className="w-4 h-4 text-sky-500" />
                    <span>فرضیه‌سازی علمی (پیش‌بینی پدیده قبل از اجرا):</span>
                  </div>
                  {currentPredictionIndex !== null && (
                    <Badge variant={isLight ? 'emerald' : 'cyan'} size="sm">
                      فرضیه ثبت شد ✓
                    </Badge>
                  )}
                </div>
                <p className={`text-xs font-semibold ${isLight ? 'text-slate-800' : 'text-slate-200'}`}>
                  {currentStep.prediction.question}
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 pt-1">
                  {currentStep.prediction.options.map((opt, optIdx) => {
                    const isSelected = currentPredictionIndex === optIdx
                    return (
                      <button
                        key={optIdx}
                        type="button"
                        onClick={() => setCurrentPredictionIndex(optIdx)}
                        className={`p-2.5 rounded-xl border text-right text-xs transition-all flex items-center gap-2 ${
                          isSelected
                            ? 'bg-sky-500 text-white border-sky-600 font-bold shadow-md'
                            : isLight
                            ? 'bg-white text-slate-700 border-slate-200 hover:bg-sky-50 hover:border-sky-300'
                            : 'bg-slate-900/90 text-slate-300 border-slate-700/80 hover:bg-slate-800 hover:border-cyan-500/50'
                        }`}
                      >
                        <span className={`w-5 h-5 rounded-full flex items-center justify-center font-mono text-[10px] shrink-0 border ${
                          isSelected
                            ? 'bg-white text-sky-700 border-white'
                            : isLight
                            ? 'bg-slate-100 text-slate-600 border-slate-200'
                            : 'bg-slate-800 text-slate-400 border-slate-700'
                        }`}>
                          {optIdx + 1}
                        </span>
                        <span className="leading-relaxed">{opt}</span>
                      </button>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Main Grid: Workbench Area (Center/Left) + Tools Shelf (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Right Column in RTL: Equipment Inventory Shelf */}
        <div className={`lg:col-span-1 rounded-3xl p-5 flex flex-col gap-3 transition-all ${
          isLight
            ? 'border border-slate-200/90 bg-white shadow-sm shadow-slate-200/40 text-slate-800'
            : 'border border-indigo-500/25 bg-gradient-to-b from-slate-900/95 via-slate-900/90 to-indigo-950/80 shadow-xl shadow-indigo-950/25 text-white'
        }`}>
          <div className={`flex items-center justify-between pb-3 border-b ${isLight ? 'border-slate-200' : 'border-indigo-500/20'}`}>
            <div className={`flex items-center gap-2 text-xs font-black ${isLight ? 'text-slate-900' : 'text-white'}`}>
              <div className={`w-6 h-6 rounded-lg flex items-center justify-center ${
                isLight ? 'bg-amber-100 border border-amber-300 text-amber-800' : 'bg-amber-400/20 border border-amber-400/40 text-amber-300'
              }`}>
                <Beaker className="w-3.5 h-3.5" />
              </div>
              <span>قفسه وسایل و مواد 🧪</span>
            </div>
            <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
              isLight ? 'text-sky-800 bg-sky-50 border border-sky-200' : 'text-cyan-300 bg-cyan-950/60 border border-cyan-400/30'
            }`}>
              کلیک برای انتخاب
            </span>
          </div>

          {/* Tools Grid */}
          <div className="space-y-2 overflow-y-auto max-h-[500px] pr-0.5">
            {experiment.availableTools.map((tool) => {
              const isPlaced = workbenchItems.some((i) => i.id === tool.id)
              const isRequiredForCurrentStep = currentStep?.targetItems?.includes(tool.id)
              const showStepBadge = labMode === 'guided' && isRequiredForCurrentStep && !isPlaced

              return (
                <div
                  key={tool.id}
                  onClick={() => !isPlaced && addItemToWorkbench(tool)}
                  className={`p-3 rounded-2xl border text-right transition-all duration-200 flex items-center justify-between gap-2.5 select-none shadow-sm ${
                    isPlaced
                      ? isLight
                        ? 'border-slate-200 bg-slate-100/60 opacity-40 cursor-default'
                        : 'border-slate-800 bg-slate-950/40 opacity-40 cursor-default'
                      : showStepBadge
                      ? isLight
                        ? 'border-amber-400 bg-amber-50 ring-2 ring-amber-300 text-amber-950 shadow-sm cursor-pointer animate-pulse scale-[1.02]'
                        : 'border-amber-400/80 bg-gradient-to-r from-amber-950/50 to-slate-900 ring-2 ring-amber-400/40 text-amber-100 shadow-md shadow-amber-500/20 cursor-pointer animate-pulse scale-[1.02]'
                      : isLight
                      ? 'border-slate-200 bg-slate-50/80 hover:bg-sky-50 hover:border-sky-300 text-slate-800 cursor-pointer hover:scale-[1.02]'
                      : 'border-slate-700/60 bg-slate-800/60 hover:bg-gradient-to-r hover:from-indigo-900/50 hover:to-slate-800 hover:border-cyan-400/50 cursor-pointer text-slate-100 hover:scale-[1.02]'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <div className={`w-9 h-9 rounded-xl border flex items-center justify-center shrink-0 shadow-xs ${
                      isLight
                        ? 'bg-sky-50 border-sky-200 text-sky-700'
                        : 'bg-gradient-to-br from-indigo-900/90 to-slate-900 border-cyan-400/30 text-cyan-300'
                    }`}>
                      <TestTube className="w-4 h-4" />
                    </div>
                    <div>
                      <h5 className={`text-xs font-black ${isLight ? 'text-slate-900' : 'text-white'}`}>{tool.name}</h5>
                      <span className={`text-[10px] leading-none ${isLight ? 'text-slate-500' : 'text-slate-300'}`}>{tool.description}</span>
                    </div>
                  </div>
                  {isPlaced ? (
                    <Badge variant="emerald" size="sm" className="font-bold">
                      روی میز ✓
                    </Badge>
                  ) : showStepBadge ? (
                    <Badge variant="amber" size="sm" className="font-black animate-bounce [animation-duration:2s]">
                      نیاز این گام ⭐
                    </Badge>
                  ) : null}
                </div>
              )
            })}
          </div>

          <div className={`mt-auto pt-3 border-t text-[11px] ${isLight ? 'border-slate-200 text-slate-500' : 'border-indigo-500/20 text-indigo-300/80'}`}>
            <span>📖 کتاب درسی: فصل {experiment.textbook.chapterNumber}، صفحه {experiment.textbook.page}</span>
          </div>
        </div>

        {/* Center/Left 3 Columns in RTL: Virtual Interactive Workbench Surface */}
        <div className="lg:col-span-3 space-y-4">
          
          {/* Virtual Table Surface */}
          <div className={`rounded-3xl relative overflow-hidden min-h-[500px] flex flex-col justify-between transition-all ${
            isLight
              ? 'natural-workbench'
              : 'border-2 border-indigo-500/30 bg-gradient-to-b from-slate-900/95 via-slate-950 to-indigo-950/90 shadow-2xl shadow-indigo-950/40'
          }`}>
            <div className={`absolute inset-0 lab-grid-bg pointer-events-none ${isLight ? 'opacity-20' : 'opacity-35'}`} />

            {/* Workbench Top Bar: Active Items on Table */}
            <div className={`relative z-10 px-6 py-3.5 border-b flex flex-wrap items-center justify-between gap-3 text-xs ${
              isLight
                ? 'border-slate-200 bg-white/95 text-slate-800 backdrop-blur-md'
                : 'border-indigo-500/20 bg-gradient-to-r from-indigo-950/90 via-slate-900/90 to-teal-950/80 text-white'
            }`}>
              <span className={`font-black flex items-center gap-2 text-sm ${isLight ? 'text-slate-900' : 'text-white'}`}>
                <span>🧪 میز کار آزمایشگاه ({workbenchItems.length} وسیله فعال)</span>
              </span>

              {/* Items chips */}
              <div className="flex flex-wrap items-center gap-2">
                {workbenchItems.length === 0 ? (
                  <span className={`text-[11px] italic ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                    برای شروع، وسایل را از قفسه سمت راست به این میز اضافه کنید.
                  </span>
                ) : (
                  workbenchItems.map((item) => (
                    <span
                      key={item.id}
                      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-bold shadow-xs ${
                        isLight
                          ? 'bg-white border border-slate-300 text-slate-800 hover:border-sky-400'
                          : 'bg-gradient-to-r from-indigo-900/80 to-cyan-950/80 border border-cyan-400/40 text-cyan-200 shadow-sm'
                      }`}
                    >
                      <span>{item.name}</span>
                      <button
                        onClick={() => removeItemFromWorkbench(item.id)}
                        className={`p-0.5 rounded-full transition-colors ${
                          isLight ? 'text-slate-400 hover:text-rose-600 hover:bg-rose-50' : 'text-slate-400 hover:text-rose-400 hover:bg-rose-500/10'
                        }`}
                        title="حذف از میز"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </span>
                  ))
                )}
              </div>
            </div>

            {/* Center Dynamic Graphical Simulation View */}
            <div className="relative z-10 flex-1 flex flex-col items-center justify-center p-6">
              {renderLabSimulationGraphics()}

              {/* Live Feedback Banner */}
              {feedback && (
                <div className="w-full max-w-xl mt-4">
                  <StatusAlert
                    type={feedback.type}
                    title={feedback.title}
                    action={
                      feedback.type === 'error' ? (
                        <Button size="sm" variant={isLight ? 'cyan' : 'cyan'} onClick={handleOpenHint} className="font-bold">
                          دریافت راهنمایی صوتی و سقراطی
                        </Button>
                      ) : undefined
                    }
                  >
                    {feedback.message}
                  </StatusAlert>
                </div>
              )}
            </div>

            {/* Workbench Bottom Action Controls */}
            <div className={`relative z-10 px-6 py-4 border-t flex flex-wrap items-center justify-between gap-4 ${
              isLight
                ? 'border-slate-200 bg-white/95 text-slate-800 backdrop-blur-md'
                : 'border-indigo-500/20 bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/90 text-white'
            }`}>
              <div className="flex items-center gap-3 text-xs">
                <span className={`px-3.5 py-1.5 rounded-2xl font-black text-sm flex items-center gap-1.5 shadow-xs ${
                  isLight
                    ? 'bg-amber-100/90 border border-amber-300 text-amber-900'
                    : 'bg-gradient-to-r from-amber-500/20 to-yellow-500/20 border border-amber-400/40 text-amber-300'
                }`}>
                  <span>امتیاز مهارت:</span>
                  <strong className="font-mono text-base">{score}</strong>/۱۰۰ ⭐
                </span>
                <span className={`px-3 py-1.5 rounded-2xl font-bold text-xs ${
                  isLight ? 'bg-slate-100 border border-slate-200 text-slate-700' : 'bg-slate-800/80 border border-slate-700/60 text-slate-300'
                }`}>
                  راهنماهای مصرف‌شده: <strong className={isLight ? 'text-sky-700 font-mono' : 'text-cyan-300 font-mono'}>{hintsUsed.length}</strong>
                </span>
              </div>

              <div className="flex items-center gap-2">
                {!isCompleted && (
                  <Button
                    variant="cyan"
                    size="md"
                    onClick={executeCurrentAction}
                    rightIcon={<Play className="w-4 h-4" />}
                    className="bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 hover:from-emerald-600 hover:to-teal-600 text-white font-black shadow-lg shadow-emerald-500/25 text-sm px-6 py-2.5 rounded-xl hover:scale-105 active:scale-95 transition-all"
                  >
                    اجرا و ثبت گام {currentStepIndex} 🚀
                  </Button>
                )}
                {isCompleted && (
                  <Button
                    variant="cyan"
                    size="md"
                    onClick={() => setCompletionModalOpen(true)}
                    rightIcon={<Award className="w-4 h-4" />}
                    className="bg-gradient-to-r from-amber-400 to-yellow-400 text-slate-950 font-black shadow-lg shadow-amber-400/30 text-sm px-6 py-2.5 rounded-xl hover:scale-105 active:scale-95 transition-all"
                  >
                    مشاهده کارنامه نهایی 🏆
                  </Button>
                )}
              </div>
            </div>

          </div>

          {/* Observations & History Logs Panel */}
          <div className={`rounded-3xl p-5 space-y-3.5 shadow-sm transition-all ${
            isLight
              ? 'border border-emerald-200 bg-white text-slate-800'
              : 'border border-emerald-500/30 bg-gradient-to-br from-emerald-950/30 via-slate-900/80 to-slate-900 shadow-lg shadow-emerald-950/20 text-white'
          }`}>
            <h4 className={`text-sm font-black flex items-center gap-2 ${isLight ? 'text-emerald-900' : 'text-white'}`}>
              <CheckCircle2 className="w-5 h-5 text-emerald-500" />
              <span>دفترچه مشاهدات علمی ثبت‌شده در آزمایشگاه 📝✨</span>
            </h4>
            {observations.length === 0 ? (
              <p className={`text-xs leading-relaxed ${isLight ? 'text-slate-600' : 'text-slate-300'}`}>
                هنوز مشاهده‌ای ثبت نشده است. با اجرای صحیح مراحل، پدیده‌ها و نتایج علمی ثبت‌شده در اینجا ظاهر خواهند شد.
              </p>
            ) : (
              <ul className="space-y-2 text-xs">
                {observations.map((obs, i) => (
                  <li key={i} className={`flex items-start gap-3 p-3 rounded-2xl border shadow-xs ${
                    isLight
                      ? 'bg-emerald-50/70 border-emerald-200 text-emerald-950'
                      : 'bg-slate-950/80 border-emerald-500/25 text-emerald-100'
                  }`}>
                    <span className={`w-6 h-6 rounded-lg font-mono text-xs flex items-center justify-center shrink-0 mt-0.5 font-bold border ${
                      isLight
                        ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                        : 'bg-emerald-500/20 text-emerald-300 border-emerald-400/30'
                    }`}>
                      {i + 1}
                    </span>
                    <span className="leading-relaxed font-medium">{obs}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Predictions History Card */}
          {predictionsLog.length > 0 && (
            <div className="rounded-2xl border border-cyan-500/30 bg-slate-900/60 p-4 space-y-3 animate-in fade-in duration-300">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 font-bold text-white">
                  <Sparkles className="w-4 h-4 text-cyan-400" />
                  <span>کارنامه فرضیه‌سازی و پیش‌بینی‌های علمی شما</span>
                </div>
                <span className="text-[11px] text-cyan-400 font-mono font-bold">
                  {predictionsLog.filter((p) => p.isCorrect).length} از {predictionsLog.length} پیش‌بینی دقیق
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                {predictionsLog.map((p, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-xl border flex flex-col justify-between gap-1.5 ${
                      p.isCorrect
                        ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-200'
                        : 'bg-amber-950/20 border-amber-600/30 text-amber-200'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[11px]">گام {p.stepIndex}: {p.isCorrect ? 'فرضیه تایید شد 🎯' : 'کشف تفاوت فرضیه 💡'}</span>
                      <Badge variant={p.isCorrect ? 'emerald' : 'amber'} size="sm">
                        {p.isCorrect ? '+۱۰ امتیاز' : 'یادگیری علمی'}
                      </Badge>
                    </div>
                    <p className="text-[11px] text-slate-300">
                      فرضیه شما: <strong>{p.selectedOption}</strong>
                    </p>
                    <p className="text-[10px] text-slate-400 leading-relaxed border-t border-slate-800/60 pt-1">
                      {p.explanation}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

      </div>

      {/* MODAL 1: INTELLIGENT HINT MODAL */}
      <Modal
        isOpen={hintModalOpen}
        onClose={() => setHintModalOpen(false)}
        title={`راهنمای هوشمند آموزشی — سطح ${activeHintLevel}`}
        description="هدایت مرحله‌ای دانش‌آموز بر اساس مبانی کتب درسی و بدون افشای مستقیم پاسخ"
      >
        <div className="space-y-4 pt-2">
          <div className="flex items-center gap-2">
            <Badge variant={activeHintLevel === 1 ? 'indigo' : activeHintLevel === 2 ? 'amber' : 'cyan'}>
              {activeHintLevel === 1
                ? 'سطح ۱: پرسش تفکری (سقراطی)'
                : activeHintLevel === 2
                ? 'سطح ۲: سرنخ مفهومی و جهت‌دهنده'
                : 'سطح ۳: توضیح کامل علمی و اقدام اصلاحی'}
            </Badge>
          </div>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 leading-relaxed">
            {hintContent}
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-slate-800">
            <Button variant="outline" size="sm" onClick={() => setHintModalOpen(false)}>
              متوجه شدم
            </Button>
            {activeHintLevel < 3 && (
              <Button variant="cyan" size="sm" onClick={handleNextHintLevel}>
                نیاز به سرنخ بیشتر (سطح {activeHintLevel + 1})
              </Button>
            )}
          </div>
        </div>
      </Modal>

      {/* MODAL 2: COMPLETION & SCORECARD MODAL */}
      <Modal
        isOpen={completionModalOpen}
        onClose={() => setCompletionModalOpen(false)}
        title="تبریک! آزمایش با موفقیت تکمیل شد"
        description="عملکرد شما بر اساس قواعد علمی معتبر ارزیابی و ثبت شد."
      >
        <div className="space-y-4 pt-2 text-right">
          <div className="p-6 rounded-2xl bg-gradient-to-br from-cyan-950/60 to-blue-950/60 border border-cyan-500/30 text-center space-y-2">
            <Award className="w-12 h-12 text-cyan-400 mx-auto" />
            <h3 className="text-xl font-black text-white">نمره علمی شما: {score} از ۱۰۰</h3>
            <p className="text-xs text-slate-300">
              {score >= 90
                ? 'عالی! بدون نقض پیش‌نیازها و با حداقل درخواست راهنمایی آزمایش را به سرانجام رساندید.'
                : 'آفرین! آزمایش با موفقیت انجام شد؛ برای کسب امتیاز ۱۰۰ می‌توانید دوباره آزمایش را تمرین کنید.'}
            </p>
          </div>

          <div className="p-3 rounded-xl bg-indigo-950/40 border border-indigo-900/60 text-xs text-indigo-200">
            <strong>ثبت کارنامه در پنل دبیر:</strong> نتایج، نمره علمی و فرضیه‌های شما با موفقیت برای دبیر کلاس جهت ارزیابی و ثبت بازخورد ارسال گردید.
          </div>

          <div className="space-y-2">
            <h5 className="text-xs font-bold text-slate-300">خلاصه مشاهدات ثبت‌شده:</h5>
            <div className="max-h-36 overflow-y-auto space-y-1 text-xs text-slate-400">
              {observations.map((obs, idx) => (
                <div key={idx} className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                  {obs}
                </div>
              ))}
            </div>
          </div>

          <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-2">
            <Button variant="outline" size="sm" onClick={() => resetWorkbench()}>
              تکرار آزمایش
            </Button>
            <Button variant="cyan" size="sm" onClick={() => navigate('/dashboard')}>
              مشاهده در داشبورد
            </Button>
          </div>
        </div>
      </Modal>

      {/* دستیار صوتی هوشمند آزمایشگاه علوم تجربی (Voice AI Assistant) */}
      <VoiceAssistantWidget
        attemptId={attemptId}
        experimentTitle={experiment.title}
        experimentSlug={experiment.slug}
        currentStepIndex={currentStepIndex}
        lastErrorCode={lastErrorCode}
        lastActionSummary={feedback?.message}
      />

    </div>
  )
}
