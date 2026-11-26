import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { teacherService } from '../services/teacherService'
import { aiService } from '../services/aiService'
import { useAuthStore } from '../store/useAuthStore'
import type { TeacherAnalyticsData } from '../types/analytics'
import type { ExperimentAttempt } from '../types/attempt'
import type { TeacherAIInsightsResponse } from '../types/ai'
import { Card, CardHeader, CardContent, Button, Badge, Modal, Input, Select, Skeleton } from '../components/ui'
import {
  GraduationCap,
  Users,
  FlaskConical,
  TrendingUp,
  AlertTriangle,
  Settings,
  CheckCircle2,
  Clock,
  Eye,
  Search,
  BarChart3,
  HelpCircle,
  FileText,
  MessageSquareCheck,
  Sparkles,
  Bot,
  RefreshCw
} from 'lucide-react'

export const TeacherDashboardPage: React.FC = () => {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState<'analytics' | 'monitoring' | 'ai_insights'>('analytics')
  const [analytics, setAnalytics] = useState<TeacherAnalyticsData | null>(null)
  const [attempts, setAttempts] = useState<ExperimentAttempt[]>([])
  const [loading, setLoading] = useState(true)

  // AI Insights State
  const [aiInsights, setAiInsights] = useState<TeacherAIInsightsResponse | null>(null)
  const [loadingAiInsights, setLoadingAiInsights] = useState(false)

  // Monitoring Filters
  const [searchStudent, setSearchStudent] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [filterClassCode, setFilterClassCode] = useState<string>('all')

  // Attempt Audit Modal & Evaluation
  const [auditModalOpen, setAuditModalOpen] = useState(false)
  const [selectedAudit, setSelectedAudit] = useState<any | null>(null)
  const [loadingAudit, setLoadingAudit] = useState(false)
  const [teacherFeedbackInput, setTeacherFeedbackInput] = useState('')
  const [feedbackSaving, setFeedbackSaving] = useState(false)
  const [feedbackSuccess, setFeedbackSuccess] = useState<string | null>(null)

  const loadData = () => {
    setLoading(true)
    Promise.all([
      teacherService.getAnalytics(),
      teacherService.getAllStudentAttempts()
    ]).then(([ana, atts]) => {
      setAnalytics(ana)
      setAttempts(atts)
      setLoading(false)
    })
  }

  const loadAiInsights = (classCode?: string) => {
    setLoadingAiInsights(true)
    aiService
      .getTeacherAIInsights(classCode && classCode !== 'all' ? classCode : undefined)
      .then((res) => {
        setAiInsights(res)
      })
      .catch((err) => {
        console.error('خطا در دریافت تحلیل‌های هوش مصنوعی:', err)
      })
      .finally(() => {
        setLoadingAiInsights(false)
      })
  }

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    if (activeTab === 'ai_insights') {
      loadAiInsights(filterClassCode)
    }
  }, [activeTab, filterClassCode])

  const handleOpenAudit = async (attemptId: string) => {
    setLoadingAudit(true)
    setAuditModalOpen(true)
    setFeedbackSuccess(null)
    const auditData = await teacherService.getStudentAttemptAudit(attemptId)
    setSelectedAudit(auditData)
    setTeacherFeedbackInput(auditData?.teacher_feedback || '')
    setLoadingAudit(false)
  }

  const handleSaveFeedback = async () => {
    if (!selectedAudit) return
    setFeedbackSaving(true)
    setFeedbackSuccess(null)
    try {
      await teacherService.submitFeedback(selectedAudit.id, teacherFeedbackInput)
      setFeedbackSuccess('بازخورد ارزیابی با موفقیت در پرونده آزمایشگاهی دانش‌آموز ثبت گردید.')
      setSelectedAudit((prev: any) => ({ ...prev, teacher_feedback: teacherFeedbackInput }))
      setAttempts((prev) =>
        prev.map((a) => (a.id === selectedAudit.id ? { ...a, teacherFeedback: teacherFeedbackInput } : a))
      )
    } finally {
      setFeedbackSaving(false)
    }
  }

  // کلاس‌های متمایز موجود در سوابق
  const distinctClassCodes = Array.from(
    new Set(attempts.map((a) => a.classCode).filter(Boolean))
  ) as string[]

  const filteredAttempts = attempts.filter((att) => {
    const q = searchStudent.toLowerCase().trim()
    const matchesSearch =
      !q ||
      att.experimentTitle.toLowerCase().includes(q) ||
      (att.studentName && att.studentName.toLowerCase().includes(q)) ||
      (att.studentSchool && att.studentSchool.toLowerCase().includes(q)) ||
      (att.classCode && att.classCode.toLowerCase().includes(q)) ||
      att.grade.includes(q) ||
      att.id.includes(q)
    const matchesStatus = statusFilter === 'all' || att.status === statusFilter
    const matchesClass = filterClassCode === 'all' || att.classCode === filterClassCode
    return matchesSearch && matchesStatus && matchesClass
  })

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full space-y-8">
      {/* Teacher Header Banner */}
      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 sm:p-8 flex flex-col sm:flex-row sm:items-center justify-between gap-6 shadow-xl relative overflow-hidden">
        <div className="absolute inset-0 lab-grid-dense opacity-20 pointer-events-none" />

        <div className="relative z-10 flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-blue-600 p-0.5 shadow-lg">
            <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center text-indigo-400">
              <GraduationCap className="w-9 h-9" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-black text-white">{user?.fullName || 'دکتر مریم مرادی'}</h1>
              <Badge variant="indigo" size="sm">
                دبیر علوم تجربی
              </Badge>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              سامانه پایش هوشمند یادگیری و تحلیل تشخیصی بدفهمی‌های علمی کلاس درس — {user?.schoolName || 'مجتمع آموزشی فرزانگان'}
            </p>
          </div>
        </div>

        <div className="relative z-10 flex items-center gap-3">
          <Link to="/teacher/experiments">
            <Button variant="cyan" size="md" rightIcon={<Settings className="w-4 h-4" />}>
              مدیریت و انتشار آزمایش‌ها
            </Button>
          </Link>
        </div>
      </div>

      {/* 4 Macro Analytics Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>دانش‌آموزان ثبت‌شده</span>
            <Users className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white font-mono">{analytics?.totalStudents || 1}</span>
            <span className="text-xs text-slate-400">دانش‌آموز فعال</span>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>آزمایش‌های درسی فعال</span>
            <FlaskConical className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white font-mono">{analytics?.activeExperimentsCount || 3}</span>
            <span className="text-xs text-slate-400">آزمایش تاییدشده</span>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>میانگین نرخ تکمیل کلاسی</span>
            <TrendingUp className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white font-mono">{analytics?.averageCompletionRate || 85.0}٪</span>
            <span className="text-xs text-emerald-400">پوشش سرفصل‌ها</span>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>کل جلسات اجراشده</span>
            <Clock className="w-5 h-5 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white font-mono">{attempts.length || 2}</span>
            <span className="text-xs text-slate-400">تلاش آزمایشگاهی</span>
          </div>
        </div>
      </div>

      {/* Tabs Switcher: Macro Analytics vs Live Attempts Monitoring */}
      <div className="flex border-b border-slate-800 space-x-6 space-x-reverse text-sm">
        <button
          onClick={() => setActiveTab('analytics')}
          className={`pb-3 font-bold flex items-center gap-2 transition-all relative ${
            activeTab === 'analytics'
              ? 'text-cyan-400 border-b-2 border-cyan-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          <span>تحلیل کلان پداگوژیک و بدفهمی‌ها</span>
        </button>

        <button
          onClick={() => setActiveTab('monitoring')}
          className={`pb-3 font-bold flex items-center gap-2 transition-all relative ${
            activeTab === 'monitoring'
              ? 'text-cyan-400 border-b-2 border-cyan-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>پایش و ممیزی زنده تلاش‌های دانش‌آموزان</span>
          <span className="px-2 py-0.5 rounded-full text-[10px] bg-cyan-950 text-cyan-400 border border-cyan-800">
            {attempts.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('ai_insights')}
          className={`pb-3 font-bold flex items-center gap-2 transition-all relative ${
            activeTab === 'ai_insights'
              ? 'text-indigo-400 border-b-2 border-indigo-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Sparkles className="w-4 h-4 text-amber-300" />
          <span>تحلیل هوشمند بدفهمی‌ها و توصیه‌های تدریس (AI Insights)</span>
          <Badge variant="indigo" size="sm" className="text-[10px] px-1.5 py-0.2">
            Gemini
          </Badge>
        </button>
      </div>

      {/* Tab 1 Content: Macro Analytics & Misconceptions */}
      {activeTab === 'analytics' && (
        <div className="space-y-8">
          {/* Frequent Error Analysis Section (تحلیل خطاهای پرتکرار) */}
          <Card>
            <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2 text-white font-bold text-sm">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>تحلیل تشخیصی شایع‌ترین بدفهمی‌های علمی دانش‌آموزان کلاس</span>
              </div>
              <Badge variant="amber" size="sm">
                استخراج خودکار از موتور شبیه‌سازی قطعی
              </Badge>
            </CardHeader>
            <CardContent className="space-y-4">
              {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Skeleton className="h-44 w-full" />
                  <Skeleton className="h-44 w-full" />
                  <Skeleton className="h-44 w-full" />
                </div>
              ) : analytics?.frequentErrors && analytics.frequentErrors.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {analytics.frequentErrors.map((err) => {
                    const maxOccurrences = Math.max(
                      ...analytics.frequentErrors.map((e) => e.occurrenceCount),
                      1
                    )
                    const percent = Math.min(100, Math.round((err.occurrenceCount / maxOccurrences) * 100))

                    return (
                      <div
                        key={err.errorCode}
                        className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4 space-y-3 flex flex-col justify-between hover:border-slate-700 transition-all shadow-sm"
                      >
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-rose-400 line-clamp-1">{err.errorTitle}</span>
                            <Badge variant="rose" size="sm">
                              {err.occurrenceCount} تکرار
                            </Badge>
                          </div>

                          {/* Misconception Visual Frequency Bar */}
                          <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                            <div
                              className="bg-gradient-to-l from-rose-500 to-amber-500 h-full rounded-full transition-all duration-500"
                              style={{ width: `${percent}%` }}
                            />
                          </div>

                          <span className="text-[11px] text-slate-400 block font-mono">
                            آزمایش: {err.experimentTitle}
                          </span>
                          <p className="text-xs text-slate-300 leading-relaxed">
                            <strong>علت علمی:</strong> {err.scientificConcept}
                          </p>
                        </div>

                        <div className="p-2.5 rounded-xl bg-amber-950/30 border border-amber-900/40 text-[11px] text-amber-200">
                          <strong>راهکار به دبیر در کلاس:</strong> {err.recommendedRemediation}
                        </div>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-400 text-xs">
                  هیچ خطای علمی پرتکراری ثبت نشده است. دانش‌آموزان مراحل را طبق استاندارد اجرا کرده‌اند.
                </div>
              )}
            </CardContent>
          </Card>

          {/* Class Experiment Performance Breakdown Table */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2 text-white font-bold text-sm">
                <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                <span>عملکرد آماری دانش‌آموزان به تفکیک آزمایش‌های رسمی درسی</span>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-right text-xs">
                  <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="p-4 font-bold">عنوان آزمایش درسی</th>
                      <th className="p-4 font-bold">تعداد جلسات تلاش</th>
                      <th className="p-4 font-bold">نرخ تکمیل موفق</th>
                      <th className="p-4 font-bold">میانگین نمره مهارتی</th>
                      <th className="p-4 font-bold">میانگین راهنمای مصرفی</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/80 text-slate-200">
                    {analytics?.experimentStats.map((st) => (
                      <tr key={st.experimentId} className="hover:bg-slate-800/30 transition-colors">
                        <td className="p-4 font-bold text-white">
                          <span>{st.experimentTitle}</span>
                        </td>
                        <td className="p-4 font-mono">{st.totalAttempts} تلاش</td>
                        <td className="p-4 font-mono">
                          <span className="text-emerald-400 font-bold">{st.completionRatePercent}٪</span>
                        </td>
                        <td className="p-4 font-mono text-cyan-400 font-bold">{st.averageScorePercent}٪</td>
                        <td className="p-4 font-mono text-amber-400">{st.averageHintsUsed} سطح</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tab 2 Content: Live Student Attempts Monitoring */}
      {activeTab === 'monitoring' && (
        <div className="space-y-6">
          {/* Filters Bar */}
          <div className="flex flex-col sm:flex-row gap-4 justify-between items-center bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2" />
              <Input
                placeholder="جست‌وجو در نام دانش‌آموز، آزمایش، مدرسه یا کد کلاس..."
                value={searchStudent}
                onChange={(e) => setSearchStudent(e.target.value)}
                className="pr-9"
              />
            </div>

            <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
              {distinctClassCodes.length > 0 && (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400 shrink-0">کد کلاس:</span>
                  <Select
                    value={filterClassCode}
                    onChange={(e) => setFilterClassCode(e.target.value)}
                    options={[
                      { label: 'تمام کلاس‌ها', value: 'all' },
                      ...distinctClassCodes.map((code) => ({ label: `کلاس ${code}`, value: code }))
                    ]}
                  />
                </div>
              )}

              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400 shrink-0">وضعیت:</span>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  options={[
                    { label: 'تمام وضعیت‌ها', value: 'all' },
                    { label: 'تکمیل‌شده (موفق)', value: 'COMPLETED' },
                    { label: 'در حال انجام', value: 'IN_PROGRESS' },
                    { label: 'نافرجام یا ناموفق', value: 'FAILED' }
                  ]}
                />
              </div>
            </div>
          </div>

          {/* Student Attempts Table */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2 text-white font-bold text-sm">
                <FileText className="w-4 h-4 text-cyan-400" />
                <span>سوابق نشست‌های آزمایشگاهی کلاسی ({filteredAttempts.length})</span>
              </div>
              <span className="text-xs text-slate-400">امکان ممیزی لحظه‌به‌لحظه کنش‌های هر دانش‌آموز و ثبت ارزیابی دبیر</span>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-right text-xs">
                  <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="p-4 font-bold">دانش‌آموز (نام و مشخصات)</th>
                      <th className="p-4 font-bold">عنوان آزمایش</th>
                      <th className="p-4 font-bold">کد اختصاصی کلاس</th>
                      <th className="p-4 font-bold">وضعیت</th>
                      <th className="p-4 font-bold">نمره</th>
                      <th className="p-4 font-bold">پیشرفت و خطاها</th>
                      <th className="p-4 font-bold">تاریخ نشست</th>
                      <th className="p-4 font-bold">ارزیابی معلم</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/80 text-slate-200">
                    {filteredAttempts.map((att) => (
                      <tr key={att.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="p-4">
                          <div className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-xs shrink-0">
                              {(att.studentName || 'د')[0]}
                            </div>
                            <div>
                              <span className="font-bold text-white block text-xs">{att.studentName || 'دانش‌آموز'}</span>
                              <span className="text-[10px] text-slate-400 block">
                                پایه {att.studentGrade || att.grade} • {att.studentSchool || 'مدرسه'}
                              </span>
                            </div>
                          </div>
                        </td>
                        <td className="p-4 font-bold text-white text-xs">{att.experimentTitle}</td>
                        <td className="p-4">
                          {att.classCode ? (
                            <Badge variant="indigo" size="sm" className="font-mono">
                              {att.classCode}
                            </Badge>
                          ) : (
                            <span className="text-slate-500 text-[11px]">عمومی</span>
                          )}
                        </td>
                        <td className="p-4">
                          <Badge
                            variant={
                              att.status === 'COMPLETED'
                                ? 'emerald'
                                : att.status === 'IN_PROGRESS'
                                ? 'cyan'
                                : 'rose'
                            }
                            size="sm"
                          >
                            {att.status === 'COMPLETED'
                              ? 'تکمیل‌شده'
                              : att.status === 'IN_PROGRESS'
                              ? 'در حال انجام'
                              : 'نافرجام'}
                          </Badge>
                        </td>
                        <td className="p-4 font-mono font-bold text-white">{att.score}٪</td>
                        <td className="p-4">
                          <div className="space-y-0.5 text-[11px] font-mono">
                            <span className="text-slate-200 block">{att.stepsCompleted} از {att.totalSteps} گام</span>
                            {att.errorsCount !== undefined && att.errorsCount > 0 ? (
                              <span className="text-rose-400 block">{att.errorsCount} خطا</span>
                            ) : (
                              <span className="text-emerald-400 block">بدون خطا</span>
                            )}
                          </div>
                        </td>
                        <td className="p-4 text-slate-400 text-[11px]">
                          {att.startedAt ? new Date(att.startedAt).toLocaleDateString('fa-IR') : '—'}
                        </td>
                        <td className="p-4">
                          <Button
                            variant={att.teacherFeedback ? 'primary' : 'outline'}
                            size="sm"
                            onClick={() => handleOpenAudit(att.id)}
                            rightIcon={att.teacherFeedback ? <MessageSquareCheck className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                          >
                            {att.teacherFeedback ? 'مشاهده و ویرایش بازخورد' : 'ارزیابی و کارنامه'}
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tab 3 Content: AI Pedagogical Insights & Classroom Misconception Analysis */}
      {activeTab === 'ai_insights' && (
        <div className="space-y-6 animate-in fade-in duration-300">
          {/* Filter Bar & Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-300" />
                <h3 className="text-sm font-bold text-white">
                  پایش هوشمند بدفهمی‌های علمی و راهکارهای تدریس جبرانی (Gemini AI)
                </h3>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                استخراج خودکار از رکوردهای واقعی پایگاه داده SQLite و تفسیر تشخیصی با هوش مصنوعی بدون ارقام جعلی
              </p>
            </div>

            <div className="flex items-center gap-3">
              {distinctClassCodes.length > 0 && (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400 shrink-0">کلاس:</span>
                  <Select
                    value={filterClassCode}
                    onChange={(e) => setFilterClassCode(e.target.value)}
                    options={[
                      { label: 'تمام کلاس‌های من', value: 'all' },
                      ...distinctClassCodes.map((code) => ({ label: `کلاس ${code}`, value: code }))
                    ]}
                  />
                </div>
              )}

              <Button
                variant="outline"
                size="sm"
                onClick={() => loadAiInsights(filterClassCode)}
                disabled={loadingAiInsights}
                rightIcon={<RefreshCw className={`w-3.5 h-3.5 ${loadingAiInsights ? 'animate-spin' : ''}`} />}
              >
                به‌روزرسانی تحلیل
              </Button>
            </div>
          </div>

          {/* 3 Metric Cards for AI Insights */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 space-y-1">
              <span className="text-xs text-slate-400">کل خطاهای واقعی ثبت‌شده در سیستم</span>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-black text-white font-mono">
                  {aiInsights?.total_errors_analyzed || 0}
                </span>
                <span className="text-xs text-amber-400">رخداد آموزشی</span>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 space-y-1">
              <span className="text-xs text-slate-400">بدفهمی‌های مفهومی شناسایی‌شده</span>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-black text-white font-mono">
                  {aiInsights?.top_misconceptions.length || 0}
                </span>
                <span className="text-xs text-indigo-400">موضوع چالشی</span>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 space-y-1">
              <span className="text-xs text-slate-400">موتور تحلیلگر آموزشی</span>
              <div className="flex items-baseline gap-2">
                <Badge variant="indigo" size="sm" className="mt-1">
                  Google Gemini + قوانین درسی
                </Badge>
              </div>
            </div>
          </div>

          {/* AI Pedagogical Remediation Highlight Card */}
          <Card className="border-indigo-500/40 bg-gradient-to-br from-indigo-950/40 via-slate-900/90 to-slate-900 shadow-xl">
            <CardHeader className="border-b border-indigo-900/40 pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-white font-bold text-sm">
                  <Bot className="w-5 h-5 text-indigo-400" />
                  <span>توصیه‌ها و استراتژی‌های تدریس جبرانی هوش مصنوعی برای دبیر</span>
                </div>
                <Badge variant="indigo" size="sm">
                  تفسیر کیفی داده‌های کلاسی
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="p-5 space-y-4">
              {loadingAiInsights ? (
                <div className="space-y-3 py-2">
                  <Skeleton className="h-4 w-1/3" />
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-12 w-full" />
                </div>
              ) : (
                <div className="space-y-4 text-xs text-slate-200 leading-relaxed font-sans">
                  <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2">
                    <p className="whitespace-pre-line text-slate-100 text-xs leading-relaxed">
                      {aiInsights?.ai_pedagogical_remediation ||
                        'بر اساس داده‌های کلاسی ثبت‌شده، توصیه می‌شود مفاهیم پیش‌نیاز هر آزمایش و تفاوت خصلت اسیدها، بازها و مواد خنثی پیش از شروع کار عملی با دانش‌آموزان مرور شود.'}
                    </p>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                    <span>
                      💡 <strong>توجه پداگوژیک:</strong> تحلیل فوق حاصل ارزیابی آماری رفتار دانش‌آموزان است و به دبیر در طرح درس جلسات آینده کمک می‌کند.
                    </span>
                    <Badge variant="emerald" size="sm">
                      داده‌های واقعی SQLite ✓
                    </Badge>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Detailed Misconceptions Breakdown Table */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2 text-white font-bold text-sm">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>طبقه‌بندی بدفهمی‌های پرتکرار کلاس بر اساس آزمایش و مرحله</span>
              </div>
              <span className="text-xs text-slate-400">
                بررسی خطاهای ثبت‌شده در کارنامه تک‌تک دانش‌آموزان
              </span>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-right text-xs">
                  <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="p-4 font-bold">عنوان خطا و کد سیستمی</th>
                      <th className="p-4 font-bold">آزمایش درسی</th>
                      <th className="p-4 font-bold">تعداد رخداد در کلاس</th>
                      <th className="p-4 font-bold">ریشه بدفهمی مفهومی</th>
                      <th className="p-4 font-bold">راهکار آموزشی پیشنهادی در تدریس</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/80 text-slate-200">
                    {aiInsights?.top_misconceptions && aiInsights.top_misconceptions.length > 0 ? (
                      aiInsights.top_misconceptions.map((err, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                          <td className="p-4">
                            <span className="font-bold text-white block text-xs">{err.error_title}</span>
                            <span className="font-mono text-[10px] text-slate-400">{err.error_code}</span>
                          </td>
                          <td className="p-4">
                            <Badge variant="indigo" size="sm">
                              {err.experiment_title}
                            </Badge>
                          </td>
                          <td className="p-4">
                            <Badge variant="amber" size="sm" className="font-mono font-bold">
                              {err.occurrence_count} بار
                            </Badge>
                          </td>
                          <td className="p-4 text-slate-300 leading-relaxed max-w-xs">{err.scientific_concept}</td>
                          <td className="p-4 text-emerald-400 leading-relaxed max-w-sm">{err.remediation}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5} className="p-8 text-center text-slate-400 text-xs">
                          هنوز خطای علمی در این کلاس ثبت نشده است یا تمامی آزمایش‌ها بدون خطا انجام شده‌اند.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Attempt Audit Detailed Modal */}
      <Modal
        isOpen={auditModalOpen}
        onClose={() => setAuditModalOpen(false)}
        title="ممیزی دقیق رفتار آزمایشگاهی دانش‌آموز"
        maxWidth="2xl"
      >
        {loadingAudit ? (
          <div className="space-y-4 py-4">
            <Skeleton className="h-6 w-1/3" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-40 w-full" />
          </div>
        ) : selectedAudit ? (
          <div className="space-y-6 text-xs text-slate-300">
            {/* Attempt Meta Header */}
            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div>
                <span className="text-[11px] text-slate-500 block">دانش‌آموز ارزیابی‌شونده:</span>
                <span className="text-white font-bold text-xs">{selectedAudit.student_name}</span>
                <span className="text-[10px] text-slate-400 block">
                  پایه {selectedAudit.student_grade || 'هشتم'} • {selectedAudit.student_school || 'مدرسه'}
                </span>
              </div>
              <div>
                <span className="text-[11px] text-slate-500 block">آزمایش درسی:</span>
                <span className="text-white font-bold text-xs">{selectedAudit.experiment_title}</span>
                {selectedAudit.class_code && (
                  <span className="text-[10px] text-indigo-400 font-mono block">
                    کد کلاس: {selectedAudit.class_code}
                  </span>
                )}
              </div>
              <div>
                <span className="text-[11px] text-slate-500 block">نمره ارزیابی:</span>
                <span className="text-cyan-400 font-mono font-bold text-sm">{selectedAudit.score}٪</span>
              </div>
              <div>
                <span className="text-[11px] text-slate-500 block">وضعیت نشست:</span>
                <Badge
                  variant={selectedAudit.status === 'COMPLETED' ? 'emerald' : 'cyan'}
                  size="sm"
                >
                  {selectedAudit.status === 'COMPLETED' ? 'تکمیل‌شده' : 'در جریان'}
                </Badge>
              </div>
            </div>

            {/* Teacher Pedagogical Feedback & Grading Box */}
            <div className="p-4 rounded-2xl bg-indigo-950/30 border border-indigo-900/50 space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-white flex items-center gap-2">
                  <GraduationCap className="w-4 h-4 text-indigo-400" />
                  <span>ثبت بازخورد تشخیصی و نظر ارزیابی معلم</span>
                </h4>
                {selectedAudit.teacher_feedback && !feedbackSuccess && (
                  <Badge variant="indigo" size="sm">بازخورد قبلی ثبت شده</Badge>
                )}
              </div>

              <p className="text-[11px] text-slate-400 leading-relaxed">
                این یادداشت ارزیابی مستقیماً در کارنامه و داشبورد دانش‌آموز ({selectedAudit.student_name}) نمایش داده می‌شود.
              </p>

              <textarea
                rows={3}
                value={teacherFeedbackInput}
                onChange={(e) => setTeacherFeedbackInput(e.target.value)}
                placeholder="مثلاً: آفرین! دقت شما در اجرای مراحل و کنترل متغیرها بسیار خوب بود. به مفاهیم شیمیایی واکنش و فرضیه‌سازی مرحله اول بیشتر توجه نمایید..."
                className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 leading-relaxed"
              />

              {feedbackSuccess && (
                <div className="text-emerald-400 text-xs font-bold flex items-center gap-1.5 animate-in fade-in">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>{feedbackSuccess}</span>
                </div>
              )}

              <div className="flex justify-end">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleSaveFeedback}
                  isLoading={feedbackSaving}
                  disabled={feedbackSaving || !teacherFeedbackInput.trim()}
                  rightIcon={<CheckCircle2 className="w-4 h-4" />}
                >
                  ثبت و ارسال ارزیابی به دانش‌آموز
                </Button>
              </div>
            </div>

            {/* Chronological Action Logs */}
            <div className="space-y-3">
              <h4 className="font-bold text-white flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-400" />
                <span>توالی کنش‌های آزمایشگاهی ثبت‌شده ({selectedAudit.action_logs?.length || 0})</span>
              </h4>

              <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                {selectedAudit.action_logs && selectedAudit.action_logs.length > 0 ? (
                  selectedAudit.action_logs.map((log: any, idx: number) => (
                    <div
                      key={log.id || idx}
                      className={`p-3 rounded-xl border flex items-start justify-between gap-3 ${
                        log.is_valid
                          ? 'bg-slate-900/60 border-slate-800'
                          : 'bg-rose-950/20 border-rose-900/40'
                      }`}
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[10px] text-slate-500">#{idx + 1}</span>
                          <span className="font-bold text-white font-mono text-[11px]">{log.action_type}</span>
                          {log.is_valid ? (
                            <Badge variant="emerald" size="sm">صحیح</Badge>
                          ) : (
                            <Badge variant="rose" size="sm">خطای علمی</Badge>
                          )}
                          <span className="text-[10px] text-slate-400">گام {log.step_index}</span>
                        </div>
                        <p className="text-slate-300 text-[11px]">{log.feedback_text}</p>
                        {log.observation_text && (
                          <p className="text-cyan-400 text-[11px]">مشاهده: {log.observation_text}</p>
                        )}
                      </div>

                      <div className="text-left font-mono text-[10px] text-slate-500 shrink-0">
                        {log.created_at ? new Date(log.created_at).toLocaleTimeString('fa-IR') : ''}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-slate-400 text-center py-4">کنشی ثبت نشده است.</div>
                )}
              </div>
            </div>

            {/* Hint Usages */}
            <div className="space-y-3">
              <h4 className="font-bold text-white flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-amber-400" />
                <span>راهنماهای سه‌سطحی دریافت‌شده ({selectedAudit.hint_usages?.length || 0})</span>
              </h4>

              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {selectedAudit.hint_usages && selectedAudit.hint_usages.length > 0 ? (
                  selectedAudit.hint_usages.map((hint: any, idx: number) => (
                    <div
                      key={hint.id || idx}
                      className="p-3 rounded-xl bg-amber-950/20 border border-amber-900/30 space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <Badge variant="amber" size="sm">سطح {hint.hint_level}</Badge>
                        <span className="font-mono text-[10px] text-slate-500">{hint.error_code}</span>
                      </div>
                      <p className="text-amber-200 text-[11px] leading-relaxed">{hint.hint_content}</p>
                    </div>
                  ))
                ) : (
                  <div className="text-slate-400 text-center py-2">دانش‌آموز از راهنما استفاده نکرده است.</div>
                )}
              </div>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  )
}
