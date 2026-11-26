import React, { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { experimentService } from '../services/experimentService'
import type { Experiment } from '../types/experiment'
import { Button, Badge, Card, CardHeader, CardContent, StatusAlert, Skeleton } from '../components/ui'
import {
  FlaskConical,
  BookOpen,
  Clock,
  ShieldCheck,
  AlertTriangle,
  ArrowLeft,
  ListOrdered,
  Beaker,
  CheckCircle2,
  ChevronRight
} from 'lucide-react'

export const ExperimentDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const [experiment, setExperiment] = useState<Experiment | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (slug) {
      experimentService.getExperimentBySlug(slug).then((exp) => {
        setExperiment(exp)
        setLoading(false)
      })
    }
  }, [slug])

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12 space-y-6">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-40 w-full" />
      </div>
    )
  }

  if (!experiment) {
    return (
      <div className="max-w-md mx-auto py-20 text-center space-y-4">
        <h2 className="text-xl font-bold text-white">آزمایش مورد نظر یافت نشد</h2>
        <p className="text-xs text-slate-400">شناسه آزمایش وارد شده در کاتالوگ موجود نمی‌باشد.</p>
        <Button variant="cyan" onClick={() => navigate('/experiments')}>
          بازگشت به کاتالوگ
        </Button>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      {/* Breadcrumb Navigation */}
      <nav className="flex items-center gap-2 text-xs text-slate-400">
        <Link to="/" className="hover:text-cyan-400 transition-colors">صفحه اصلی</Link>
        <ChevronRight className="w-3.5 h-3.5 rotate-180" />
        <Link to="/experiments" className="hover:text-cyan-400 transition-colors">کاتالوگ آزمایش‌ها</Link>
        <ChevronRight className="w-3.5 h-3.5 rotate-180" />
        <span className="text-slate-200 font-medium truncate">{experiment.title}</span>
      </nav>

      {/* Main Header Banner */}
      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 sm:p-10 space-y-6 relative overflow-hidden">
        <div className="absolute inset-0 lab-grid-dense opacity-30 pointer-events-none" />

        <div className="relative z-10 space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="cyan">پایه {experiment.grade}</Badge>
            <Badge variant="indigo">{experiment.subject}</Badge>
            <Badge variant={experiment.difficulty === 'آسان' ? 'emerald' : 'amber'}>
              سطح {experiment.difficulty}
            </Badge>
            <span className="flex items-center gap-1 text-xs text-slate-400 mr-auto font-mono">
              <Clock className="w-4 h-4 text-cyan-400" />
              مدت تخمینی: {experiment.durationMinutes} دقیقه
            </span>
          </div>

          <h1 className="text-2xl sm:text-4xl font-black text-white leading-tight">
            {experiment.title}
          </h1>

          <p className="text-slate-300 text-sm sm:text-base leading-relaxed max-w-3xl">
            {experiment.summary}
          </p>

          {/* Textbook Reference Box */}
          <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-slate-300">
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-cyan-400 shrink-0" />
              <span>
                <strong>منبع درسی رسمی:</strong> {experiment.textbook.book} — فصل {experiment.textbook.chapterNumber} ({experiment.textbook.chapter})، صفحه {experiment.textbook.page}
              </span>
            </div>
            <span className="text-emerald-400 flex items-center gap-1 font-mono text-[11px]">
              <ShieldCheck className="w-4 h-4" />
              اعتبارسنجی علمی مصوب
            </span>
          </div>

          {/* CTA Button */}
          <div className="pt-2">
            <Link to={`/experiments/${experiment.slug}/lab`}>
              <Button variant="cyan" size="lg" leftIcon={<ArrowLeft className="w-5 h-5" />}>
                ورود به محیط آزمایشگاه و شروع آزمایش
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Grid: Objectives & Safety Notes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Objectives */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <CheckCircle2 className="w-4 h-4 text-cyan-400" />
              <span>اهداف آموزشی و یادگیری</span>
            </div>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3 text-xs sm:text-sm text-slate-300">
              {experiment.objectives.map((obj, i) => (
                <li key={i} className="flex items-start gap-2.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-2 shrink-0" />
                  <span className="leading-relaxed">{obj}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Safety Notes */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>نکات ایمنی و احتیاط‌های آزمایشگاهی</span>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {experiment.safetyNotes.map((note, i) => (
              <StatusAlert key={i} type="warning">
                {note}
              </StatusAlert>
            ))}
          </CardContent>
        </Card>

      </div>

      {/* Tools & Materials Required */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2 text-white font-bold text-sm">
            <Beaker className="w-4 h-4 text-cyan-400" />
            <span>وسایل، ادوات و مواد مورد نیاز در آزمایشگاه</span>
          </div>
          <span className="text-xs text-slate-400">
            {experiment.availableTools.length} مورد موجود در قفسه
          </span>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {experiment.availableTools.map((tool) => (
              <div
                key={tool.id}
                className="rounded-xl border border-slate-800 bg-slate-900/40 p-3 flex items-start gap-3"
              >
                <div className="w-9 h-9 rounded-lg bg-slate-800 border border-slate-700/80 flex items-center justify-center text-cyan-400 shrink-0">
                  <FlaskConical className="w-4 h-4" />
                </div>
                <div className="text-right">
                  <h4 className="text-xs font-bold text-slate-200">{tool.name}</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">
                    {tool.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Step by Step Protocol */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2 text-white font-bold text-sm">
            <ListOrdered className="w-4 h-4 text-cyan-400" />
            <span>مراحل اجرای استاندارد آزمایش</span>
          </div>
          <span className="text-xs text-slate-400">{experiment.steps.length} مرحله علمی</span>
        </CardHeader>
        <CardContent className="space-y-4">
          {experiment.steps.map((st) => (
            <div
              key={st.index}
              className="rounded-xl border border-slate-800/80 bg-slate-950/60 p-4 flex items-start gap-4"
            >
              <div className="w-7 h-7 rounded-full bg-cyan-950 border border-cyan-500/50 text-cyan-300 font-bold flex items-center justify-center text-xs shrink-0 mt-0.5">
                {st.index}
              </div>
              <div className="space-y-1.5 flex-1 text-right">
                <h4 className="text-sm font-bold text-white">{st.title}</h4>
                <p className="text-xs text-slate-300 leading-relaxed">{st.instruction}</p>
                <p className="text-[11px] text-cyan-400 font-mono">
                  <strong>مفهوم علمی:</strong> {st.scientificConcept}
                </p>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

    </div>
  )
}
