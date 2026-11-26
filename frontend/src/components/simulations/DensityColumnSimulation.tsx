import React, { useState } from 'react'
import { Layers, Droplets, Info, RefreshCw, CheckCircle2 } from 'lucide-react'
import { simulationService } from '../../services/simulationService'

interface DensityColumnProps {
  attemptId?: string | null
  onStepComplete?: (stepIndex: number, obs: string) => void
}

export const DensityColumnSimulation: React.FC<DensityColumnProps> = ({
  attemptId,
  onStepComplete
}) => {
  const [honeyVol, setHoneyVol] = useState<number>(50) // ml (d = 1.42)
  const [waterVol, setWaterVol] = useState<number>(50) // ml (d = 1.00)
  const [oilVol, setOilVol] = useState<number>(50) // ml (d = 0.91)

  const [hasHoney, setHasHoney] = useState<boolean>(false)
  const [hasWater, setHasWater] = useState<boolean>(false)
  const [hasOil, setHasOil] = useState<boolean>(false)

  // چگالی‌های استاندارد کتاب درسی
  const honeyDensity = 1.42 // g/ml
  const waterDensity = 1.00 // g/ml
  const oilDensity = 0.91 // g/ml

  const honeyMass = (honeyVol * honeyDensity).toFixed(1)
  const waterMass = (waterVol * waterDensity).toFixed(1)
  const oilMass = (oilVol * oilDensity).toFixed(1)

  const totalVol = (hasHoney ? honeyVol : 0) + (hasWater ? waterVol : 0) + (hasOil ? oilVol : 0)
  const totalMass = (
    (hasHoney ? Number(honeyMass) : 0) +
    (hasWater ? Number(waterMass) : 0) +
    (hasOil ? Number(oilMass) : 0)
  ).toFixed(1)

  const handlePour = async (liquid: 'honey' | 'water' | 'oil') => {
    if (liquid === 'honey') {
      setHasHoney(true)
      if (attemptId) {
        try {
          await simulationService.executeAction(attemptId, {
            action_type: 'POUR_HONEY',
            source_id: 'honey_jar',
            target_id: 'graduated_cylinder',
            parameters: { volume_ml: honeyVol }
          })
        } catch (e) {
          console.warn('Backend sync failed:', e)
        }
      }
    } else if (liquid === 'water') {
      setHasWater(true)
      if (attemptId) {
        try {
          await simulationService.executeAction(attemptId, {
            action_type: 'POUR_WATER',
            source_id: 'water_beaker',
            target_id: 'graduated_cylinder',
            parameters: { volume_ml: waterVol }
          })
        } catch (e) {
          console.warn('Backend sync failed:', e)
        }
      }
    } else if (liquid === 'oil') {
      setHasOil(true)
      if (attemptId) {
        try {
          await simulationService.executeAction(attemptId, {
            action_type: 'POUR_OIL',
            source_id: 'oil_bottle',
            target_id: 'graduated_cylinder',
            parameters: { volume_ml: oilVol }
          })
        } catch (e) {
          console.warn('Backend sync failed:', e)
        }
      }
      if (onStepComplete) {
        onStepComplete(
          5,
          'تشکیل لایه‌های مجزای مایعات به دلیل تفاوت چگالی و امتزاج‌ناپذیری تایید شد: عسل در کف، آب در میانه و روغن در بالا.'
        )
      }
    }
  }

  const handleReset = () => {
    setHasHoney(false)
    setHasWater(false)
    setHasOil(false)
  }

  return (
    <div className="w-full bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl text-slate-100 space-y-6">
      
      {/* هدر آزمایش چگالی */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Layers className="w-5 h-5" />
            </span>
            <h3 className="text-base font-black text-white">
              شبیه‌ساز تشکیل ستون چگالی و بررسی امتزاج‌پذیری مایعات
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            علوم تجربی پایه هفتم | اندازه‌گیری در علوم | رابطه چگالی (d = m/V) و پایداری لایه‌ها
          </p>
        </div>

        {/* فرمول چگالی */}
        <div className="px-4 py-2 rounded-2xl bg-slate-950/80 border border-amber-500/30 text-xs font-mono text-amber-200 text-left dir-ltr shadow-inner">
          d = m / V &nbsp;(g/cm³)
        </div>
      </div>

      {/* ناحیه مرکزی */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        {/* استوانه مدرج گرافیکی */}
        <div className="lg:col-span-6 flex flex-col items-center justify-center p-6 bg-slate-950/60 rounded-2xl border border-slate-800 relative min-h-[380px]">
          
          {/* مشخصات جرم و حجم کلی */}
          <div className="absolute top-4 right-4 flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900/80 border border-slate-700 text-xs font-mono text-amber-300">
            <span>حجم کل: {totalVol} ml | جرم کل: {totalMass} g</span>
          </div>

          {/* استوانه مدرج شیشه‌ای */}
          <div className="relative w-36 h-72 border-4 border-slate-400/80 border-t-0 rounded-b-2xl bg-slate-900/50 flex flex-col justify-end p-1.5 shadow-2xl mt-6">
            
            {/* خطوط درجه‌بندی میلی‌لیتر */}
            <div className="absolute left-1 top-4 bottom-4 flex flex-col justify-between text-[8px] font-mono text-slate-500 select-none">
              <span>250 —</span>
              <span>200 —</span>
              <span>150 —</span>
              <span>100 —</span>
              <span>50 —</span>
            </div>

            {/* لایه روغن (بالاترین لایه - کمترین چگالی d = 0.91) */}
            {hasOil && (
              <div
                className="w-full bg-gradient-to-t from-amber-400/80 to-amber-300/70 border-b border-amber-200/50 relative flex items-center justify-center transition-all duration-700 shadow-sm"
                style={{ height: `${Math.min(80, oilVol * 0.9)}px` }}
              >
                <span className="text-[10px] font-bold text-amber-950 bg-amber-200/70 px-2 py-0.5 rounded-full shadow-sm">
                  روغن ({oilDensity} g/ml)
                </span>
              </div>
            )}

            {/* لایه آب (لایه میانی - چگالی میانی d = 1.00) */}
            {hasWater && (
              <div
                className="w-full bg-gradient-to-t from-cyan-600/70 to-blue-500/60 border-b border-cyan-300/40 relative flex items-center justify-center transition-all duration-700 shadow-sm"
                style={{ height: `${Math.min(80, waterVol * 0.9)}px` }}
              >
                <span className="text-[10px] font-bold text-white bg-blue-900/60 px-2 py-0.5 rounded-full shadow-sm">
                  آب ({waterDensity.toFixed(2)} g/ml)
                </span>
              </div>
            )}

            {/* لایه عسل (پایین‌ترین لایه - بیشترین چگالی d = 1.42) */}
            {hasHoney && (
              <div
                className="w-full rounded-b-xl bg-gradient-to-t from-amber-900/90 to-amber-700/85 relative flex items-center justify-center transition-all duration-700 shadow-inner"
                style={{ height: `${Math.min(80, honeyVol * 0.9)}px` }}
              >
                <span className="text-[10px] font-bold text-amber-100 bg-amber-950/70 px-2 py-0.5 rounded-full shadow-sm">
                  عسل ({honeyDensity} g/ml)
                </span>
              </div>
            )}

            {!hasHoney && !hasWater && !hasOil && (
              <div className="h-full flex items-center justify-center text-[11px] text-slate-500 text-center px-2">
                استوانه مدرج خالی است. مایعات را به ترتیب اضافه کنید.
              </div>
            )}
          </div>

          <span className="text-xs font-bold text-slate-300 mt-3">استوانه مدرج آزمایشگاه</span>
        </div>

        {/* پنل افزودن مایعات و اسلایدرها */}
        <div className="lg:col-span-6 space-y-4">
          
          {/* کارت ۱: عسل */}
          <div className="bg-slate-950/70 p-3.5 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-amber-400">۱. عسل غلیظ (چگالی: ۱.۴۲ g/ml):</span>
              <span className="font-mono text-slate-300">{honeyVol} ml | {honeyMass} g</span>
            </div>
            <input
              type="range"
              min="20"
              max="80"
              step="5"
              disabled={hasHoney}
              value={honeyVol}
              onChange={(e) => setHoneyVol(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-600"
            />
            <button
              onClick={() => handlePour('honey')}
              disabled={hasHoney}
              className={`w-full py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                hasHoney
                  ? 'bg-slate-800 text-emerald-400 border border-emerald-500/30'
                  : 'bg-amber-700 hover:bg-amber-600 text-white shadow-md'
              }`}
            >
              {hasHoney ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Droplets className="w-3.5 h-3.5" />}
              <span>{hasHoney ? 'عسل در کف ظرف قرار گرفت' : 'ریختن عسل در استوانه'}</span>
            </button>
          </div>

          {/* کارت ۲: آب */}
          <div className="bg-slate-950/70 p-3.5 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-cyan-400">۲. آب معمولی (چگالی: ۱.۰۰ g/ml):</span>
              <span className="font-mono text-slate-300">{waterVol} ml | {waterMass} g</span>
            </div>
            <input
              type="range"
              min="20"
              max="80"
              step="5"
              disabled={hasWater}
              value={waterVol}
              onChange={(e) => setWaterVol(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
            <button
              onClick={() => handlePour('water')}
              disabled={hasWater || !hasHoney}
              className={`w-full py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                hasWater
                  ? 'bg-slate-800 text-emerald-400 border border-emerald-500/30'
                  : !hasHoney
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-500 text-white shadow-md'
              }`}
            >
              {hasWater ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Droplets className="w-3.5 h-3.5" />}
              <span>{hasWater ? 'آب به عنوان لایه میانی اضافه شد' : 'افزودن آرام آب'}</span>
            </button>
          </div>

          {/* کارت ۳: روغن */}
          <div className="bg-slate-950/70 p-3.5 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-yellow-300">۳. روغن مایع خوراکی (چگالی: ۰.۹۱ g/ml):</span>
              <span className="font-mono text-slate-300">{oilVol} ml | {oilMass} g</span>
            </div>
            <input
              type="range"
              min="20"
              max="80"
              step="5"
              disabled={hasOil}
              value={oilVol}
              onChange={(e) => setOilVol(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-yellow-400"
            />
            <button
              onClick={() => handlePour('oil')}
              disabled={hasOil || !hasWater}
              className={`w-full py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                hasOil
                  ? 'bg-slate-800 text-emerald-400 border border-emerald-500/30'
                  : !hasWater
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-yellow-600 hover:bg-yellow-500 text-slate-950 shadow-md font-black'
              }`}
            >
              {hasOil ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Droplets className="w-3.5 h-3.5" />}
              <span>{hasOil ? 'روغن به عنوان لایه رویی اضافه شد' : 'افزودن روغن خوراکی'}</span>
            </button>
          </div>

          {/* دکمه ریست */}
          <button
            onClick={handleReset}
            className="w-full py-2 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs flex items-center justify-center gap-2 border border-slate-700"
          >
            <RefreshCw className="w-4 h-4" />
            <span>خالی کردن استوانه و آزمایش مجدد</span>
          </button>
        </div>
      </div>

      {/* بخش پداگوژیک: چه چیزی یاد گرفتیم؟ */}
      <div className="p-4 rounded-2xl bg-amber-950/30 border border-amber-500/20 text-xs space-y-2">
        <div className="flex items-center gap-2 font-bold text-amber-300">
          <Info className="w-4 h-4" />
          <span>چه چیزی از این آزمایش یاد گرفتیم؟ (مفاهیم چگالی و امتزاج‌پذیری)</span>
        </div>
        <ul className="list-disc list-inside text-slate-300 space-y-1 text-[11px] leading-relaxed">
          <li>
            <strong>تفاوت چگالی:</strong> مایع با بیشترین چگالی (عسل با ۱.۴۲ گرم بر سانتی‌متر مکعب) در پایین‌ترین سطح قرار می‌گیرد و مایع با کمترین چگالی (روغن با ۰.۹۱ گرم بر سانتی‌متر مکعب) بر روی سایرین شناور می‌ماند.
          </li>
          <li>
            <strong>نقش امتزاج‌ناپذیری (عدم انحلال):</strong> چگالی به تنهایی برای تشکیل لایه‌ها کافی نیست؛ برای مثال اگر الکل و آب با چگالی متفاوت اضافه شوند به سرعت در هم حل می‌شوند. روغن به دلیل ناقطبی بودن در آب قطبی حل نمی‌شود و مرز مشخصی تشکیل می‌دهد.
          </li>
        </ul>
      </div>
    </div>
  )
}
export default DensityColumnSimulation
