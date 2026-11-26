import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { experimentService } from '../services/experimentService'
import type { Experiment, GradeLevel, SubjectType, ContentStatus, DifficultyLevel } from '../types/experiment'
import {
  Card,
  CardHeader,
  CardContent,
  Button,
  Badge,
  Modal,
  Input,
  Select,
  StatusAlert,
  Skeleton
} from '../components/ui'
import {
  FlaskConical,
  Plus,
  ArrowRight,
  BookOpen,
  Search,
  Play,
  KeyRound,
  Copy,
  Check
} from 'lucide-react'

export const TeacherManagementPage: React.FC = () => {
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [filterSubject, setFilterSubject] = useState<SubjectType | 'all'>('all')
  const [filterGrade, setFilterGrade] = useState<GradeLevel | 'all'>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  // New Experiment Form
  const [newTitle, setNewTitle] = useState('')
  const [newGrade, setNewGrade] = useState<GradeLevel>('هشتم')
  const [newSubject, setNewSubject] = useState<SubjectType>('شیمی')
  const [newDifficulty, setNewDifficulty] = useState<DifficultyLevel>('متوسط')
  const [newDuration, setNewDuration] = useState('15')
  const [newBook, setNewBook] = useState('علوم تجربی پایه هشتم')
  const [newChapter, setNewChapter] = useState('مخلوط و جداسازی مواد')
  const [newPage, setNewPage] = useState('16')
  const [newSummary, setNewSummary] = useState('')
  const [newObjective, setNewObjective] = useState('')
  const [newSafety, setNewSafety] = useState('')
  const [isClassOnly, setIsClassOnly] = useState(false)
  const [classCode, setClassCode] = useState(`CLS-${Math.floor(1000 + Math.random() * 9000)}`)
  const [copiedCode, setCopiedCode] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const loadExperiments = () => {
    setLoading(true)
    experimentService
      .getAllExperiments({
        grade: filterGrade,
        subject: filterSubject,
        status: filterStatus === 'all' ? undefined : filterStatus
      })
      .then((data) => {
        setExperiments(data)
        setLoading(false)
      })
      .catch(() => {
        setLoading(false)
      })
  }

  useEffect(() => {
    loadExperiments()
  }, [filterGrade, filterSubject, filterStatus])

  const handleCreateDraft = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTitle.trim()) {
      setErrorMsg('عنوان آزمایش الزامی است.')
      return
    }

    setSubmitting(true)
    setErrorMsg(null)

    // تولید نامک معتبر بر اساس زمان و عنوان
    const generatedSlug = `exp-${Date.now().toString().slice(-6)}-${encodeURIComponent(
      newTitle.trim().slice(0, 15).replace(/\s+/g, '-')
    )}`

    try {
      const created = await experimentService.saveExperimentDraft({
        slug: generatedSlug,
        title: newTitle.trim(),
        grade: newGrade,
        subject: newSubject,
        difficulty: newDifficulty,
        durationMinutes: parseInt(newDuration) || 15,
        status: 'DRAFT',
        summary: newSummary || 'توضیحات پیش‌نویس آزمایش طراحی‌شده توسط دبیر محترم',
        objectives: newObjective ? [newObjective] : ['آشنایی با اصول علمی آزمایشگاهی'],
        safetyNotes: newSafety ? [newSafety] : ['رعایت نکات عمومی ایمنی در آزمایشگاه'],
        textbook: {
          book: newBook,
          grade: newGrade,
          chapter: newChapter,
          chapterNumber: 2,
          page: parseInt(newPage) || 1
        },
        availableTools: [],
        steps: [],
        classCode: classCode.trim().toUpperCase() || undefined,
        isClassOnly: isClassOnly
      })

      setModalOpen(false)
      setSuccessMsg(`آزمایش «${created.title}» با وضعیت پیش‌نویس در پایگاه داده ایجاد شد.`)
      setNewTitle('')
      setNewSummary('')
      setNewObjective('')
      setNewSafety('')
      loadExperiments()
    } catch (err: any) {
      setErrorMsg(err?.detail || err?.message || 'خطا در ثبت آزمایش در سرور.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleUpdateStatus = async (id: string, newStatus: ContentStatus) => {
    try {
      await experimentService.updateStatus(id, newStatus)
      const statusFa =
        newStatus === 'PUBLISHED'
          ? 'منتشرشده'
          : newStatus === 'VERIFIED'
          ? 'تأیید علمی'
          : 'پیش‌نویس'
      setSuccessMsg(`وضعیت آزمایش با موفقیت به «${statusFa}» تغییر یافت.`)
      loadExperiments()
    } catch (err: any) {
      setErrorMsg(err?.detail || err?.message || 'خطا در تغییر وضعیت انتشار آزمایش.')
    }
  }

  const filteredExperiments = experiments.filter((exp) => {
    if (!searchTerm) return true
    const q = searchTerm.toLowerCase()
    return (
      exp.title.toLowerCase().includes(q) ||
      exp.slug.toLowerCase().includes(q) ||
      exp.textbook.book.toLowerCase().includes(q)
    )
  })

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full space-y-8">
      {/* Header Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <Link
            to="/teacher/dashboard"
            className="text-xs text-slate-400 hover:text-cyan-400 flex items-center gap-1 mb-1 transition-colors"
          >
            <ArrowRight className="w-3.5 h-3.5" />
            بازگشت به داشبورد تحلیلی معلم
          </Link>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            <FlaskConical className="w-6 h-6 text-cyan-400" />
            مدیریت محتوا، تدوین و چرخه حیات آزمایش‌ها
          </h1>
        </div>

        <Button
          variant="cyan"
          size="md"
          onClick={() => {
            setErrorMsg(null)
            setModalOpen(true)
          }}
          rightIcon={<Plus className="w-4 h-4" />}
        >
          ایجاد پیش‌نویس آزمایش جدید
        </Button>
      </div>

      {successMsg && (
        <StatusAlert type="success" title="عملیات موفق">
          {successMsg}
        </StatusAlert>
      )}

      {errorMsg && (
        <StatusAlert type="error" title="خطا در عملیات">
          {errorMsg}
        </StatusAlert>
      )}

      {/* Filter Bar */}
      <div className="bg-slate-900/60 p-4 rounded-2xl border border-slate-800 flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2" />
          <Input
            placeholder="جست‌وجو در عنوان یا کتاب درسی..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pr-9"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <Select
            value={filterSubject}
            onChange={(e) => setFilterSubject(e.target.value as any)}
            options={[
              { value: 'all', label: 'همه رشته‌ها' },
              { value: 'شیمی', label: 'شیمی' },
              { value: 'فیزیک', label: 'فیزیک' },
              { value: 'زیست', label: 'زیست‌شناسی' }
            ]}
          />

          <Select
            value={filterGrade}
            onChange={(e) => setFilterGrade(e.target.value as any)}
            options={[
              { value: 'all', label: 'همه پایه‌ها' },
              { value: 'هفتم', label: 'پایه هفتم' },
              { value: 'هشتم', label: 'پایه هشتم' },
              { value: 'نهم', label: 'پایه نهم' },
              { value: 'دهم', label: 'پایه دهم' }
            ]}
          />

          <Select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            options={[
              { value: 'all', label: 'تمام وضعیت‌ها' },
              { value: 'PUBLISHED', label: 'منتشرشده' },
              { value: 'VERIFIED', label: 'تأیید علمی' },
              { value: 'DRAFT', label: 'پیش‌نویس' }
            ]}
          />
        </div>
      </div>

      {/* Experiments Management Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2 text-white font-bold text-sm">
            <span>فهرست آزمایش‌های ثبت‌شده در سامانه ({filteredExperiments.length})</span>
          </div>
          <span className="text-xs text-slate-400">کنترل دسترسی ویژه دبیران مجرب و مدیران آموزشی</span>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-6 space-y-4">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-right text-xs">
                <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="p-4 font-bold">عنوان آزمایش و نامک</th>
                    <th className="p-4 font-bold">پایه و رشته</th>
                    <th className="p-4 font-bold">منبع درسی رسمی</th>
                    <th className="p-4 font-bold">سختی و زمان</th>
                    <th className="p-4 font-bold">کد دسترسی کلاس</th>
                    <th className="p-4 font-bold">وضعیت انتشار</th>
                    <th className="p-4 font-bold">تغییر وضعیت</th>
                    <th className="p-4 font-bold">اقدامات</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/80 text-slate-200">
                  {filteredExperiments.map((exp) => (
                    <tr key={exp.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="p-4 font-bold text-white">
                        <div className="space-y-0.5">
                          <span>{exp.title}</span>
                          <span className="text-[10px] text-slate-500 block font-mono">
                            شناسه: {exp.slug}
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-1.5">
                          <Badge variant="cyan" size="sm">
                            پایه {exp.grade}
                          </Badge>
                          <Badge variant="indigo" size="sm">
                            {exp.subject}
                          </Badge>
                        </div>
                      </td>
                      <td className="p-4 text-slate-300">
                        <div className="flex items-center gap-1">
                          <BookOpen className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                          <span>
                            {exp.textbook.book} (فصل {exp.textbook.chapterNumber}، ص {exp.textbook.page})
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="space-y-1">
                          <span className="text-slate-300 block">{exp.difficulty}</span>
                          <span className="text-[10px] text-slate-500 font-mono block">
                            {exp.durationMinutes} دقیقه
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        {exp.classCode ? (
                          <div className="flex items-center gap-1.5">
                            <Badge variant={exp.isClassOnly ? 'rose' : 'indigo'} size="sm" className="font-mono">
                              {exp.isClassOnly ? '🔒 ' : ''}{exp.classCode}
                            </Badge>
                            <button
                              type="button"
                              onClick={() => {
                                navigator.clipboard.writeText(exp.classCode || '')
                                setCopiedCode(exp.classCode || null)
                                setTimeout(() => setCopiedCode(null), 2000)
                              }}
                              className="text-slate-400 hover:text-cyan-400 text-[10px] px-1.5 py-0.5 rounded bg-slate-950 border border-slate-800 transition-colors flex items-center gap-1"
                              title="کپی کد دسترسی برای ارسال به دانش‌آموزان"
                            >
                              {copiedCode === exp.classCode ? (
                                <>
                                  <Check className="w-3 h-3 text-emerald-400" />
                                  <span className="text-emerald-400">کپی شد</span>
                                </>
                              ) : (
                                <>
                                  <Copy className="w-3 h-3" />
                                  <span>کپی</span>
                                </>
                              )}
                            </button>
                          </div>
                        ) : (
                          <span className="text-slate-500 text-[11px]">عمومی (سراسری)</span>
                        )}
                      </td>
                      <td className="p-4">
                        <Badge
                          variant={
                            exp.status === 'PUBLISHED'
                              ? 'emerald'
                              : exp.status === 'VERIFIED'
                              ? 'cyan'
                              : 'amber'
                          }
                          size="sm"
                        >
                          {exp.status === 'PUBLISHED'
                            ? 'منتشرشده'
                            : exp.status === 'VERIFIED'
                            ? 'تأیید علمی'
                            : 'پیش‌نویس معلم'}
                        </Badge>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-1.5">
                          {exp.status !== 'PUBLISHED' && (
                            <Button
                              variant="cyan"
                              size="sm"
                              onClick={() => handleUpdateStatus(exp.id, 'PUBLISHED')}
                            >
                              انتشار در کاتالوگ
                            </Button>
                          )}
                          {exp.status === 'DRAFT' && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleUpdateStatus(exp.id, 'VERIFIED')}
                            >
                              تأیید علمی
                            </Button>
                          )}
                          {exp.status === 'PUBLISHED' && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleUpdateStatus(exp.id, 'DRAFT')}
                            >
                              لغو انتشار
                            </Button>
                          )}
                        </div>
                      </td>
                      <td className="p-4">
                        <Link to={`/experiments/${exp.slug}/lab`}>
                          <Button variant="ghost" size="sm" rightIcon={<Play className="w-3.5 h-3.5" />}>
                            تست در لابراتوار
                          </Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal: New Experiment Creation */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="تعریف و تدوین آزمایش جدید منطبق بر کتب درسی"
        description="اطلاعات متادیتا و مراجع رسمی درسی را وارد کنید؛ آزمایش در وضعیت پیش‌نویس ذخیره خواهد شد."
        maxWidth="lg"
      >
        <form onSubmit={handleCreateDraft} className="space-y-4 pt-2 text-xs">
          <Input
            label="عنوان کامل آزمایش درسی"
            placeholder="مثلاً: بررسی اثر تغییر دما بر انحلال‌پذیری نمک خوراکی"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            required
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Select
              label="پایه تحصیلی"
              value={newGrade}
              onChange={(e) => setNewGrade(e.target.value as GradeLevel)}
              options={[
                { value: 'هفتم', label: 'پایه هفتم' },
                { value: 'هشتم', label: 'پایه هشتم' },
                { value: 'نهم', label: 'پایه نهم' },
                { value: 'دهم', label: 'پایه دهم' }
              ]}
            />
            <Select
              label="حوزه درسی"
              value={newSubject}
              onChange={(e) => setNewSubject(e.target.value as SubjectType)}
              options={[
                { value: 'شیمی', label: 'شیمی' },
                { value: 'فیزیک', label: 'فیزیک' },
                { value: 'زیست', label: 'زیست‌شناسی' }
              ]}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Select
              label="درجه دشواری پداگوژیک"
              value={newDifficulty}
              onChange={(e) => setNewDifficulty(e.target.value as DifficultyLevel)}
              options={[
                { value: 'آسان', label: 'آسان' },
                { value: 'متوسط', label: 'متوسط' },
                { value: 'پیشرفته', label: 'پیشرفته' }
              ]}
            />
            <Input
              label="مدت زمان پیشنهادی (دقیقه)"
              type="number"
              value={newDuration}
              onChange={(e) => setNewDuration(e.target.value)}
            />
          </div>

          <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 space-y-3">
            <span className="font-bold text-white flex items-center gap-1.5 text-xs">
              <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
              مرجع کتاب درسی رسمی آموزش و پرورش
            </span>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <Input
                label="نام کتاب"
                value={newBook}
                onChange={(e) => setNewBook(e.target.value)}
              />
              <Input
                label="عنوان فصل"
                value={newChapter}
                onChange={(e) => setNewChapter(e.target.value)}
              />
              <Input
                label="شماره صفحه کتاب"
                type="number"
                value={newPage}
                onChange={(e) => setNewPage(e.target.value)}
              />
            </div>
          </div>

          <Input
            label="اهداف آموزشی کلیدی آزمایش"
            placeholder="مثلاً: درک تفاوت اثر دما بر انحلال‌پذیری جامدات..."
            value={newObjective}
            onChange={(e) => setNewObjective(e.target.value)}
          />

          <Input
            label="نکات و هشدارهای ایمنی آزمایشگاه"
            placeholder="مثلاً: هنگام کار با شعله چراغ بونزن از عینک محافظ استفاده شود..."
            value={newSafety}
            onChange={(e) => setNewSafety(e.target.value)}
          />

          <Input
            label="خلاصه دستور کار و توضیح علمی"
            placeholder="شرح موجز فرایند عملی آزمایش برای مطالعه دانش‌آموز..."
            value={newSummary}
            onChange={(e) => setNewSummary(e.target.value)}
          />

          {/* تنظیمات اتصال به کلاس و کد دسترسی اختصاصی */}
          <div className="p-3 bg-indigo-950/30 border border-indigo-900/50 rounded-xl space-y-3">
            <span className="font-bold text-white flex items-center gap-1.5 text-xs text-indigo-300">
              <KeyRound className="w-3.5 h-3.5 text-indigo-400" />
              سطح دسترسی کلاسی و کد اختصاصی ورود دانش‌آموزان
            </span>

            <div className="flex flex-col sm:flex-row sm:items-center gap-3 pt-1">
              <label className="flex items-center gap-2 cursor-pointer text-slate-200">
                <input
                  type="radio"
                  name="accessType"
                  checked={!isClassOnly}
                  onChange={() => setIsClassOnly(false)}
                  className="accent-indigo-500"
                />
                <span>آزمایش عمومی (نمایش در کاتالوگ سراسری)</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer text-slate-200">
                <input
                  type="radio"
                  name="accessType"
                  checked={isClassOnly}
                  onChange={() => setIsClassOnly(true)}
                  className="accent-indigo-500"
                />
                <span className="text-indigo-300 font-bold">🔒 اختصاصی کلاس من (صرفاً با کد اختصاصی)</span>
              </label>
            </div>

            <div className="flex items-end gap-2 pt-1">
              <div className="flex-1">
                <Input
                  label="کد اختصاصی کلاس / آزمون (Class Code)"
                  placeholder="مثلاً: CLASS-801 یا MORADI-EXP"
                  value={classCode}
                  onChange={(e) => setClassCode(e.target.value.toUpperCase())}
                  className="font-mono uppercase tracking-wider"
                  required
                />
              </div>
              <Button
                type="button"
                variant="outline"
                size="md"
                onClick={() => setClassCode(`CLS-${Math.floor(1000 + Math.random() * 9000)}`)}
                className="shrink-0"
              >
                تولید خودکار کد
              </Button>
            </div>
            <p className="text-[11px] text-slate-400">
              دانش‌آموزان شما با وارد کردن این کد در صفحه کاتالوگ، مستقیماً وارد این آزمایش شده و نتایج کارنامه آن‌ها به صورت اختصاصی در پنل پایش شما ثبت می‌گردد.
            </p>
          </div>

          <div className="pt-3 border-t border-slate-800 flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setModalOpen(false)}
              disabled={submitting}
            >
              انصراف
            </Button>
            <Button type="submit" variant="cyan" size="sm" disabled={submitting}>
              {submitting ? 'در حال ذخیره‌سازی...' : 'ذخیره پیش‌نویس در سرور'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
