import React from 'react'
import { Link } from 'react-router-dom'
import type { Experiment } from '../../types/experiment'
import { Card, CardContent } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { useThemeStore } from '../../store/useThemeStore'
import {
  FlaskConical,
  Zap,
  Filter,
  Gauge,
  Leaf,
  TestTube,
  Clock,
  BookOpen,
  ArrowLeft,
  ShieldCheck
} from 'lucide-react'

export interface ExperimentCardProps {
  experiment: Experiment
  onActionClick?: () => void
}

export const ExperimentCard: React.FC<ExperimentCardProps> = ({ experiment }) => {
  const { theme } = useThemeStore()
  const isLight = theme === 'light'

  const getThumbnailIcon = () => {
    switch (experiment.thumbnailSvgType) {
      case 'circuit':
        return <Zap className={`w-10 h-10 ${isLight ? 'text-amber-500' : 'text-cyan-400'}`} />
      case 'filter':
        return <Filter className={`w-10 h-10 ${isLight ? 'text-teal-600' : 'text-teal-400'}`} />
      case 'gauge':
        return <Gauge className={`w-10 h-10 ${isLight ? 'text-sky-600' : 'text-cyan-400'}`} />
      case 'leaf':
        return <Leaf className={`w-10 h-10 ${isLight ? 'text-emerald-600' : 'text-emerald-400'}`} />
      case 'test-tube':
        return <TestTube className={`w-10 h-10 ${isLight ? 'text-amber-600' : 'text-amber-400'}`} />
      case 'flask':
      default:
        return <FlaskConical className={`w-10 h-10 ${isLight ? 'text-indigo-600' : 'text-blue-400'}`} />
    }
  }

  const getDifficultyVariant = () => {
    switch (experiment.difficulty) {
      case 'آسان':
        return 'emerald'
      case 'متوسط':
        return 'amber'
      case 'پیشرفته':
        return 'rose'
      default:
        return 'slate'
    }
  }

  return (
    <Card hoverable className={`flex flex-col h-full rounded-3xl overflow-hidden transition-all duration-300 group ${
      isLight
        ? 'border border-slate-200/90 bg-white shadow-sm hover:border-sky-300 hover:shadow-lg hover:shadow-sky-500/10'
        : 'border border-indigo-500/20 bg-gradient-to-b from-slate-900/90 to-slate-950/90 shadow-lg shadow-indigo-950/20 hover:border-cyan-400/50 hover:shadow-cyan-500/15'
    }`}>
      
      {/* Card Header Media & Icons */}
      <div className={`relative h-44 p-5 flex flex-col justify-between overflow-hidden border-b transition-colors ${
        isLight
          ? 'bg-gradient-to-br from-amber-50/80 via-sky-50/50 to-emerald-50/50 border-slate-100'
          : 'bg-gradient-to-br from-indigo-950/80 via-slate-900 to-purple-950/60 border-indigo-500/20'
      }`}>
        <div className={`absolute inset-0 lab-grid-dense pointer-events-none ${isLight ? 'opacity-15' : 'opacity-30 group-hover:opacity-60'} transition-opacity`} />
        
        {/* Top Badges */}
        <div className="relative z-10 flex items-center justify-between gap-1">
          <div className="flex items-center gap-1.5 flex-wrap">
            <Badge variant={isLight ? 'indigo' : 'cyan'} size="sm" className="font-bold">
              پایه {experiment.grade}
            </Badge>
            {experiment.classCode && (
              <Badge variant="indigo" size="sm" className="font-mono">
                {experiment.isClassOnly ? '🔒 کلاس:' : 'کد:'} {experiment.classCode}
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-1.5">
            <Badge variant={getDifficultyVariant()} size="sm">
              {experiment.difficulty}
            </Badge>
            <Badge variant={isLight ? 'cyan' : 'indigo'} size="sm" className="font-bold">
              {experiment.subject}
            </Badge>
          </div>
        </div>

        {/* Center Schematic Art */}
        <div className="relative z-10 flex items-center justify-center py-2 group-hover:scale-110 transition-transform duration-300">
          <div className={`w-16 h-16 rounded-2xl border flex items-center justify-center shadow-md ${
            isLight
              ? 'bg-white border-slate-200 shadow-slate-200/80'
              : 'bg-gradient-to-br from-indigo-900/90 to-slate-900 border-cyan-400/40 shadow-cyan-500/20'
          }`}>
            {getThumbnailIcon()}
          </div>
        </div>

        {/* Bottom meta */}
        <div className={`relative z-10 flex items-center justify-between text-[11px] ${
          isLight ? 'text-slate-600' : 'text-slate-300'
        }`}>
          <span className="flex items-center gap-1 font-medium">
            <Clock className={`w-3.5 h-3.5 ${isLight ? 'text-amber-600' : 'text-amber-400'}`} />
            {experiment.durationMinutes} دقیقه
          </span>
          <span className={`flex items-center gap-1 font-medium ${
            isLight ? 'text-emerald-700' : 'text-emerald-300'
          }`}>
            <ShieldCheck className="w-3.5 h-3.5" />
            تایید رسمی کتب درسی
          </span>
        </div>
      </div>

      {/* Card Content */}
      <CardContent className="flex-1 flex flex-col justify-between p-5 space-y-4">
        <div>
          <h3 className={`text-base font-black transition-colors line-clamp-1 mb-2 ${
            isLight ? 'text-slate-900 group-hover:text-sky-600' : 'text-white group-hover:text-cyan-300'
          }`}>
            {experiment.title}
          </h3>
          <p className={`text-xs line-clamp-2 leading-relaxed mb-3 ${
            isLight ? 'text-slate-600' : 'text-slate-400'
          }`}>
            {experiment.summary}
          </p>

          <div className={`pt-2 border-t flex items-center gap-2 text-[11px] ${
            isLight ? 'border-slate-100 text-slate-500' : 'border-slate-800/60 text-slate-400'
          }`}>
            <BookOpen className={`w-3.5 h-3.5 shrink-0 ${isLight ? 'text-sky-600' : 'text-blue-400'}`} />
            <span className="truncate">
              {experiment.textbook.book} — فصل {experiment.textbook.chapterNumber} (ص {experiment.textbook.page})
            </span>
          </div>
        </div>

        {/* Card Footer Actions */}
        <div className="pt-2 flex items-center gap-2">
          <Link to={`/experiments/${experiment.slug}`} className="flex-1">
            <Button variant="outline" size="sm" className="w-full font-bold">
              اهداف و وسایل
            </Button>
          </Link>
          <Link to={`/experiments/${experiment.slug}/lab`} className="flex-1">
            <Button
              variant="cyan"
              size="sm"
              className="w-full font-bold bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:from-emerald-600 hover:to-teal-700"
              leftIcon={<ArrowLeft className="w-4 h-4" />}
            >
              ورود به آزمایشگاه
            </Button>
          </Link>
        </div>
      </CardContent>

    </Card>
  )
}
