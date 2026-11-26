import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/useAuthStore'
import { attemptService } from '../services/attemptService'
import type { UserProgressStats } from '../types/user'
import type { ExperimentAttempt } from '../types/attempt'
import { Card, CardHeader, CardContent, Button, Badge } from '../components/ui'
import {
  UserCircle,
  FlaskConical,
  Award,
  Clock,
  Sparkles,
  ArrowLeft,
  CheckCircle2,
  TrendingUp,
  School,
  KeyRound,
  MessageSquareCheck
} from 'lucide-react'

export const StudentDashboardPage: React.FC = () => {
  const { user } = useAuthStore()
  const [stats, setStats] = useState<UserProgressStats | null>(null)
  const [attempts, setAttempts] = useState<ExperimentAttempt[]>([])

  useEffect(() => {
    Promise.all([
      attemptService.getStudentStats(),
      attemptService.getAttemptsByUser(user?.id || 'usr-student-01')
    ]).then(([st, atts]) => {
      setStats(st)
      setAttempts(atts)
    })
  }, [user])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full space-y-8">
      
      {/* Profile Header Banner */}
      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 sm:p-8 flex flex-col sm:flex-row sm:items-center justify-between gap-6 shadow-xl relative overflow-hidden">
        <div className="absolute inset-0 lab-grid-dense opacity-25 pointer-events-none" />

        <div className="relative z-10 flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 p-0.5 shadow-lg">
            <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center text-cyan-400">
              <UserCircle className="w-9 h-9" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-black text-white">{user?.fullName || 'دانش‌آموز'}</h1>
              <Badge variant="cyan" size="sm">دانش‌آموز</Badge>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
              <span className="flex items-center gap-1">
                <School className="w-3.5 h-3.5 text-slate-400" />
                {user?.schoolName || 'دبیرستان دوره اول شهید بهشتی'}
              </span>
              <span>•</span>
              <span>پایه {user?.grade || 'هشتم'}</span>
            </div>
          </div>
        </div>

        <div className="relative z-10 flex items-center gap-3">
          <Link to="/experiments">
            <Button variant="primary" size="md" leftIcon={<KeyRound className="w-4 h-4" />}>
              ورود با کد کلاس دبیر
            </Button>
          </Link>
          <Link to="/experiments">
            <Button variant="cyan" size="md" leftIcon={<ArrowLeft className="w-4 h-4" />}>
              انجام آزمایش جدید
            </Button>
          </Link>
        </div>
      </div>

      {/* 4 Overview Statistics Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            label: 'آزمایش‌های تکمیل‌شده',
            val: stats?.completedExperiments || 2,
            unit: 'آزمایش',
            icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          },
          {
            label: 'تعداد کل تلاش‌ها',
            val: stats?.totalAttempts || 4,
            unit: 'جلسه',
            icon: <FlaskConical className="w-5 h-5 text-blue-400" />
          },
          {
            label: 'میانگین نمره علمی',
            val: `${stats?.averageScore || 92}٪`,
            unit: 'دقت آزمایش',
            icon: <TrendingUp className="w-5 h-5 text-cyan-400" />
          },
          {
            label: 'راهنمایی‌های مصرف‌شده',
            val: stats?.hintsRequestedTotal || 3,
            unit: 'مورد',
            icon: <Sparkles className="w-5 h-5 text-amber-400" />
          }
        ].map((item, i) => (
          <div key={i} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 space-y-2">
            <div className="flex items-center justify-between text-slate-400 text-xs">
              <span>{item.label}</span>
              {item.icon}
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-black text-white font-mono">{item.val}</span>
              <span className="text-[11px] text-slate-400">{item.unit}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Grid: Badges & Recent History */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Badges / Achievements (1 Column) */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <Award className="w-4 h-4 text-amber-400" />
              <span>نشان‌ها و افتخارات علمی</span>
            </div>
            <Badge variant="amber" size="sm">{stats?.badges.length || 0} نشان</Badge>
          </CardHeader>
          <CardContent className="space-y-3">
            {stats?.badges.map((b) => (
              <div
                key={b.id}
                className="p-3 rounded-xl border border-slate-800 bg-slate-950/60 flex items-start gap-3"
              >
                <div className="w-9 h-9 rounded-xl bg-amber-950/60 border border-amber-600/40 text-amber-300 flex items-center justify-center shrink-0">
                  <Award className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-200">{b.title}</h4>
                  <p className="text-[11px] text-slate-400 leading-snug mt-0.5">{b.description}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Recent Attempts History (2 Columns) */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <FlaskConical className="w-4 h-4 text-cyan-400" />
              <span>سوابق و کارنامه‌های اخیر آزمایش‌ها</span>
            </div>
            <Link to="/history" className="text-xs text-cyan-400 hover:underline">
              مشاهده همه
            </Link>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-slate-800/80">
              {attempts.map((att) => (
                <div
                  key={att.id}
                  className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-800/30 transition-colors"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-white">{att.experimentTitle}</span>
                      <Badge variant={att.status === 'COMPLETED' ? 'emerald' : 'amber'} size="sm">
                        {att.status === 'COMPLETED' ? 'تکمیل شده' : 'در حال انجام'}
                      </Badge>
                      {att.classCode && (
                        <Badge variant="indigo" size="sm" className="font-mono">
                          کلاس: {att.classCode}
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-400">
                      <span>پایه {att.grade}</span>
                      <span>•</span>
                      <span>{att.subject}</span>
                      <span>•</span>
                      <span className="flex items-center gap-1 font-mono">
                        <Clock className="w-3.5 h-3.5" />
                        {new Date(att.startedAt).toLocaleDateString('fa-IR')}
                      </span>
                    </div>

                    {att.teacherFeedback && (
                      <div className="mt-2 text-xs bg-indigo-950/40 border border-indigo-900/60 p-2.5 rounded-xl text-indigo-200 flex items-start gap-2 max-w-xl">
                        <MessageSquareCheck className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                        <div>
                          <strong className="text-indigo-300 block">ارزیابی و بازخورد معلم:</strong>
                          <p className="mt-0.5 text-slate-200 leading-relaxed">{att.teacherFeedback}</p>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <div className="text-left font-mono">
                      <span className="text-xs text-slate-400 block">نمره علمی:</span>
                      <span className="text-base font-bold text-cyan-400">{att.score}/۱۰۰</span>
                    </div>
                    <Link to={`/history/${att.id}`}>
                      <Button variant="outline" size="sm">
                        کارنامه تفصیلی
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

      </div>

    </div>
  )
}
