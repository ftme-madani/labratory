import React, { useState } from 'react'
import { Filter, AlertTriangle, Droplets, RefreshCw, Info } from 'lucide-react'
import { simulationService } from '../../services/simulationService'

interface WaterFiltrationProps {
  attemptId?: string | null
  onStepComplete?: (stepIndex: number, obs: string) => void
}

export const WaterFiltrationSimulation: React.FC<WaterFiltrationProps> = ({
  attemptId,
  onStepComplete
}) => {
  const [isFiltering, setIsFiltering] = useState<boolean>(false)
  const [progress, setProgress] = useState<number>(0)
  const [isCompleted, setIsCompleted] = useState<boolean>(false)
  const inletTurbidity = 250 // NTU
  const outletTurbidity = 12 // NTU

  const handleStartFiltration = async () => {
    setIsFiltering(true)
    setProgress(0)

    if (attemptId) {
      try {
        await simulationService.executeAction(attemptId, {
          action_type: 'POUR_DIRTY_WATER',
          source_id: 'turbid_water_beaker',
          target_id: 'plastic_bottle',
          parameters: { volume_ml: 200 }
        })
      } catch (e) {
        console.warn('Backend sync failed:', e)
      }
    }

    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsFiltering(false)
          setIsCompleted(true)
          if (onStepComplete) {
            onStepComplete(
              5,
              'تصفیه فیزیکی کامل شد: کدورت از ۲۵۰ NTU به ۱۲ NTU کاهش یافت، اما به دلیل وجود میکروب‌ها غیرقابل شرب است.'
            )
          }
          return 100
        }
        return prev + 10
      })
    }, 400)
  }

  const handleReset = () => {
    setIsFiltering(false)
    setProgress(0)
    setIsCompleted(false)
  }

  return (
    <div className="w-full bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl text-slate-100 space-y-6">
      
      {/* هدر آزمایش صافی آب */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Filter className="w-5 h-5" />
            </span>
            <h3 className="text-base font-black text-white">
              شبیه‌ساز ساخت صافی چندلایه آب و جداسازی مکانیکی ذرات معلق
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            علوم تجربی پایه هشتم | مخلوط‌ها و جداسازی مواد | تصفیه فیزیکی، کدورت‌سنجی و ایمنی زیستی
          </p>
        </div>

        {/* شاخص کدورت آب */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs font-mono">
          <span className="text-amber-400">ورودی: {inletTurbidity} NTU (کدر)</span>
          <span className="text-slate-600">→</span>
          <span className="text-emerald-400">خروجی: {outletTurbidity} NTU (زلال)</span>
        </div>
      </div>

      {/* هشدار علمی و بهداشتی بسیار مهم و قرمز */}
      <div className="p-4 rounded-2xl bg-rose-950/40 border-2 border-rose-500/50 flex items-start gap-3 text-xs shadow-lg">
        <span className="p-2 rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/30 shrink-0">
          <AlertTriangle className="w-5 h-5" />
        </span>
        <div className="space-y-1">
          <h4 className="font-bold text-rose-300 text-sm">
            هشدار علمی و ایمنی آزمایشگاهی: آب خروجی به هیچ‌وجه قابل شرب نیست!
          </h4>
          <p className="text-slate-300 leading-relaxed text-[11px]">
            این صافی فیزیکی تنها ذرات معلق، گل‌ولای و ناخالصی‌های درشت را به دام می‌اندازد. باکتری‌ها، ویروس‌ها، انگل‌ها و املاح شیمیایی محلول از میان منافذ پنبه و ماسه عبور می‌کنند. بنابراین آب تصفیه‌شده از نظر بهداشتی غیرقابل نوشیدن است و نیاز به ضدعفونی و جوشاندن دارد.
          </p>
        </div>
      </div>

      {/* ناحیه مرکزی */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        {/* ستون فیلتر گرافیکی */}
        <div className="lg:col-span-6 flex flex-col items-center justify-center p-6 bg-slate-950/60 rounded-2xl border border-slate-800 relative min-h-[400px]">
          
          {/* بطری وارونه تصفیه آب */}
          <div className="relative w-44 flex flex-col items-center">
            
            {/* قیف و بدنه بالایی بطری */}
            <div className="w-36 h-56 border-2 border-slate-500/80 rounded-t-3xl bg-slate-900/40 flex flex-col justify-between overflow-hidden shadow-2xl relative">
              
              {/* آب گل‌آلود در حال ریزش از بالا */}
              {isFiltering && (
                <div
                  className="absolute top-0 w-full bg-amber-900/70 border-b border-amber-700/80 transition-all duration-300"
                  style={{ height: `${Math.max(10, 40 - progress * 0.3)}px` }}
                />
              )}

              {/* لایه ۳ (بالا): شن درشت (Gravel) */}
              <div className="w-full h-16 bg-gradient-to-b from-stone-600 to-stone-700 border-b border-stone-800 flex flex-col items-center justify-center p-1 relative">
                <span className="text-[10px] font-bold text-stone-200">لایه شن درشت</span>
                <span className="text-[8px] text-stone-400">به‌دام‌انداختن ذرات درشت و خاشاک</span>
                {/* دانه‌های شن متحرک */}
                <div className="absolute inset-0 flex flex-wrap gap-1 p-1 opacity-40">
                  {Array.from({ length: 18 }).map((_, i) => (
                    <div key={i} className="w-2.5 h-2.5 rounded-sm bg-stone-900" />
                  ))}
                </div>
              </div>

              {/* لایه ۲ (میانی): ماسه ریز (Sand) */}
              <div className="w-full h-18 bg-gradient-to-b from-amber-200/60 to-amber-300/50 border-b border-amber-400/30 flex flex-col items-center justify-center p-1 relative">
                <span className="text-[10px] font-bold text-amber-950">لایه ماسه ریز</span>
                <span className="text-[8px] text-amber-900">به‌دام‌انداختن ذرات گل‌ولای ریز</span>
              </div>

              {/* لایه ۱ (پایین): پنبه متراکم (Cotton) */}
              <div className="w-full h-14 bg-gradient-to-b from-white/90 to-slate-200/95 flex flex-col items-center justify-center p-1 relative">
                <span className="text-[10px] font-bold text-slate-800">لایه پنبه فشرده</span>
                <span className="text-[8px] text-slate-500">جلوگیری از خروج ماسه و فیلتر نهایی</span>
              </div>
            </div>

            {/* دهانه خروجی بطری و قطرات زلال */}
            <div className="w-6 h-6 bg-slate-700 border border-slate-600 rounded-b-md flex justify-center relative">
              {isFiltering && (
                <div className="absolute top-6 w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              )}
            </div>

            {/* ظرف جمع‌آوری آب تصفیه‌شده در زیر دهانه */}
            <div className="w-28 h-20 border-2 border-slate-500/80 border-t-0 rounded-b-2xl bg-slate-900/60 mt-4 flex flex-col justify-end p-1.5 shadow-xl">
              <div
                className="w-full rounded-b-xl bg-gradient-to-t from-cyan-500/50 to-blue-400/40 transition-all duration-500 relative flex items-center justify-center"
                style={{ height: `${(progress / 100) * 50}px` }}
              >
                {progress > 20 && (
                  <span className="text-[8px] font-mono text-cyan-200">آب زلال (۱۲ NTU)</span>
                )}
              </div>
            </div>
          </div>

          <span className="text-xs font-bold text-slate-300 mt-2">
            ستون تصفیه فیزیکی چندلایه
          </span>
        </div>

        {/* پنل اطلاعات لایه‌ها و کنترل تصفیه */}
        <div className="lg:col-span-6 space-y-4">
          
          {/* مقایسه آب ورودی و خروجی */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-950/70 p-3.5 rounded-2xl border border-slate-800 space-y-1">
              <span className="text-slate-400 text-[11px] block">آب ورودی (گل‌آلود):</span>
              <span className="font-bold text-amber-400 text-xs">کدورت: ۲۵۰ NTU</span>
              <p className="text-[10px] text-slate-400">حاوی خاک، ماسه و ذرات معلق درشت</p>
            </div>

            <div className="bg-slate-950/70 p-3.5 rounded-2xl border border-slate-800 space-y-1">
              <span className="text-slate-400 text-[11px] block">آب خروجی (صاف‌شده):</span>
              <span className="font-bold text-emerald-400 text-xs">کدورت: ۱۲ NTU</span>
              <p className="text-[10px] text-slate-400">شفاف و زلال، اما غیرقابل شرب!</p>
            </div>
          </div>

          {/* ترتیب چیدمان مهندسی لایه‌ها */}
          <div className="bg-slate-950/70 p-4 rounded-2xl border border-slate-800 space-y-2">
            <span className="text-xs font-bold text-slate-300 block">ترتیب استاندارد چیدمان لایه‌های صافی:</span>
            
            <div className="space-y-1.5 text-xs">
              <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <span>۳. لایه بالا (شن درشت):</span>
                <span className="text-stone-300 font-bold">جداسازی آشغال‌ها و ذرات درشت</span>
              </div>
              <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <span>۲. لایه میانی (ماسه ریز):</span>
                <span className="text-amber-300 font-bold">جداسازی ذرات ریز معلق خاک</span>
              </div>
              <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <span>۱. لایه پایین (پنبه فشرده):</span>
                <span className="text-slate-200 font-bold">نگهداری ماسه و زلال‌سازی نهایی</span>
              </div>
            </div>
          </div>

          {/* پیشرفت تصفیه */}
          {isFiltering && (
            <div className="bg-slate-950/70 p-3.5 rounded-2xl border border-slate-800 space-y-2">
              <div className="flex justify-between text-xs font-bold">
                <span className="text-cyan-300">در حال تصفیه آب از میان لایه‌ها...</span>
                <span className="font-mono text-cyan-400">{progress}%</span>
              </div>
              <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* دکمه‌های اجرا و ریست */}
          <div className="flex items-center gap-3 pt-2">
            {!isFiltering && !isCompleted ? (
              <button
                onClick={handleStartFiltration}
                className="flex-1 py-3 px-5 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-600/30"
              >
                <Droplets className="w-4 h-4" />
                <span>ریختن آب گل‌آلود و آغاز تصفیه</span>
              </button>
            ) : (
              <button
                onClick={handleReset}
                className="flex-1 py-3 px-5 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs flex items-center justify-center gap-2 transition-all border border-slate-700"
              >
                <RefreshCw className="w-4 h-4" />
                <span>تنظیم مجدد صافی</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* بخش پداگوژیک: چه چیزی یاد گرفتیم؟ */}
      <div className="p-4 rounded-2xl bg-blue-950/30 border border-blue-500/20 text-xs space-y-2">
        <div className="flex items-center gap-2 font-bold text-blue-300">
          <Info className="w-4 h-4" />
          <span>چه چیزی از این آزمایش یاد گرفتیم؟ (مفاهیم تصفیه فیزیکی آب)</span>
        </div>
        <ul className="list-disc list-inside text-slate-300 space-y-1 text-[11px] leading-relaxed">
          <li>
            <strong>تصفیه مکانیکی تدریجی:</strong> با گذر آب از ذرات درشت (شن) به ذرات ریزتر (ماسه) و الیاف پنبه، ذرات معلق به دام می‌افتند و آب زلال می‌شود.
          </li>
          <li>
            <strong>تفاوت زلالی با سلامت میکروبی:</strong> زلال بودن ظاهر آب دلیلی بر پاکیزگی زیستی آن نیست. ویروس‌ها، باکتری‌ها و سموم محلول نیازمند کلرزنی، فیلترهای ممبران اسمز معکوس یا جوشاندن هستند.
          </li>
        </ul>
      </div>
    </div>
  )
}
export default WaterFiltrationSimulation
