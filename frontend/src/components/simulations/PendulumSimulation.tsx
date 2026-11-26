import React, { useState, useEffect, useRef } from 'react'
import { Play, Pause, RotateCcw, Clock, Gauge, TrendingUp, Info } from 'lucide-react'
import { simulationService } from '../../services/simulationService'

interface PendulumSimulationProps {
  attemptId?: string | null
  onStepComplete?: (stepIndex: number, obs: string) => void
}

export const PendulumSimulation: React.FC<PendulumSimulationProps> = ({
  attemptId,
  onStepComplete
}) => {
  const [length, setLength] = useState<number>(1.0) // m (0.2 to 1.5)
  const [mass, setMass] = useState<number>(150) // g (50 to 500)
  const [initialAngle, setInitialAngle] = useState<number>(10) // degrees (small angle <= 15)
  const [isRunning, setIsRunning] = useState<boolean>(false)
  const [elapsedTime, setElapsedTime] = useState<number>(0)
  const [cycleCount, setCycleCount] = useState<number>(0)
  const [currentAngle, setCurrentAngle] = useState<number>(10)

  const g = 9.81 // m/s^2
  const theoreticalPeriod = 2 * Math.PI * Math.sqrt(length / g)

  const animRef = useRef<number | null>(null)
  const startTimeRef = useRef<number | null>(null)
  const pausedTimeRef = useRef<number>(0)

  // انیمیشن فیزیکی با معادله حرکت هارمونیک ساده
  useEffect(() => {
    if (isRunning) {
      const omega = Math.sqrt(g / length)
      const startStamp = performance.now() - pausedTimeRef.current * 1000
      startTimeRef.current = startStamp

      const animate = (timestamp: number) => {
        const t = (timestamp - startStamp) / 1000
        setElapsedTime(t)

        // زاویه در لحظه t: theta(t) = theta_0 * cos(omega * t)
        const theta = initialAngle * Math.cos(omega * t)
        setCurrentAngle(theta)

        // شمارش دوره‌های نوسان
        const cycles = Math.floor(t / theoreticalPeriod)
        setCycleCount(cycles)

        animRef.current = requestAnimationFrame(animate)
      }

      animRef.current = requestAnimationFrame(animate)

      return () => {
        if (animRef.current) cancelAnimationFrame(animRef.current)
      }
    } else {
      if (animRef.current) cancelAnimationFrame(animRef.current)
    }
  }, [isRunning, length, initialAngle, theoreticalPeriod])

  const handleStart = async () => {
    setIsRunning(true)
    if (attemptId) {
      try {
        await simulationService.executeAction(attemptId, {
          action_type: 'RELEASE_AND_MEASURE',
          source_id: 'pendulum_bob',
          parameters: { length_m: length, mass_g: mass, angle_deg: initialAngle, oscillations: 10 }
        })
      } catch (e) {
        console.warn('Backend action sync:', e)
      }
    }
  }

  const handlePause = () => {
    setIsRunning(false)
    pausedTimeRef.current = elapsedTime
    if (cycleCount >= 5 && onStepComplete) {
      onStepComplete(
        5,
        `نوسان آونگ با طول ${length}m ثبت شد: دوره تناوب تجربی ${(elapsedTime / Math.max(1, cycleCount)).toFixed(2)} ثانیه.`
      )
    }
  }

  const handleReset = () => {
    setIsRunning(false)
    setElapsedTime(0)
    setCycleCount(0)
    setCurrentAngle(initialAngle)
    pausedTimeRef.current = 0
  }

  // مختصات وزنه در تصویر آونگ SVG
  // طول نمایشی بر حسب پیکسل: تناسبی با طول واقعی
  const visualLengthPx = 70 + length * 130
  const rad = (currentAngle * Math.PI) / 180
  const originX = 140
  const originY = 30
  const bobX = originX + visualLengthPx * Math.sin(rad)
  const bobY = originY + visualLengthPx * Math.cos(rad)
  // اندازه وزنه متناسب با جرم
  const bobRadius = 12 + (mass / 500) * 10

  // داده‌های جدول مقایسه طول و دوره تناوب
  const tableData = [
    { L: 0.25, sqrtL: 0.5, T: (2 * Math.PI * Math.sqrt(0.25 / 9.81)).toFixed(2), T2: (4 * Math.PI * Math.PI * (0.25 / 9.81)).toFixed(2) },
    { L: 0.5, sqrtL: 0.71, T: (2 * Math.PI * Math.sqrt(0.5 / 9.81)).toFixed(2), T2: (4 * Math.PI * Math.PI * (0.5 / 9.81)).toFixed(2) },
    { L: 1.0, sqrtL: 1.0, T: (2 * Math.PI * Math.sqrt(1.0 / 9.81)).toFixed(2), T2: (4 * Math.PI * Math.PI * (1.0 / 9.81)).toFixed(2) },
    { L: 1.44, sqrtL: 1.2, T: (2 * Math.PI * Math.sqrt(1.44 / 9.81)).toFixed(2), T2: (4 * Math.PI * Math.PI * (1.44 / 9.81)).toFixed(2) }
  ]

  return (
    <div className="w-full bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl text-slate-100 space-y-6">
      
      {/* هدر آزمایش آونگ */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Gauge className="w-5 h-5" />
            </span>
            <h3 className="text-base font-black text-white">
              شبیه‌ساز فیزیک آونگ ساده و اثبات دوره تناوب
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            علوم تجربی پایه نهم | فصل حرکت | رابطه دوره تناوب با طول نخ و شتاب گرانش
          </p>
        </div>

        {/* فرمول علمی دوره تناوب */}
        <div className="px-4 py-2 rounded-2xl bg-slate-950/80 border border-cyan-500/30 text-xs font-mono text-cyan-200 text-left dir-ltr shadow-inner">
          T = 2π √(L / g) &nbsp;|&nbsp; θ ≤ 15°
        </div>
      </div>

      {/* ناحیه مرکزی: آونگ متحرک + پنل کنترل و جدول تجربی */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        {/* تصویر گرافیکی زنده آونگ SVG */}
        <div className="lg:col-span-6 flex flex-col items-center justify-center p-6 bg-slate-950/60 rounded-2xl border border-slate-800 relative min-h-[380px]">
          
          {/* زمان‌سنج دیجیتال و شمارنده نوسان */}
          <div className="absolute top-4 right-4 flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/80 border border-slate-700 text-xs font-mono text-cyan-300">
            <Clock className="w-4 h-4 text-cyan-400" />
            <span>{elapsedTime.toFixed(2)} s</span>
          </div>

          <div className="absolute top-4 left-4 flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900/80 border border-slate-700 text-xs font-bold text-amber-300">
            <span>تعداد نوسان‌ها:</span>
            <span className="font-mono">{cycleCount}</span>
          </div>

          {/* بوم نمایش آونگ با SVG */}
          <svg width="280" height="290" className="overflow-visible">
            {/* پایه نگهدارنده افقی */}
            <rect x="70" y="15" width="140" height="12" rx="4" fill="#334155" />
            <circle cx="140" cy="21" r="5" fill="#06b6d4" />

            {/* خط عمود راهنما (موقعیت تعادل آونگ) */}
            <line
              x1={originX}
              y1={originY}
              x2={originX}
              y2={originY + visualLengthPx + 10}
              stroke="#475569"
              strokeDasharray="4 4"
              strokeWidth="1.5"
            />

            {/* کمان زاویه نوسان */}
            <path
              d={`M ${originX} ${originY + 45} A 45 45 0 0 ${currentAngle > 0 ? 1 : 0} ${originX + 45 * Math.sin(rad)} ${originY + 45 * Math.cos(rad)}`}
              fill="none"
              stroke="#eab308"
              strokeWidth="1.5"
            />
            <text x="145" y="75" fill="#facc15" fontSize="10" fontFamily="sans-serif">
              {Math.abs(Math.round(currentAngle))}°
            </text>

            {/* نخ آونگ */}
            <line
              x1={originX}
              y1={originY}
              x2={bobX}
              y2={bobY}
              stroke="#94a3b8"
              strokeWidth="2.5"
            />

            {/* وزنه آونگ */}
            <circle
              cx={bobX}
              cy={bobY}
              r={bobRadius}
              fill="url(#bobGradient)"
              stroke="#38bdf8"
              strokeWidth="2"
              className="filter drop-shadow-md"
            />

            <defs>
              <radialGradient id="bobGradient" cx="35%" cy="35%">
                <stop offset="0%" stopColor="#38bdf8" />
                <stop offset="70%" stopColor="#0284c7" />
                <stop offset="100%" stopColor="#0f172a" />
              </radialGradient>
            </defs>
          </svg>

          {/* شاخص دوره تناوب تئوری */}
          <div className="mt-2 text-xs font-mono text-slate-400 flex items-center gap-3">
            <span>دوره تناوب تئوری (T): <strong className="text-cyan-300">{theoreticalPeriod.toFixed(2)} ثانیه</strong></span>
          </div>
        </div>

        {/* پنل تنظیمات پیشرفته و پارامترها */}
        <div className="lg:col-span-6 space-y-4">
          
          {/* اسلایدر طول نخ L */}
          <div className="bg-slate-950/70 p-4 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-300 font-bold">طول نخ آونگ (L):</span>
              <span className="font-mono text-cyan-300 font-bold">{length.toFixed(2)} متر</span>
            </div>
            <input
              type="range"
              min="0.2"
              max="1.5"
              step="0.05"
              disabled={isRunning}
              value={length}
              onChange={(e) => setLength(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>۰.۲۰ متر (کوتاه)</span>
              <span>۰.۸۵ m</span>
              <span>۱.۵۰ متر (بلند)</span>
            </div>
          </div>

          {/* اسلایدر جرم وزنه m */}
          <div className="bg-slate-950/70 p-4 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-300 font-bold">جرم وزنه (m) — عدم تاثیر بر دوره تناوب:</span>
              <span className="font-mono text-amber-300 font-bold">{mass} گرم</span>
            </div>
            <input
              type="range"
              min="50"
              max="500"
              step="25"
              disabled={isRunning}
              value={mass}
              onChange={(e) => setMass(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>۵۰ گرم (سبک)</span>
              <span>۲۵۰ g</span>
              <span>۵۰۰ گرم (سنگین)</span>
            </div>
          </div>

          {/* اسلایدر زاویه اولیه با تاکید بر شرط زاویه کوچک */}
          <div className="bg-slate-950/70 p-4 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-300 font-bold">زاویه انحراف اولیه (θ ≤ ۱۵°):</span>
              <span className="font-mono text-emerald-300 font-bold">{initialAngle}°</span>
            </div>
            <input
              type="range"
              min="4"
              max="15"
              step="1"
              disabled={isRunning}
              value={initialAngle}
              onChange={(e) => {
                setInitialAngle(Number(e.target.value))
                if (!isRunning) setCurrentAngle(Number(e.target.value))
              }}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
            <span className="text-[10px] text-slate-400 block">
              توجه علمی: تقریب sin(θ) ≈ θ تنها در زوایای کوچک (کمتر از ۱۵ درجه) معتبر است.
            </span>
          </div>

          {/* دکمه‌های کنترل نوسان و زمان‌سنج */}
          <div className="flex items-center gap-3 pt-2">
            {!isRunning ? (
              <button
                onClick={handleStart}
                className="flex-1 py-3 px-5 rounded-2xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-cyan-600/30"
              >
                <Play className="w-4 h-4" />
                <span>رهاسازی و آغاز نوسان</span>
              </button>
            ) : (
              <button
                onClick={handlePause}
                className="flex-1 py-3 px-5 rounded-2xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-amber-600/30"
              >
                <Pause className="w-4 h-4" />
                <span>توقف زمان‌سنج و ثبت دوره</span>
              </button>
            )}

            <button
              onClick={handleReset}
              className="py-3 px-4 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs flex items-center justify-center gap-2 transition-all border border-slate-700"
            >
              <RotateCcw className="w-4 h-4" />
              <span>ریست</span>
            </button>
          </div>
        </div>
      </div>

      {/* جدول داده‌های علمی: رابطه طول نخ با مجذور دوره تناوب (T² ∝ L) */}
      <div className="bg-slate-950/70 p-4 rounded-2xl border border-slate-800/80 space-y-3">
        <div className="flex items-center gap-2 font-bold text-xs text-cyan-300">
          <TrendingUp className="w-4 h-4" />
          <span>جدول نتایج تحلیلی: رابطه خطی مجذور دوره تناوب (T²) با طول نخ (L)</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-center text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="py-2">طول نخ L (متر)</th>
                <th className="py-2">رادیکال طول √L</th>
                <th className="py-2">دوره تناوب T (ثانیه)</th>
                <th className="py-2">مربع زمان تناوب T² (s²)</th>
                <th className="py-2">نسبت T² / L (≈ 4.02)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
              {tableData.map((row, idx) => (
                <tr key={idx} className={Math.abs(length - row.L) < 0.15 ? 'bg-cyan-500/10 text-cyan-200' : ''}>
                  <td className="py-2">{row.L}</td>
                  <td className="py-2">{row.sqrtL}</td>
                  <td className="py-2 font-bold">{row.T}</td>
                  <td className="py-2">{row.T2}</td>
                  <td className="py-2 text-emerald-400">{(Number(row.T2) / row.L).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* بخش پداگوژیک: چه چیزی یاد گرفتیم؟ */}
      <div className="p-4 rounded-2xl bg-cyan-950/30 border border-cyan-500/20 text-xs space-y-2">
        <div className="flex items-center gap-2 font-bold text-cyan-300">
          <Info className="w-4 h-4" />
          <span>چه چیزی از این آزمایش یاد گرفتیم؟</span>
        </div>
        <ul className="list-disc list-inside text-slate-300 space-y-1 text-[11px] leading-relaxed">
          <li>
            <strong>تاثیر طول نخ:</strong> با ۴ برابر شدن طول نخ آونگ، زمان یک نوسان کامل (دوره تناوب) ۲ برابر می‌شود (T ∝ √L).
          </li>
          <li>
            <strong>استقلال دوره از جرم:</strong> تغییر جرم وزنه (سبک یا سنگین) هیچ تاثیری در دوره تناوب آونگ ندارد؛ زیرا شتاب گرانش بر تمام اجسام یکسان اثر می‌کند.
          </li>
          <li>
            <strong>محدودیت زاویه کوچک:</strong> فرمول T = 2π√(L/g) تنها زمانی با دقت بالا صادق است که زاویه انحراف کمتر از ۱۵ درجه باشد.
          </li>
        </ul>
      </div>
    </div>
  )
}
export default PendulumSimulation
