import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { experimentService } from '../services/experimentService'
import type { Experiment, GradeLevel, SubjectType } from '../types/experiment'
import { ExperimentCard } from '../components/catalog/ExperimentCard'
import { Input, Select, Button, Skeleton, EmptyState, Badge } from '../components/ui'
import { BookOpen, Search, RotateCcw, KeyRound, ArrowLeft, AlertCircle } from 'lucide-react'

export const CatalogPage: React.FC = () => {
  const navigate = useNavigate()
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedGrade, setSelectedGrade] = useState<GradeLevel | 'all'>('all')
  const [selectedSubject, setSelectedSubject] = useState<SubjectType | 'all'>('all')

  // ورود به آزمایش کلاسی با کد دبیر
  const [classCodeInput, setClassCodeInput] = useState('')
  const [joinLoading, setJoinLoading] = useState(false)
  const [joinError, setJoinError] = useState<string | null>(null)

  const fetchExperiments = () => {
    setLoading(true)
    experimentService
      .getAllExperiments({
        search: searchTerm,
        grade: selectedGrade,
        subject: selectedSubject
      })
      .then((data) => {
        setExperiments(data)
        setLoading(false)
      })
  }

  useEffect(() => {
    fetchExperiments()
  }, [searchTerm, selectedGrade, selectedSubject])

  const handleResetFilters = () => {
    setSearchTerm('')
    setSelectedGrade('all')
    setSelectedSubject('all')
  }

  const handleJoinClass = async (e: React.FormEvent) => {
    e.preventDefault()
    const code = classCodeInput.trim().toUpperCase()
    if (!code) return

    setJoinLoading(true)
    setJoinError(null)

    try {
      const exp = await experimentService.joinClassExperiment(code)
      navigate(`/experiments/${exp.slug}/lab?class_code=${encodeURIComponent(code)}`)
    } catch (err: any) {
      setJoinError(
        err?.detail || err?.message || 'آزمایش یا کلاسی با این کد یافت نشد. لطفاً کد را با دبیر خود مجدداً بررسی کنید.'
      )
    } finally {
      setJoinLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full space-y-8">
      
      {/* Header Banner */}
      <div className="border-b border-slate-800 pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <BookOpen className="w-5 h-5 text-cyan-400" />
            <h1 className="text-2xl sm:text-3xl font-black text-white">
              کاتالوگ جامع آزمایش‌های علوم تجربی
            </h1>
          </div>
          <p className="text-xs text-slate-400">
            فهرست آزمایش‌های شبیه‌سازی‌شده منطبق بر سرفصل کتب درسی دوره اول و دوم متوسطه
          </p>
        </div>

        <div className="text-xs text-slate-400 font-mono">
          نمایش {experiments.length} آزمایش معتبر
        </div>
      </div>

      {/* Join Class Experiment by Code Banner */}
      <div className="rounded-2xl border border-indigo-900/60 bg-gradient-to-r from-indigo-950/50 via-slate-900/80 to-blue-950/50 p-5 shadow-xl relative overflow-hidden space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0 shadow-inner">
              <KeyRound className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm sm:text-base font-bold text-white">
                  ورود به آزمایش کلاسی با کد اختصاصی دبیر
                </h2>
                <Badge variant="indigo" size="sm">ویژه تکالیف کلاسی</Badge>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                اگر دبیر محترم شما برای تکلیف آزمایشگاهی کد کلاسی اعلام کرده است، آن را وارد کنید:
              </p>
            </div>
          </div>

          <form onSubmit={handleJoinClass} className="flex items-center gap-2 w-full md:w-auto">
            <div className="w-full md:w-56">
              <Input
                placeholder="کد کلاس دبیر..."
                value={classCodeInput}
                onChange={(e) => {
                  setClassCodeInput(e.target.value.toUpperCase())
                  setJoinError(null)
                }}
                className="font-mono text-center tracking-widest uppercase font-bold"
                required
              />
            </div>
            <Button
              type="submit"
              variant="primary"
              size="md"
              isLoading={joinLoading}
              className="shrink-0"
              rightIcon={<ArrowLeft className="w-4 h-4" />}
            >
              شروع آزمایش کلاسی
            </Button>
          </form>
        </div>

        {joinError && (
          <div className="text-rose-400 text-xs flex items-center gap-2 pt-1 font-medium animate-in fade-in">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{joinError}</span>
          </div>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
        
        {/* Search Input */}
        <div className="lg:col-span-2">
          <Input
            label="جستجوی آزمایش"
            placeholder="جستجو بر اساس عنوان، ابزار، فصل یا مبحث درسی..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            rightIcon={<Search className="w-4 h-4" />}
          />
        </div>

        {/* Grade Filter */}
        <div>
          <Select
            label="پایه تحصیلی"
            value={selectedGrade}
            onChange={(e) => setSelectedGrade(e.target.value as GradeLevel | 'all')}
            options={[
              { value: 'all', label: 'تمامی پایه‌ها' },
              { value: 'هفتم', label: 'پایه هفتم' },
              { value: 'هشتم', label: 'پایه هشتم' },
              { value: 'نهم', label: 'پایه نهم' },
              { value: 'دهم', label: 'پایه دهم' }
            ]}
          />
        </div>

        {/* Subject Filter */}
        <div className="flex gap-2">
          <div className="flex-1">
            <Select
              label="درس / حوزه علمی"
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value as SubjectType | 'all')}
              options={[
                { value: 'all', label: 'تمامی دروس' },
                { value: 'شیمی', label: 'شیمی تجربی' },
                { value: 'فیزیک', label: 'فیزیک تجربی' },
                { value: 'زیست‌شناسی', label: 'زیست‌شناسی' },
                { value: 'شیمی و فیزیک', label: 'شیمی و فیزیک' }
              ]}
            />
          </div>
          {(searchTerm || selectedGrade !== 'all' || selectedSubject !== 'all') && (
            <Button
              variant="outline"
              size="md"
              className="mt-auto"
              onClick={handleResetFilters}
              title="بازنشانی فیلترها"
            >
              <RotateCcw className="w-4 h-4" />
            </Button>
          )}
        </div>

      </div>

      {/* Experiments Grid or Loading / Empty */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((n) => (
            <div key={n} className="rounded-2xl border border-slate-800 bg-slate-900/40 p-5 space-y-4">
              <Skeleton className="h-44 w-full" />
              <Skeleton className="h-5 w-3/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
              <div className="flex gap-2 pt-2">
                <Skeleton className="h-9 flex-1" />
                <Skeleton className="h-9 flex-1" />
              </div>
            </div>
          ))}
        </div>
      ) : experiments.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {experiments.map((exp) => (
            <ExperimentCard key={exp.id} experiment={exp} />
          ))}
        </div>
      ) : (
        <EmptyState
          title="آزمایشی مطابق با فیلترهای انتخابی شما یافت نشد"
          description="می‌توانید عبارت جستجو را تغییر دهید یا فیلترهای پایه و درس را بازنشانی کنید."
          action={
            <Button variant="cyan" size="sm" onClick={handleResetFilters}>
              نمایش همه آزمایش‌ها
            </Button>
          }
        />
      )}

    </div>
  )
}
