import React, { useState, useEffect } from 'react'
import { Beaker, Sparkles, RefreshCw, Play, Info, Thermometer } from 'lucide-react'
import { simulationService } from '../../services/simulationService'

interface VinegarReactionProps {
  attemptId?: string | null
  onStepComplete?: (stepIndex: number, obs: string) => void
}

export const VinegarReactionSimulation: React.FC<VinegarReactionProps> = ({
  attemptId,
  onStepComplete
}) => {
  const [vinegarVolume, setVinegarVolume] = useState<number>(50) // ml
  const [bakingSodaMass, setBakingSodaMass] = useState<number>(5) // g
  const [stage, setStage] = useState<'ready' | 'vinegar_poured' | 'reacting' | 'completed'>('ready')
  const [foamLevel, setFoamLevel] = useState<number>(0)
  const [tempDrop, setTempDrop] = useState<number>(0)
  const [co2Volume, setCo2Volume] = useState<number>(0)
  const [limitingReagent, setLimitingReagent] = useState<string>('')
  const [bubbles, setBubbles] = useState<Array<{ id: number; left: number; delay: number; size: number }>>([])

  // محاسبه استوکیومتری بر مبنای مقادیر واقعی
  // سرکه ۵٪ اسید استیک: غلظت تقریباً ۰.۸۳ مولار
  const aceticMoles = (vinegarVolume * 1.005 * 0.05) / 60.05
  // جوش‌شیرین: جرم مولی ۸۴.۰۰۷ گرم بر مول
  const sodaMoles = bakingSodaMass / 84.007

  useEffect(() => {
    if (stage === 'reacting') {
      const limiting = sodaMoles <= aceticMoles ? 'جوش‌شیرین (تمام شد)' : 'سرکه (اسید تمام شد)'
      setLimitingReagent(limiting)
      const molesReacted = Math.min(aceticMoles, sodaMoles)
      // حجم گاز در شرایط استاندارد آزمایشگاه: هر مول ۲۴.۴۵ لیتر
      const co2Ml = Math.round(molesReacted * 24450)
      setCo2Volume(co2Ml)
      setTempDrop(parseFloat((molesReacted * 28).toFixed(1)))

      // تولید حباب‌های متحرک
      const newBubbles = Array.from({ length: 24 }).map((_, i) => ({
        id: i,
        left: 15 + Math.random() * 70,
        delay: Math.random() * 1.5,
        size: 4 + Math.random() * 8
      }))
      setBubbles(newBubbles)

      // بالا آمدن کف فوم
      const maxFoam = Math.min(95, Math.max(30, (co2Ml / 10) + 20))
      setFoamLevel(maxFoam)

      const timer = setTimeout(() => {
        setStage('completed')
        setFoamLevel(maxFoam * 0.45) // فرونشست تدریجی کف پس از خروج گاز
        if (onStepComplete) {
          onStepComplete(
            4,
            `واکنش کامل شد: ${co2Ml} میلی‌لیتر گاز CO₂ آزاد شد و دما ${tempDrop} درجه کاهش یافت.`
          )
        }
      }, 3500)

      return () => clearTimeout(timer)
    }
  }, [stage, aceticMoles, sodaMoles, vinegarVolume, bakingSodaMass, onStepComplete, tempDrop])

  const handlePourVinegar = async () => {
    setStage('vinegar_poured')
    if (attemptId) {
      try {
        await simulationService.executeAction(attemptId, {
          action_type: 'POUR_VINEGAR',
          source_id: 'vinegar_bottle',
          target_id: 'beaker_1',
          parameters: { volume_ml: vinegarVolume }
        })
      } catch (e) {
        console.warn('Backend action failed, running locally:', e)
      }
    }
  }

  const handleStartReaction = async () => {
    setStage('reacting')
    if (attemptId) {
      try {
        await simulationService.executeAction(attemptId, {
          action_type: 'ADD_BAKING_SODA',
          source_id: 'baking_soda_jar',
          target_id: 'beaker_1',
          parameters: { mass_g: bakingSodaMass }
        })
      } catch (e) {
        console.warn('Backend action failed, running locally:', e)
      }
    }
  }

  const handleReset = () => {
    setStage('ready')
    setFoamLevel(0)
    setCo2Volume(0)
    setTempDrop(0)
  }

  return (
    <div className="w-full bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl text-slate-100 space-y-6">
      {/* عنوان و مشخصه واکنش */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Beaker className="w-5 h-5" />
            </span>
            <h3 className="text-base font-black text-white">
              شبیه‌ساز تعاملی واکنش سرکه و جوش‌شیرین (تولید گاز کربن دی‌اکسید)
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            علوم تجربی پایه هشتم | تغییرهای شیمیایی در خدمت زندگی | واکنش اسید و کربنات
          </p>
        </div>

        {/* معادله واکنش موازنه شده */}
        <div className="px-4 py-2 rounded-2xl bg-slate-950/80 border border-purple-500/30 text-xs font-mono text-purple-200 text-left dir-ltr shadow-inner">
          CH₃COOH + NaHCO₃ → CH₃COONa + H₂O + CO₂↑
        </div>
      </div>

      {/* ناحیه مرکزی: تصویر آزمایشگاه و پنل تنظیمات */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        {/* تصویر گرافیکی زنده بشر و واکنش */}
        <div className="lg:col-span-6 flex flex-col items-center justify-center p-6 bg-slate-950/60 rounded-2xl border border-slate-800 relative min-h-[360px] overflow-hidden">
          
          {/* نشانگر گاز CO2 آزادشده */}
          {(stage === 'reacting' || stage === 'completed') && (
            <div className="absolute top-4 right-4 flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-500/20 border border-purple-400/40 text-purple-300 text-xs font-bold animate-pulse">
              <Sparkles className="w-3.5 h-3.5" />
              <span>خروج گاز CO₂ ({co2Volume} ml)</span>
            </div>
          )}

          {/* نشانگر گرماگیر بودن و افت دما */}
          {(stage === 'reacting' || stage === 'completed') && (
            <div className="absolute top-4 left-4 flex items-center gap-1 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-400/40 text-blue-300 text-xs font-mono">
              <Thermometer className="w-3.5 h-3.5" />
              <span>ΔT ≈ -{tempDrop}°C (گرماگیر)</span>
            </div>
          )}

          {/* بشر شیشه‌ای آزمایشگاهی */}
          <div className="relative w-44 h-64 border-4 border-slate-400/70 border-t-0 rounded-b-3xl bg-slate-900/40 flex flex-col justify-end p-2 shadow-2xl mt-8">
            
            {/* خطوط درجه‌بندی میلی‌لیتر روی بشر */}
            <div className="absolute left-2 top-4 bottom-4 flex flex-col justify-between text-[9px] font-mono text-slate-500 select-none">
              <span>250ml —</span>
              <span>200ml —</span>
              <span>150ml —</span>
              <span>100ml —</span>
              <span>50ml —</span>
            </div>

            {/* پودر جوش‌شیرین در حال ریزش هنگام شروع */}
            {stage === 'reacting' && (
              <div className="absolute top-2 right-12 w-8 h-20 flex flex-col items-center pointer-events-none animate-in fade-in">
                <div className="w-2 h-2 rounded-full bg-white opacity-80 animate-ping" />
                <div className="w-1.5 h-12 bg-gradient-to-b from-white/90 to-transparent rounded-full opacity-70" />
              </div>
            )}

            {/* مایع سرکه داخل بشر */}
            {stage !== 'ready' && (
              <div
                className="w-full rounded-b-2xl bg-gradient-to-t from-amber-200/40 via-amber-100/25 to-transparent relative transition-all duration-700 overflow-hidden"
                style={{ height: `${Math.min(100, vinegarVolume * 0.9)}px` }}
              >
                {/* حباب‌های گاز فعال درون مایع */}
                {stage === 'reacting' &&
                  bubbles.map((b) => (
                    <div
                      key={b.id}
                      className="absolute rounded-full bg-white/70 border border-white shadow-sm animate-bounce"
                      style={{
                        left: `${b.left}%`,
                        bottom: '4px',
                        width: `${b.size}px`,
                        height: `${b.size}px`,
                        animationDuration: `${0.8 + b.delay}s`
                      }}
                    />
                  ))}
              </div>
            )}

            {/* ستون کف و حباب ناشی از فوران واکنش */}
            {(stage === 'reacting' || stage === 'completed') && (
              <div
                className="absolute bottom-2 left-2 right-2 rounded-b-2xl bg-gradient-to-t from-white/95 via-purple-100/90 to-white/70 border-t-2 border-purple-200/80 shadow-lg transition-all duration-1000 flex items-center justify-center overflow-hidden"
                style={{ height: `${foamLevel * 2}px` }}
              >
                <div className="w-full h-full flex flex-wrap gap-1 p-1 opacity-70">
                  {Array.from({ length: 30 }).map((_, i) => (
                    <div
                      key={i}
                      className="w-2.5 h-2.5 rounded-full bg-white/90 border border-slate-300"
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          <span className="text-xs font-bold text-slate-300 mt-3">بشر ۲۵۰ میلی‌لیتری آزمایشگاه</span>
        </div>

        {/* پنل تنظیمات پیشرفته و کنترل پارامترها */}
        <div className="lg:col-span-6 space-y-5">
          
          {/* اسلایدر حجم سرکه */}
          <div className="bg-slate-950/70 p-4 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-300 font-bold">حجم سرکه خوراکی (اسید استیک ۵٪):</span>
              <span className="font-mono text-purple-300 font-bold">{vinegarVolume} ml</span>
            </div>
            <input
              type="range"
              min="20"
              max="120"
              step="5"
              disabled={stage === 'reacting'}
              value={vinegarVolume}
              onChange={(e) => setVinegarVolume(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>۲۰ میلی‌لیتر (کم)</span>
              <span>۷۰ ml</span>
              <span>۱۲۰ میلی‌لیتر (زیاد)</span>
            </div>
          </div>

          {/* اسلایدر جرم جوش‌شیرین */}
          <div className="bg-slate-950/70 p-4 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-300 font-bold">جرم جوش‌شیرین (سدیم هیدروژن‌کربنات):</span>
              <span className="font-mono text-cyan-300 font-bold">{bakingSodaMass} g</span>
            </div>
            <input
              type="range"
              min="2"
              max="25"
              step="1"
              disabled={stage === 'reacting'}
              value={bakingSodaMass}
              onChange={(e) => setBakingSodaMass(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>۲ گرم (یک قاشق کوچک)</span>
              <span>۱۲ g</span>
              <span>۲۵ گرم (زیاد)</span>
            </div>
          </div>

          {/* محاسبات استوکیومتری در زمان واقعی */}
          <div className="grid grid-cols-2 gap-3 p-3.5 rounded-2xl bg-slate-950/50 border border-slate-800/80 text-xs">
            <div>
              <span className="text-slate-400 block text-[11px]">مول اسید استیک:</span>
              <span className="font-mono font-bold text-purple-300">{aceticMoles.toFixed(3)} mol</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[11px]">مول جوش‌شیرین:</span>
              <span className="font-mono font-bold text-cyan-300">{sodaMoles.toFixed(3)} mol</span>
            </div>
            <div className="col-span-2 pt-2 border-t border-slate-800/60 flex items-center justify-between">
              <span className="text-slate-400 text-[11px]">محدودکننده واکنش:</span>
              <span className="font-bold text-amber-300">
                {limitingReagent || (sodaMoles <= aceticMoles ? 'جوش‌شیرین' : 'سرکه')}
              </span>
            </div>
          </div>

          {/* دکمه‌های اجرای گام‌به‌گام */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            {stage === 'ready' && (
              <button
                onClick={handlePourVinegar}
                className="flex-1 py-3 px-5 rounded-2xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-purple-600/30"
              >
                <Beaker className="w-4 h-4" />
                <span>۱. ریختن سرکه در بشر</span>
              </button>
            )}

            {stage === 'vinegar_poured' && (
              <button
                onClick={handleStartReaction}
                className="flex-1 py-3 px-5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-emerald-600/30 animate-pulse"
              >
                <Play className="w-4 h-4" />
                <span>۲. افزودن جوش‌شیرین و شروع واکنش</span>
              </button>
            )}

            {(stage === 'reacting' || stage === 'completed') && (
              <button
                onClick={handleReset}
                className="py-3 px-5 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs flex items-center justify-center gap-2 transition-all border border-slate-700"
              >
                <RefreshCw className="w-4 h-4" />
                <span>تنظیم مجدد آزمایش</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* بخش آموزشی پداگوژیک: چه چیزی یاد گرفتیم؟ */}
      <div className="p-4 rounded-2xl bg-purple-950/30 border border-purple-500/20 text-xs space-y-2">
        <div className="flex items-center gap-2 font-bold text-purple-300">
          <Info className="w-4 h-4" />
          <span>چه چیزی از این آزمایش یاد گرفتیم؟ (مفاهیم برنامه درسی)</span>
        </div>
        <ul className="list-disc list-inside text-slate-300 space-y-1 text-[11px] leading-relaxed">
          <li>
            <strong>تولید گاز و تغییر شیمیایی:</strong> واکنش میان اسید استیک (سرکه) و سدیم هیدروژن‌کربنات (جوش‌شیرین) با جوشش شدید و تولید گاز کربن‌دی‌اکسید (CO₂) همراه است که با ایجاد کف و حباب مشاهده می‌شود.
          </li>
          <li>
            <strong>واکنش گرماگیر (Endothermic):</strong> در طی این واکنش مقداری گرما از محیط جذب می‌شود، بنابراین دمای محتویات ظرف چند درجه خنک‌تر می‌شود.
          </li>
          <li>
            <strong>مفهوم واکنش‌دهنده محدودکننده:</strong> هر کدام از دو ماده که مول کمتری داشته باشد، زودتر مصرف شده و پایان واکنش را رقم می‌زند.
          </li>
        </ul>
      </div>
    </div>
  )
}
export default VinegarReactionSimulation
