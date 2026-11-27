import React from 'react'
import type { MisconceptionItem } from '../../types/analytics'

interface MisconceptionChartsProps {
  misconceptions: MisconceptionItem[]
  successRate: number
  totalAttempts: number
  completedAttempts: number
  isLight: boolean
}

export const MisconceptionCharts: React.FC<MisconceptionChartsProps> = ({
  misconceptions,
  successRate,
  totalAttempts,
  completedAttempts,
  isLight
}) => {
  // ۱. داده‌های نمودار میله‌ای (Top 5 Misconceptions)
  const topMisconceptions = misconceptions.slice(0, 5)
  const maxOccur = Math.max(...topMisconceptions.map((m) => m.occurrenceCount), 1)

  // ۲. داده‌های نمودار دونات/دایره‌ای وضعیت موفقیت
  const failedAttempts = Math.max(0, totalAttempts - completedAttempts)
  
  // محاسبه مختصات دایره‌ای SVG
  const radius = 60
  const circ = 2 * Math.PI * radius
  const successStrokeDash = (successRate / 100) * circ

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 my-6">
      
      {/* نمودار میله‌ای افقی شایع‌ترین کج‌فهمی‌ها */}
      <div className={`lg:col-span-8 p-6 rounded-3xl border transition-all ${
        isLight ? 'bg-white border-slate-200 shadow-sm' : 'bg-slate-900/90 border-indigo-500/25 shadow-xl'
      }`}>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className={`text-base font-black ${isLight ? 'text-slate-900' : 'text-white'}`}>
              📊 نمودار فراوانی کج‌فهمی‌های علمی (Bar Chart)
            </h3>
            <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              پرتکرارترین الگوهای خطای علمی دانش‌آموزان به تفکیک تعداد تکرار
            </p>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-full font-mono font-bold bg-amber-500/10 text-amber-500 border border-amber-500/20">
            {topMisconceptions.length} خطای شاخص
          </span>
        </div>

        {topMisconceptions.length === 0 ? (
          <div className="text-center py-12 text-xs text-slate-400">
            داده‌ای برای نمایش نمودار وجود ندارد.
          </div>
        ) : (
          <div className="space-y-4 pt-2">
            {topMisconceptions.map((item, idx) => {
              const pctOfMax = Math.round((item.occurrenceCount / maxOccur) * 100)
              const colors = [
                'from-rose-500 to-amber-500',
                'from-amber-500 to-yellow-400',
                'from-sky-500 to-indigo-500',
                'from-indigo-500 to-purple-500',
                'from-teal-500 to-emerald-400'
              ]
              const barGrad = colors[idx % colors.length]

              return (
                <div key={item.errorCode} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className={`font-bold truncate max-w-[70%] ${isLight ? 'text-slate-800' : 'text-slate-200'}`}>
                      {item.errorTitle}
                    </span>
                    <span className="font-mono font-black text-amber-500">
                      {item.occurrenceCount} نوبت ({item.percentage}٪)
                    </span>
                  </div>

                  <div className="w-full h-3 rounded-full bg-slate-100 dark:bg-slate-800/80 overflow-hidden p-0.5 border border-slate-200 dark:border-slate-700/50">
                    <div
                      className={`h-full rounded-full bg-gradient-to-r ${barGrad} transition-all duration-1000 shadow-sm`}
                      style={{ width: `${pctOfMax}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* نمودار دایره‌ای / دونات نرخ موفقیت کلاس */}
      <div className={`lg:col-span-4 p-6 rounded-3xl border flex flex-col justify-between transition-all ${
        isLight ? 'bg-white border-slate-200 shadow-sm' : 'bg-slate-900/90 border-indigo-500/25 shadow-xl'
      }`}>
        <div>
          <h3 className={`text-base font-black ${isLight ? 'text-slate-900' : 'text-white'}`}>
            🎯 نرخ موفقیت کلاس (Donut Chart)
          </h3>
          <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
            نسبت آزمایش‌های به پایان رسیده بدون خطا
          </p>
        </div>

        <div className="flex flex-col items-center justify-center my-4 relative">
          <svg className="w-44 h-44 -rotate-90" viewBox="0 0 160 160">
            {/* Background Circle */}
            <circle
              cx="80"
              cy="80"
              r={radius}
              stroke={isLight ? '#e2e8f0' : '#1e293b'}
              strokeWidth="16"
              fill="transparent"
            />
            {/* Success Value Circle */}
            <circle
              cx="80"
              cy="80"
              r={radius}
              stroke="#10b981"
              strokeWidth="16"
              strokeDasharray={circ}
              strokeDashoffset={circ - successStrokeDash}
              strokeLinecap="round"
              fill="transparent"
              className="transition-all duration-1000 ease-out"
            />
          </svg>

          {/* Center Label */}
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span className={`text-3xl font-black font-mono ${isLight ? 'text-slate-900' : 'text-white'}`}>
              {successRate}٪
            </span>
            <span className="text-[11px] text-emerald-500 font-bold">موفقیت کل</span>
          </div>
        </div>

        {/* Legend */}
        <div className="grid grid-cols-2 gap-2 text-xs pt-3 border-t border-slate-200/60 dark:border-slate-800">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-emerald-500 shrink-0" />
            <span className={isLight ? 'text-slate-600' : 'text-slate-300'}>موفق: {completedAttempts}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-slate-300 dark:bg-slate-700 shrink-0" />
            <span className={isLight ? 'text-slate-600' : 'text-slate-300'}>ناقص: {failedAttempts}</span>
          </div>
        </div>
      </div>

    </div>
  )
}
