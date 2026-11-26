import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { attemptService } from '../services/attemptService'
import type { ExperimentAttempt } from '../types/attempt'
import { Card, CardHeader, CardContent, Button, Badge, Skeleton } from '../components/ui'
import {
  CheckCircle2,
  AlertCircle,
  Sparkles,
  ArrowRight,
  Clock,
  Calendar,
  ListChecks,
  RotateCcw
} from 'lucide-react'

export const AttemptHistoryPage: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>()
  const [selectedAttempt, setSelectedAttempt] = useState<ExperimentAttempt | null>(null)
  const [allAttempts, setAllAttempts] = useState<ExperimentAttempt[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (attemptId) {
      attemptService.getAttemptById(attemptId).then((att) => {
        setSelectedAttempt(att)
        setLoading(false)
      })
    } else {
      attemptService.getAttemptsByUser('usr-student-01').then((atts) => {
        setAllAttempts(atts)
        setLoading(false)
      })
    }
  }, [attemptId])

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 space-y-4">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  // View: Detailed Single Attempt Report
  if (selectedAttempt) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
        
        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link to="/dashboard" className="text-xs text-slate-400 hover:text-cyan-400 flex items-center gap-1">
            <ArrowRight className="w-3.5 h-3.5" />
            بازگشت به داشبورد دانش‌آموز
          </Link>
          <span className="text-xs font-mono text-slate-500">کد پیگیری تلاش: {selectedAttempt.id}</span>
        </div>

        {/* Report Header Card */}
        <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 sm:p-8 space-y-4 shadow-xl">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="space-y-1">
              <span className="text-xs text-cyan-400 font-bold">کارنامه تحلیلی و گزارش آزمایشگاه</span>
              <h1 className="text-xl sm:text-2xl font-black text-white">{selectedAttempt.experimentTitle}</h1>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-cyan-950/80 border border-cyan-500/40 text-center font-mono">
                <span className="text-[10px] text-cyan-300 block">نمره علمی</span>
                <span className="text-2xl font-black text-cyan-400">{selectedAttempt.score}</span>
                <span className="text-[10px] text-slate-400">/۱۰۰</span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center gap-4 text-xs text-slate-400">
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              تاریخ: {new Date(selectedAttempt.startedAt).toLocaleDateString('fa-IR')}
            </span>
            <span>•</span>
            <span className="flex items-center gap-1 font-mono">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              زمان ثبت: {new Date(selectedAttempt.startedAt).toLocaleTimeString('fa-IR')}
            </span>
            <span>•</span>
            <Badge variant="emerald" size="sm">
              وضعیت: {selectedAttempt.status === 'COMPLETED' ? 'تکمیل موفق' : 'ناتمام'}
            </Badge>
          </div>
        </div>

        {/* Step-by-Step Action Logs (Audit Trail) */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <ListChecks className="w-4 h-4 text-cyan-400" />
              <span>ردیابی گام‌به‌گام اقدامات و اعتبارسنجی علمی</span>
            </div>
            <span className="text-xs text-slate-400">
              {selectedAttempt.actionsLog.length} کنش ثبت‌شده
            </span>
          </CardHeader>
          <CardContent className="space-y-3">
            {selectedAttempt.actionsLog.map((log, index) => (
              <div
                key={index}
                className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 flex items-start gap-3"
              >
                <div className="shrink-0 mt-0.5">
                  {log.isValid ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-rose-400" />
                  )}
                </div>
                <div className="flex-1 space-y-1 text-right">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-white">مرحله {log.stepIndex}</span>
                    <span className="font-mono text-[10px] text-slate-500">
                      {new Date(log.timestamp).toLocaleTimeString('fa-IR')}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">{log.feedbackText}</p>
                  {log.observationText && (
                    <p className="text-[11px] text-cyan-300 bg-cyan-950/40 border border-cyan-800/40 p-2 rounded-lg mt-1 font-mono">
                      {log.observationText}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Hints Used in this attempt */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>راهنمایی‌های هوشمند دریافت شده در حین آزمایش</span>
            </div>
            <Badge variant="amber" size="sm">{selectedAttempt.hintsUsed.length} راهنمایی</Badge>
          </CardHeader>
          <CardContent className="space-y-3">
            {selectedAttempt.hintsUsed.length === 0 ? (
              <p className="text-xs text-slate-400">
                در این آزمایش بدون استفاده از راهنما به پاسخ رسیده‌اید.
              </p>
            ) : (
              selectedAttempt.hintsUsed.map((hint, i) => (
                <div
                  key={i}
                  className="p-3.5 rounded-xl border border-slate-800 bg-slate-950/60 flex items-start gap-3 text-xs"
                >
                  <Badge variant="indigo" size="sm" className="shrink-0 mt-0.5">
                    سطح {hint.level}
                  </Badge>
                  <div className="space-y-1 flex-1 text-right">
                    <span className="text-[11px] text-slate-400">مربوط به مرحله {hint.stepIndex}</span>
                    <p className="text-slate-200 leading-relaxed">{hint.content}</p>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Re-try CTA */}
        <div className="flex items-center justify-end gap-3">
          <Link to={`/experiments/${selectedAttempt.experimentSlug}/lab`}>
            <Button variant="cyan" size="md" rightIcon={<RotateCcw className="w-4 h-4" />}>
              انجام دوباره این آزمایش
            </Button>
          </Link>
        </div>

      </div>
    )
  }

  // View: General History List
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-black text-white">تاریخچه کامل آزمایش‌ها</h1>
        <p className="text-xs text-slate-400">فهرست تمامی جلسات و تلاش‌های ثبت‌شده در سامانه</p>
      </div>

      <div className="space-y-3">
        {allAttempts.map((att) => (
          <div
            key={att.id}
            className="p-5 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-slate-700 transition-colors"
          >
            <div className="space-y-1">
              <h3 className="text-base font-bold text-white">{att.experimentTitle}</h3>
              <div className="flex items-center gap-3 text-xs text-slate-400">
                <span>پایه {att.grade}</span>
                <span>•</span>
                <span>{att.subject}</span>
                <span>•</span>
                <span>نمره: {att.score}٪</span>
              </div>
            </div>

            <Link to={`/history/${att.id}`}>
              <Button variant="outline" size="sm">
                مشاهده کارنامه
              </Button>
            </Link>
          </div>
        ))}
      </div>
    </div>
  )
}
