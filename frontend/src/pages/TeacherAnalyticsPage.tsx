import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { teacherService } from '../services/teacherService'
import { experimentService } from '../services/experimentService'
import type {
  AnalyticsOverview,
  MisconceptionItem,
  TeacherStudentItem,
  StudentActionLog
} from '../types/analytics'
import type { Experiment } from '../types/experiment'
import { useThemeStore } from '../store/useThemeStore'
import {
  Users,
  CheckCircle2,
  AlertTriangle,
  Filter,
  Download,
  BookOpen,
  ArrowRight,
  RefreshCw,
  Search,
  FileSpreadsheet,
  Printer,
  X,
  Sparkles,
  GraduationCap
} from 'lucide-react'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Modal } from '../components/ui/Modal'

export const TeacherAnalyticsPage: React.FC = () => {
  const { theme } = useThemeStore()
  const isLight = theme === 'light'

  // داده‌های فیلتر
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [selectedExperimentId, setSelectedExperimentId] = useState<number | undefined>(undefined)
  const [selectedClassCode, setSelectedClassCode] = useState<string>('')
  const [searchTerm, setSearchTerm] = useState<string>('')

  // وضعیت‌های بارگذاری و داده‌ها
  const [loading, setLoading] = useState<boolean>(true)
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null)
  const [misconceptions, setMisconceptions] = useState<MisconceptionItem[]>([])
  const [students, setStudents] = useState<TeacherStudentItem[]>([])

  // دراور / مودال لاگ‌های دانش‌آموز انتخابی
  const [selectedStudent, setSelectedStudent] = useState<TeacherStudentItem | null>(null)
  const [studentLogs, setStudentLogs] = useState<StudentActionLog[]>([])
  const [loadingLogs, setLoadingLogs] = useState<boolean>(false)

  // بارگذاری لیست آزمایش‌ها جهت فیلتر
  useEffect(() => {
    experimentService.getAllExperiments().then((exps) => {
      setExperiments(exps)
    })
  }, [])

  // بارگذاری داده‌های تحلیلی با تغییر فیلترها
  const loadAnalytics = async () => {
    setLoading(true)
    try {
      const filters = {
        experimentId: selectedExperimentId,
        classCode: selectedClassCode || undefined
      }

      const [ovData, miscData, studentsData] = await Promise.all([
        teacherService.getOverview(filters),
        teacherService.getMisconceptions(filters),
        teacherService.getStudentsAnalytics(filters)
      ])

      setOverview(ovData)
      setMisconceptions(miscData.misconceptions)
      setStudents(studentsData)
    } catch (err) {
      console.error('خطا در بارگذاری آمارهای پداگوژیک:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAnalytics()
  }, [selectedExperimentId, selectedClassCode])

  // باز کردن لاگ‌های اقدامات دانش‌آموز
  const handleOpenStudentLogs = async (student: TeacherStudentItem) => {
    setSelectedStudent(student)
    setLoadingLogs(true)
    try {
      const res = await teacherService.getStudentLogs(student.studentId, {
        experimentId: selectedExperimentId
      })
      setStudentLogs(res.logs)
    } catch (err) {
      console.error('خطا در دریافت لاگ دانش‌آموز:', err)
    } finally {
      setLoadingLogs(false)
    }
  }

  // فیلتر جستجوی دانش‌آموزان
  const filteredStudents = students.filter((s) => {
    if (!searchTerm.trim()) return true
    const term = searchTerm.toLowerCase()
    return (
      s.fullName.toLowerCase().includes(term) ||
      s.email.toLowerCase().includes(term) ||
      (s.schoolName && s.schoolName.toLowerCase().includes(term))
    )
  })

  // چاپ گزارش
  const handlePrint = () => {
    window.print()
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 text-right font-sans">
      
      {/* ۱. هدر اصلی صفحه */}
      <div className={`p-6 sm:p-8 rounded-3xl border transition-all ${
        isLight
          ? 'bg-gradient-to-r from-sky-50 via-white to-amber-50/50 border-slate-200/90 shadow-sm'
          : 'bg-gradient-to-r from-slate-900 via-indigo-950/70 to-slate-900 border-indigo-500/30 shadow-xl'
      }`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs">
              <Link to="/teacher/dashboard" className={`flex items-center gap-1 transition-colors ${
                isLight ? 'text-slate-500 hover:text-sky-600' : 'text-indigo-300 hover:text-cyan-300'
              }`}>
                <ArrowRight className="w-3.5 h-3.5" />
                <span>داشبورد معلم</span>
              </Link>
              <span className="text-slate-400">/</span>
              <span className={`font-semibold ${isLight ? 'text-slate-700' : 'text-slate-300'}`}>
                تحلیل کج‌فهمی‌ها و رفتار علمی دانش‌آموزان
              </span>
            </div>

            <h1 className={`text-2xl sm:text-3xl font-black flex items-center gap-3 ${
              isLight ? 'text-slate-900' : 'text-white'
            }`}>
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-amber-400 to-emerald-500 p-0.5 flex items-center justify-center text-slate-950 shadow-md">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <span>تحلیل کج‌فهمی‌های علمی (Misconception Analytics)</span>
            </h1>

            <p className={`text-xs sm:text-sm max-w-2xl leading-relaxed ${
              isLight ? 'text-slate-600' : 'text-slate-300'
            }`}>
              رصد و عارضه‌یابی خطاهای پرتکرار آزمایشگاهی بر مبنای قوانین قطعی موتور شبیه‌سازی، شناسایی ریشه‌های مفهومی و ارائه سرنخ‌های جبرانی به تفکیک دانش‌آموزان.
            </p>
          </div>

          {/* کلیدهای خروجی و گزارش‌گیری */}
          <div className="flex flex-wrap items-center gap-2.5">
            <Button
              variant="outline"
              size="sm"
              onClick={() => teacherService.downloadClassReportCsv(selectedClassCode, selectedExperimentId)}
              rightIcon={<FileSpreadsheet className="w-4 h-4 text-emerald-600" />}
              className={`font-bold rounded-xl ${
                isLight ? 'border-slate-300 text-slate-700 hover:bg-slate-100' : 'border-slate-700 text-slate-200'
              }`}
            >
              دانلود CSV کلاس
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrint}
              rightIcon={<Printer className="w-4 h-4 text-sky-600" />}
              className={`font-bold rounded-xl ${
                isLight ? 'border-slate-300 text-slate-700 hover:bg-slate-100' : 'border-slate-700 text-slate-200'
              }`}
            >
              چاپ گزارش
            </Button>
            <Button
              variant="cyan"
              size="sm"
              onClick={loadAnalytics}
              rightIcon={<RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />}
              className="font-bold rounded-xl"
            >
              بروزرسانی داده‌ها
            </Button>
          </div>
        </div>
      </div>

      {/* ۲. نوار فیلترهای پیشرفته */}
      <div className={`p-4 rounded-2xl border flex flex-wrap items-center justify-between gap-4 ${
        isLight ? 'bg-white border-slate-200 shadow-xs' : 'bg-slate-900/80 border-slate-800'
      }`}>
        <div className="flex flex-wrap items-center gap-3 flex-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-500">
            <Filter className="w-4 h-4 text-sky-500" />
            <span>فیلترها:</span>
          </div>

          {/* فیلتر آزمایش */}
          <select
            value={selectedExperimentId || ''}
            onChange={(e) => setSelectedExperimentId(e.target.value ? Number(e.target.value) : undefined)}
            className={`text-xs rounded-xl px-3 py-2 border outline-none font-medium ${
              isLight
                ? 'bg-slate-50 border-slate-200 text-slate-800 focus:border-sky-500'
                : 'bg-slate-800 border-slate-700 text-slate-200 focus:border-cyan-400'
            }`}
          >
            <option value="">همه آزمایش‌ها (کل کتاب‌ها)</option>
            {experiments.map((exp) => (
              <option key={exp.id} value={exp.id}>
                {exp.title} (پایه {exp.grade})
              </option>
            ))}
          </select>

          {/* فیلتر کد کلاس */}
          <input
            type="text"
            value={selectedClassCode}
            onChange={(e) => setSelectedClassCode(e.target.value)}
            placeholder="کد اختصاصی کلاس (مثلاً CLASS-8A)"
            className={`text-xs rounded-xl px-3 py-2 border outline-none font-medium ${
              isLight
                ? 'bg-slate-50 border-slate-200 text-slate-800 focus:border-sky-500'
                : 'bg-slate-800 border-slate-700 text-slate-200 focus:border-cyan-400'
            }`}
          />

          {(selectedExperimentId || selectedClassCode) && (
            <button
              onClick={() => {
                setSelectedExperimentId(undefined)
                setSelectedClassCode('')
              }}
              className="text-xs text-rose-500 hover:text-rose-600 font-bold flex items-center gap-1"
            >
              <X className="w-3.5 h-3.5" />
              <span>پاک‌سازی فیلتر</span>
            </button>
          )}
        </div>

        {/* فیلتر جستجوی نام دانش‌آموز */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-400 absolute right-3 top-2.5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="جستجوی نام دانش‌آموز..."
            className={`w-full text-xs rounded-xl pr-9 pl-3 py-2 border outline-none ${
              isLight
                ? 'bg-slate-50 border-slate-200 text-slate-800 focus:border-sky-500'
                : 'bg-slate-800 border-slate-700 text-slate-200 focus:border-cyan-400'
            }`}
          />
        </div>
      </div>

      {/* ۳. بخش کارت‌های خلاصه شاخص‌های کلیدی (Overview Cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* ۱: کل تلاش‌ها */}
        <div className={`p-5 rounded-2xl border transition-all ${
          isLight ? 'bg-white border-slate-200 shadow-xs' : 'bg-slate-900/90 border-slate-800'
        }`}>
          <div className="flex items-center justify-between mb-3">
            <span className={`text-xs font-bold ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              کل تلاش‌های انجام‌شده
            </span>
            <div className={`w-8 h-8 rounded-xl flex items-center justify-center ${
              isLight ? 'bg-sky-50 text-sky-600' : 'bg-sky-950/60 text-cyan-400 border border-cyan-500/30'
            }`}>
              <BookOpen className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-black font-mono ${isLight ? 'text-slate-900' : 'text-white'}`}>
              {overview?.totalAttempts ?? 0}
            </span>
            <span className="text-[11px] text-slate-400">نوبت آزمایش</span>
          </div>
          <span className="text-[11px] text-emerald-600 font-medium mt-1 block">
            {overview?.completedAttempts ?? 0} مورد تکمیل موفق
          </span>
        </div>

        {/* ۲: درصد موفقیت کلی */}
        <div className={`p-5 rounded-2xl border transition-all ${
          isLight ? 'bg-white border-slate-200 shadow-xs' : 'bg-slate-900/90 border-slate-800'
        }`}>
          <div className="flex items-center justify-between mb-3">
            <span className={`text-xs font-bold ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              درصد موفقیت کلی کلاس
            </span>
            <div className={`w-8 h-8 rounded-xl flex items-center justify-center ${
              isLight ? 'bg-emerald-50 text-emerald-600' : 'bg-emerald-950/60 text-emerald-400 border border-emerald-500/30'
            }`}>
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-black font-mono ${isLight ? 'text-slate-900' : 'text-white'}`}>
              {overview?.overallSuccessRate ?? 0}٪
            </span>
            <span className="text-[11px] text-slate-400">بدون بن‌بست</span>
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            میانگین نمره: <strong className="text-amber-500 font-mono">{overview?.averageScore ?? 0}</strong> از ۱۰۰
          </span>
        </div>

        {/* ۳: دانش‌آموزان فعال */}
        <div className={`p-5 rounded-2xl border transition-all ${
          isLight ? 'bg-white border-slate-200 shadow-xs' : 'bg-slate-900/90 border-slate-800'
        }`}>
          <div className="flex items-center justify-between mb-3">
            <span className={`text-xs font-bold ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              دانش‌آموزان فعال
            </span>
            <div className={`w-8 h-8 rounded-xl flex items-center justify-center ${
              isLight ? 'bg-indigo-50 text-indigo-600' : 'bg-indigo-950/60 text-indigo-400 border border-indigo-500/30'
            }`}>
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-black font-mono ${isLight ? 'text-slate-900' : 'text-white'}`}>
              {overview?.activeStudentsCount ?? 0}
            </span>
            <span className="text-[11px] text-slate-400">نفر</span>
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            ثبت‌شده در این دوره آماری
          </span>
        </div>

        {/* ۴: خطاهای رصدشده */}
        <div className={`p-5 rounded-2xl border transition-all ${
          isLight ? 'bg-white border-slate-200 shadow-xs' : 'bg-slate-900/90 border-slate-800'
        }`}>
          <div className="flex items-center justify-between mb-3">
            <span className={`text-xs font-bold ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              کج‌فهمی‌های شناسایی‌شده
            </span>
            <div className={`w-8 h-8 rounded-xl flex items-center justify-center ${
              isLight ? 'bg-amber-50 text-amber-600' : 'bg-amber-950/60 text-amber-400 border border-amber-500/30'
            }`}>
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-black font-mono text-amber-500`}>
              {overview?.totalErrorsRecorded ?? 0}
            </span>
            <span className="text-[11px] text-slate-400">رویداد خطا</span>
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            {overview?.totalHintsUsed ?? 0} بار مصرف راهنما
          </span>
        </div>
      </div>

      {/* ۴. نمودار و تحلیل کج‌فهمی‌های شایع (Misconceptions Frequency Bar Chart) */}
      <div className={`p-6 sm:p-8 rounded-3xl border transition-all ${
        isLight ? 'bg-white border-slate-200 shadow-sm' : 'bg-slate-900/90 border-indigo-500/25 shadow-xl'
      }`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
          <div>
            <h2 className={`text-lg sm:text-xl font-black flex items-center gap-2 ${
              isLight ? 'text-slate-900' : 'text-white'
            }`}>
              <Sparkles className="w-5 h-5 text-amber-500" />
              <span>فراوانی و کالبدشکافی کج‌فهمی‌های علمی دانش‌آموزان</span>
            </h2>
            <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              بر اساس کدهای خطای موتور قطعی؛ درصد تکرار و سرنخ اصلاحی پیشنهادی به دبیر
            </p>
          </div>

          <Badge variant="amber" size="sm" className="font-mono font-bold">
            {misconceptions.length} الگوی خطای شناسایی‌شده
          </Badge>
        </div>

        {misconceptions.length === 0 ? (
          <div className="text-center py-12 text-xs text-slate-400">
            هیچ خطای علمی یا کج‌فهمی در این بازه فیلتر ثبت نشده است. عملکرد دانش‌آموزان عالی بوده است! 🎉
          </div>
        ) : (
          <div className="space-y-6">
            {/* Visual Bar Chart */}
            <div className="space-y-4">
              {misconceptions.map((item, idx) => {
                const maxOccurrence = Math.max(...misconceptions.map((m) => m.occurrenceCount), 1)
                const barPercent = Math.round((item.occurrenceCount / maxOccurrence) * 100)

                return (
                  <div
                    key={item.errorCode}
                    className={`p-4 rounded-2xl border transition-all ${
                      isLight
                        ? 'bg-slate-50/80 border-slate-200 hover:border-amber-300 hover:bg-amber-50/20'
                        : 'bg-slate-950/60 border-slate-800 hover:border-amber-500/40'
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs mb-2">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-amber-400/20 text-amber-500 font-mono font-black flex items-center justify-center text-[10px]">
                          {idx + 1}
                        </span>
                        <strong className={`text-sm ${isLight ? 'text-slate-900' : 'text-white'}`}>
                          {item.errorTitle}
                        </strong>
                        <span className="font-mono text-[10px] text-slate-400 bg-slate-200/50 dark:bg-slate-800 px-2 py-0.5 rounded-md">
                          {item.errorCode}
                        </span>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="text-[11px] text-slate-400">
                          {item.affectedStudentsCount} دانش‌آموز تحت تاثیر
                        </span>
                        <span className="font-mono font-black text-amber-500 text-sm">
                          {item.occurrenceCount} بار ({item.percentage}٪)
                        </span>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full h-2.5 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden mb-3">
                      <div
                        className="h-full bg-gradient-to-r from-amber-500 via-orange-400 to-rose-400 rounded-full transition-all duration-700"
                        style={{ width: `${barPercent}%` }}
                      />
                    </div>

                    {/* Scientific Concept & Remediation */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 border-t border-slate-200/60 dark:border-slate-800/80 text-[11px]">
                      <div className="flex items-start gap-1.5">
                        <span className="font-bold text-sky-600 dark:text-cyan-400 shrink-0">ریشه علمی:</span>
                        <span className={isLight ? 'text-slate-700' : 'text-slate-300'}>{item.scientificConcept}</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <span className="font-bold text-emerald-600 dark:text-emerald-400 shrink-0">راهکار پداگوژیک معلم:</span>
                        <span className={isLight ? 'text-slate-700' : 'text-slate-300'}>{item.recommendedRemediation}</span>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>

      {/* ۵. جدول عملکرد دانش‌آموزان و ممیزی لاگ‌ها */}
      <div className={`p-6 sm:p-8 rounded-3xl border transition-all ${
        isLight ? 'bg-white border-slate-200 shadow-sm' : 'bg-slate-900/90 border-indigo-500/25 shadow-xl'
      }`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
          <div>
            <h2 className={`text-lg sm:text-xl font-black flex items-center gap-2 ${
              isLight ? 'text-slate-900' : 'text-white'
            }`}>
              <GraduationCap className="w-5 h-5 text-sky-500" />
              <span>جدول ارزیابی و ممیزی عملکرد تک‌تک دانش‌آموزان</span>
            </h2>
            <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              برای مشاهده ممیزی لاگ‌های گام‌به‌گام و سرنخ‌های دریافتی، روی دکمه لاگ اقدامات هر دانش‌آموز کلیک کنید
            </p>
          </div>

          <span className="text-xs font-bold text-slate-500">
            نمایش {filteredStudents.length} از {students.length} دانش‌آموز
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-right text-xs">
            <thead>
              <tr className={`border-b text-[11px] font-bold ${
                isLight ? 'border-slate-200 text-slate-500' : 'border-slate-800 text-slate-400'
              }`}>
                <th className="py-3 px-3">نام و مشخصات دانش‌آموز</th>
                <th className="py-3 px-3">پایه / کد کلاس</th>
                <th className="py-3 px-3 text-center">تعداد تلاش‌ها</th>
                <th className="py-3 px-3 text-center">درصد موفقیت</th>
                <th className="py-3 px-3 text-center">میانگین نمره</th>
                <th className="py-3 px-3 text-center">خطاها / راهنماها</th>
                <th className="py-3 px-3">آخرین فعالیت</th>
                <th className="py-3 px-3 text-left">عملیات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {filteredStudents.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-slate-400 text-xs">
                    دانش‌آموزی با این مشخصات یافت نشد.
                  </td>
                </tr>
              ) : (
                filteredStudents.map((st) => (
                  <tr
                    key={st.studentId}
                    className={`hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors ${
                      isLight ? 'text-slate-800' : 'text-slate-200'
                    }`}
                  >
                    <td className="py-3.5 px-3">
                      <div>
                        <strong className="block font-bold">{st.fullName}</strong>
                        <span className="text-[10px] text-slate-400">{st.email}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-3">
                      <div className="space-y-0.5">
                        <Badge variant="indigo" size="sm">پایه {st.grade || 'هشتم'}</Badge>
                        {st.classCode && (
                          <span className="block font-mono text-[10px] text-slate-400">
                            {st.classCode}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-3 text-center font-mono font-bold">
                      {st.totalAttempts}
                    </td>
                    <td className="py-3.5 px-3 text-center">
                      <span className={`inline-block px-2 py-0.5 rounded-full font-mono font-bold text-[11px] ${
                        st.successRate >= 80
                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                          : st.successRate >= 50
                          ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'
                          : 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300'
                      }`}>
                        {st.successRate}٪
                      </span>
                    </td>
                    <td className="py-3.5 px-3 text-center font-mono font-black text-sm">
                      {st.averageScore}
                    </td>
                    <td className="py-3.5 px-3 text-center text-[11px]">
                      <span className="text-rose-500 font-mono font-bold">{st.errorsCount} خطا</span>
                      <span className="text-slate-400 mx-1">/</span>
                      <span className="text-sky-500 font-mono font-bold">{st.hintsCount} راهنما</span>
                    </td>
                    <td className="py-3.5 px-3 text-[11px] text-slate-400">
                      {st.lastActivity ? new Date(st.lastActivity).toLocaleDateString('fa-IR') : '—'}
                    </td>
                    <td className="py-3.5 px-3 text-left">
                      <div className="flex items-center justify-end gap-1.5">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleOpenStudentLogs(st)}
                          className="text-[11px] font-bold rounded-lg"
                        >
                          لاگ اقدامات 🔍
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => teacherService.downloadStudentReportCsv(st.studentId)}
                          title="دانلود CSV دانش‌آموز"
                          className="p-1.5 rounded-lg text-emerald-600 hover:bg-emerald-50"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ۶. مودال / دراور جزئیات ممیزی لاگ‌های اقدامات دانش‌آموز */}
      <Modal
        isOpen={Boolean(selectedStudent)}
        onClose={() => setSelectedStudent(null)}
        title={`ممیزی لاگ اقدامات و کج‌فهمی‌های دانش‌آموز: ${selectedStudent?.fullName || ''}`}
        description="ردیابی زمانی تمام اقدامات روی میز کار، پیش‌نیازهای نقض‌شده و راهنماهای دریافت‌شده"
        maxWidth="xl"
      >
        <div className="space-y-4 pt-2 text-right">
          {loadingLogs ? (
            <div className="text-center py-10 text-xs text-slate-400 flex flex-col items-center gap-2">
              <RefreshCw className="w-5 h-5 animate-spin text-sky-500" />
              <span>در حال استعلام لاگ‌های قطعی موتور شبیه‌سازی...</span>
            </div>
          ) : studentLogs.length === 0 ? (
            <div className="text-center py-10 text-xs text-slate-400">
              هیچ لاگ اقدامی برای این دانش‌آموز ثبت نشده است.
            </div>
          ) : (
            <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-1">
              {studentLogs.map((log) => (
                <div
                  key={log.id}
                  className={`p-3.5 rounded-2xl border transition-all text-xs space-y-2 ${
                    log.isValid
                      ? isLight
                        ? 'bg-emerald-50/50 border-emerald-200'
                        : 'bg-emerald-950/20 border-emerald-500/30'
                      : isLight
                      ? 'bg-rose-50/50 border-rose-200'
                      : 'bg-rose-950/20 border-rose-500/30'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant={log.isValid ? 'emerald' : 'rose'} size="sm" className="font-bold">
                        {log.isValid ? 'اقدام معتبر ✓' : 'خطای پداگوژیک ✕'}
                      </Badge>
                      <strong className={isLight ? 'text-slate-900' : 'text-white'}>
                        گام {log.stepIndex}: {log.actionType}
                      </strong>
                    </div>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {new Date(log.createdAt).toLocaleTimeString('fa-IR')}
                    </span>
                  </div>

                  {/* ابزارها و پارامترها */}
                  {log.itemIds && log.itemIds.length > 0 && (
                    <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
                      <span>ابزارهای روی میز:</span>
                      <div className="flex flex-wrap gap-1">
                        {log.itemIds.map((tid, idx) => (
                          <span key={idx} className="bg-slate-200/60 dark:bg-slate-800 px-1.5 py-0.5 rounded text-[10px] font-mono">
                            {tid}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* پیام فیدبک یا خطای کج‌فهمی */}
                  <div className={`p-2.5 rounded-xl border text-[11px] leading-relaxed ${
                    log.isValid
                      ? isLight ? 'bg-white border-emerald-100 text-emerald-950' : 'bg-slate-900 border-emerald-500/20 text-emerald-200'
                      : isLight ? 'bg-white border-rose-100 text-rose-950' : 'bg-slate-900 border-rose-500/20 text-rose-200'
                  }`}>
                    {log.errorCode && (
                      <span className="block font-bold mb-1 text-rose-600 dark:text-rose-400">
                        کد خطا: {log.errorCode} {log.errorTitle ? `(${log.errorTitle})` : ''}
                      </span>
                    )}
                    <p>{log.feedbackText}</p>
                    {log.observationText && (
                      <span className="block mt-1 font-medium text-slate-500">
                        مشاهده حاصله: {log.observationText}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center justify-between pt-3 border-t border-slate-200 dark:border-slate-800">
            <span className="text-[11px] text-slate-400">
              مجموع لاگ‌ها: {studentLogs.length} رویداد
            </span>
            <Button variant="outline" size="sm" onClick={() => setSelectedStudent(null)}>
              بستن
            </Button>
          </div>
        </div>
      </Modal>

    </div>
  )
}
