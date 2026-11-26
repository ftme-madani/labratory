import React, { useState } from 'react'
import { Eye, Info, RefreshCw, Clock } from 'lucide-react'
import { simulationService } from '../../services/simulationService'

interface PlantTransportProps {
  attemptId?: string | null
  onStepComplete?: (stepIndex: number, obs: string) => void
}

export const PlantTransportSimulation: React.FC<PlantTransportProps> = ({
  attemptId,
  onStepComplete
}) => {
  const [selectedColor, setSelectedColor] = useState<'red' | 'blue'>('red')
  const [simulatedHours, setSimulatedHours] = useState<number>(0)
  const [viewMode, setViewMode] = useState<'stalk' | 'cross_section'>('stalk')

  const timeMilestones = [
    { hours: 0, label: 'آغاز (۰ ساعت)', desc: 'کرفس تازه در آب رنگی قرار گرفته است.' },
    { hours: 1, label: '۱ ساعت بعد', desc: 'شیره رنگی تا ارتفاع ۵ سانتی‌متر در قاعده ساقه بالا آمده است.' },
    { hours: 4, label: '۴ ساعت بعد', desc: 'رنگ به نیمه ساقه رسیده و خطوط آوندها به وضوح مشخص است.' },
    { hours: 12, label: '۱۲ ساعت بعد', desc: 'رنگ به برگ‌ها رسیده و رگبرگ‌های اصلی سرخ/آبی شده‌اند.' },
    { hours: 24, label: '۲۴ ساعت بعد', desc: 'رنگ‌پذیری کامل پهنک برگ و تمام رگبرگ‌ها بر اثر مکش تعرق.' }
  ]

  const handleTimeChange = async (hours: number) => {
    setSimulatedHours(hours)
    if (attemptId) {
      try {
        await simulationService.executeAction(attemptId, {
          action_type: 'SIMULATE_TIME',
          source_id: 'celery_stalk',
          parameters: { hours, color: selectedColor }
        })
      } catch (e) {
        console.warn('Backend sync failed:', e)
      }
    }

    if (hours >= 12 && onStepComplete) {
      onStepComplete(
        4,
        `پس از گذشت ${hours} ساعت شبیه‌سازی‌شده، صعود آب رنگی در آوندهای چوبی و رنگ‌پذیری رگبرگ‌ها مشاهده شد.`
      )
    }
  }

  // درصد صعود رنگ در ساقه
  const progressRatio = Math.min(1, simulatedHours / 24)
  const colorHex = selectedColor === 'red' ? '#ef4444' : '#3b82f6'
  const colorBg = selectedColor === 'red' ? 'rgba(239, 68, 68, 0.85)' : 'rgba(59, 130, 246, 0.85)'

  return (
    <div className="w-full bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl text-slate-100 space-y-6">
      
      {/* هدر آزمایش زیست کرفس و آوند چوبی */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Eye className="w-5 h-5" />
            </span>
            <h3 className="text-base font-black text-white">
              شبیه‌ساز انتقال آب و املاح در آوندهای چوبی ساقه کرفس
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            علوم تجربی پایه هفتم | سفر آب درون گیاه | پدیده تعرق، مویینگی و آوندهای چوبی (Xylem)
          </p>
        </div>

        {/* برچسب فشرده‌سازی زمان */}
        <div className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-bold">
          <Clock className="w-4 h-4" />
          <span>شبیه‌سازی گذر زمان واقعی به صورت فشرده</span>
        </div>
      </div>

      {/* ناحیه مرکزی */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        {/* بوم گرافیکی نمایش ساقه یا برش عرضی */}
        <div className="lg:col-span-6 flex flex-col items-center justify-center p-6 bg-slate-950/60 rounded-2xl border border-slate-800 relative min-h-[380px]">
          
          {/* دکمه جابجایی بین نمای ساقه و برش عرضی میکروسکوپی */}
          <div className="absolute top-4 left-4 flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-slate-700 text-xs z-10">
            <button
              onClick={() => setViewMode('stalk')}
              className={`px-3 py-1 rounded-lg font-bold transition-all ${
                viewMode === 'stalk' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              نمای کلی ساقه
            </button>
            <button
              onClick={() => setViewMode('cross_section')}
              className={`px-3 py-1 rounded-lg font-bold transition-all ${
                viewMode === 'cross_section' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              برش عرضی (میکروسکوپ)
            </button>
          </div>

          {viewMode === 'stalk' ? (
            /* نمای کلی ساقه کرفس درون لیوان */
            <div className="relative w-48 h-72 flex flex-col items-center justify-end">
              
              {/* برگ‌های بالایی ساقه کرفس */}
              <div className="absolute top-2 w-36 h-28 pointer-events-none transition-all duration-700">
                {/* برگ چپ */}
                <svg viewBox="0 0 100 100" className="w-16 h-16 absolute -left-2 top-2">
                  <path
                    d="M 50 90 Q 20 50 10 20 Q 50 30 70 60 Z"
                    fill={progressRatio > 0.4 ? colorBg : '#15803d'}
                    stroke={selectedColor === 'red' ? '#b91c1c' : '#1d4ed8'}
                    strokeWidth={progressRatio > 0.4 ? '1.5' : '0.5'}
                    className="transition-colors duration-1000"
                  />
                </svg>

                {/* برگ مرکزی */}
                <svg viewBox="0 0 100 100" className="w-20 h-20 absolute left-8 -top-2">
                  <path
                    d="M 50 95 Q 40 40 50 10 Q 60 40 50 95 Z"
                    fill={progressRatio > 0.3 ? colorBg : '#16a34a'}
                    stroke={selectedColor === 'red' ? '#b91c1c' : '#1d4ed8'}
                    strokeWidth={progressRatio > 0.3 ? '1.5' : '0.5'}
                    className="transition-colors duration-1000"
                  />
                  {/* رگبرگ‌های رنگی برگ وسط */}
                  {progressRatio > 0.4 && (
                    <line x1="50" y1="95" x2="50" y2="20" stroke={colorHex} strokeWidth="2" />
                  )}
                </svg>

                {/* برگ راست */}
                <svg viewBox="0 0 100 100" className="w-16 h-16 absolute right-0 top-2">
                  <path
                    d="M 50 90 Q 80 50 90 20 Q 50 30 30 60 Z"
                    fill={progressRatio > 0.4 ? colorBg : '#15803d'}
                    stroke={selectedColor === 'red' ? '#b91c1c' : '#1d4ed8'}
                    strokeWidth={progressRatio > 0.4 ? '1.5' : '0.5'}
                    className="transition-colors duration-1000"
                  />
                </svg>
              </div>

              {/* ساقه کرفس */}
              <div className="relative w-14 h-48 bg-gradient-to-r from-emerald-700 via-emerald-500 to-emerald-800 rounded-t-lg border border-emerald-400/40 overflow-hidden shadow-inner flex justify-center">
                
                {/* شیارهای آوندهای چوبی درون ساقه */}
                <div className="w-full h-full flex justify-around px-1">
                  <div className="w-1.5 h-full bg-emerald-900/40 relative">
                    {/* صعود شیره رنگی در آوند چوبی */}
                    <div
                      className="absolute bottom-0 w-full rounded-full transition-all duration-1000"
                      style={{
                        height: `${progressRatio * 100}%`,
                        backgroundColor: colorHex
                      }}
                    />
                  </div>
                  <div className="w-1.5 h-full bg-emerald-900/40 relative">
                    <div
                      className="absolute bottom-0 w-full rounded-full transition-all duration-1000"
                      style={{
                        height: `${Math.min(100, progressRatio * 110)}%`,
                        backgroundColor: colorHex
                      }}
                    />
                  </div>
                  <div className="w-1.5 h-full bg-emerald-900/40 relative">
                    <div
                      className="absolute bottom-0 w-full rounded-full transition-all duration-1000"
                      style={{
                        height: `${progressRatio * 95}%`,
                        backgroundColor: colorHex
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* لیوان شیشه‌ای شفاف حاوی آب رنگی */}
              <div className="absolute bottom-0 w-36 h-28 border-2 border-slate-400/60 border-t-0 rounded-b-3xl bg-slate-800/30 flex flex-col justify-end p-1.5 shadow-xl">
                {/* مایع آب رنگی در لیوان */}
                <div
                  className="w-full h-16 rounded-b-2xl transition-colors duration-500 relative"
                  style={{ backgroundColor: colorBg }}
                >
                  <span className="absolute bottom-1 right-2 text-[8px] font-mono text-white/90">
                    محلول رنگی خوراکی
                  </span>
                </div>
              </div>
            </div>
          ) : (
            /* نمای برش عرضی ساقه زیر میکروسکوپ */
            <div className="flex flex-col items-center justify-center p-4 animate-in fade-in">
              <span className="text-xs font-bold text-emerald-300 mb-3">
                برش عرضی ساقه کرفس (مشاهده دسته‌های آوندی)
              </span>

              {/* دایره نمای میکروسکوپ */}
              <div className="w-52 h-52 rounded-full border-4 border-slate-600 bg-emerald-950/80 relative flex items-center justify-center shadow-2xl overflow-hidden">
                
                {/* مقطع هلالی ساقه کرفس */}
                <div className="w-40 h-28 rounded-b-full border-2 border-emerald-400 bg-emerald-800/60 relative flex items-center justify-around px-4">
                  
                  {/* نقاط دسته‌های آوندی چوبی (Vascular Bundles) */}
                  {Array.from({ length: 7 }).map((_, idx) => (
                    <div
                      key={idx}
                      className="flex flex-col items-center transition-all duration-700"
                      style={{ transform: `translateY(${Math.sin((idx / 6) * Math.PI) * 12}px)` }}
                    >
                      <div
                        className="w-3.5 h-3.5 rounded-full border-2 transition-all duration-1000"
                        style={{
                          backgroundColor: progressRatio > 0.05 ? colorHex : '#064e3b',
                          borderColor: progressRatio > 0.05 ? '#ffffff' : '#047857'
                        }}
                      />
                      <span className="text-[7px] text-white/80 mt-0.5">آوند</span>
                    </div>
                  ))}
                </div>
              </div>

              <span className="text-[10px] text-slate-400 mt-3 text-center">
                نقاط رنگی نمایانگر آوندهای چوبی (Xylem) هستند که آب رنگی را به سمت بالا هدایت کرده‌اند.
              </span>
            </div>
          )}

          <span className="text-xs font-bold text-slate-300 mt-2">
            وضعیت پس از گذشت {simulatedHours} ساعت
          </span>
        </div>

        {/* پنل کنترل پارامترها و بازه زمانی */}
        <div className="lg:col-span-6 space-y-5">
          
          {/* انتخاب رنگ خوراکی */}
          <div className="bg-slate-950/70 p-4 rounded-2xl border border-slate-800 space-y-2">
            <span className="text-xs text-slate-300 font-bold block">انتخاب رنگ خوراکی معرف:</span>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSelectedColor('red')}
                className={`flex-1 py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-2 border transition-all ${
                  selectedColor === 'red'
                    ? 'bg-rose-600 border-rose-400 text-white shadow-lg shadow-rose-600/30'
                    : 'bg-slate-900 border-slate-700 text-slate-400 hover:text-slate-200'
                }`}
              >
                <div className="w-3 h-3 rounded-full bg-rose-400" />
                <span>رنگ سرخ خوراکی</span>
              </button>

              <button
                onClick={() => setSelectedColor('blue')}
                className={`flex-1 py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-2 border transition-all ${
                  selectedColor === 'blue'
                    ? 'bg-blue-600 border-blue-400 text-white shadow-lg shadow-blue-600/30'
                    : 'bg-slate-900 border-slate-700 text-slate-400 hover:text-slate-200'
                }`}
              >
                <div className="w-3 h-3 rounded-full bg-blue-400" />
                <span>رنگ آبی خوراکی</span>
              </button>
            </div>
          </div>

          {/* خط زمان شبیه‌سازی فشرده (ساعات گذر زمان) */}
          <div className="bg-slate-950/70 p-4 rounded-2xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-300 font-bold">انتخاب زمان سپری‌شده در شبیه‌سازی:</span>
              <span className="font-mono text-emerald-300 font-bold">{simulatedHours} ساعت</span>
            </div>

            <div className="grid grid-cols-5 gap-2">
              {timeMilestones.map((m) => (
                <button
                  key={m.hours}
                  onClick={() => handleTimeChange(m.hours)}
                  className={`py-2 px-1 text-center rounded-xl text-[11px] font-bold border transition-all ${
                    simulatedHours === m.hours
                      ? 'bg-emerald-600 border-emerald-400 text-white shadow-md shadow-emerald-600/20'
                      : 'bg-slate-900 border-slate-700 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {m.hours}h
                </button>
              ))}
            </div>

            {/* توضیح وضعیت در این زمان */}
            <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-[11px] text-slate-300">
              {timeMilestones.find((m) => m.hours === simulatedHours)?.desc}
            </div>
          </div>

          {/* ریست آزمایش */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => handleTimeChange(0)}
              className="py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs flex items-center justify-center gap-2 transition-all border border-slate-700"
            >
              <RefreshCw className="w-4 h-4" />
              <span>بازگشت به زمان اولیه (ساعت ۰)</span>
            </button>
          </div>
        </div>
      </div>

      {/* بخش پداگوژیک: چه چیزی یاد گرفتیم؟ */}
      <div className="p-4 rounded-2xl bg-emerald-950/30 border border-emerald-500/20 text-xs space-y-2">
        <div className="flex items-center gap-2 font-bold text-emerald-300">
          <Info className="w-4 h-4" />
          <span>چه چیزی از این آزمایش یاد گرفتیم؟ (مفاهیم کتاب زیست پایه هفتم)</span>
        </div>
        <ul className="list-disc list-inside text-slate-300 space-y-1 text-[11px] leading-relaxed">
          <li>
            <strong>مسیر یک‌طرفه آوندهای چوبی:</strong> آوندهای چوبی لوله‌های باریکی از سلول‌های مرده هستند که آب و نمک‌های معدنی را از ریشه و ساقه به سمت برگ‌ها بالا می‌برند.
          </li>
          <li>
            <strong>مکش تعرق (Transpiration Pull):</strong> تبخیر آب از روزنه‌های برگ باعث ایجاد فشار منفی (مکش) می‌شود که ستون پیوسته‌ای از مولکول‌های آب را از آوندها بالا می‌کشد.
          </li>
          <li>
            <strong>آرایش دسته‌های آوندی:</strong> در برش عرضی ساقه کرفس، آوندها به شکل دسته‌هایی منظم در حاشیه ساقه قرار دارند که با رنگ‌آمیزی به خوبی قابل مشاهده هستند.
          </li>
        </ul>
      </div>
    </div>
  )
}
export default PlantTransportSimulation
