import React from 'react'
import { FlaskConical, ShieldCheck, Cpu, Sparkles } from 'lucide-react'
import { useThemeStore } from '../../store/useThemeStore'

export const Footer: React.FC = () => {
  const { theme } = useThemeStore()
  const isLight = theme === 'light'

  return (
    <footer className={`w-full border-t text-xs mt-auto transition-colors duration-200 ${
      isLight
        ? 'border-slate-200 bg-white/80 text-slate-600'
        : 'border-slate-800/80 bg-slate-950 text-slate-400'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          
          <div className="md:col-span-2 space-y-3">
            <div className={`flex items-center gap-2 font-bold text-sm ${isLight ? 'text-slate-900' : 'text-white'}`}>
              <FlaskConical className={`w-4 h-4 ${isLight ? 'text-emerald-600' : 'text-cyan-400'}`} />
              <span>پروژهٔ کارشناسی مهندسی کامپیوتر</span>
            </div>
            <p className={`leading-relaxed max-w-md ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
              طراحی و پیاده‌سازی آزمایشگاه مجازی هوشمند و تعاملی برای آموزش آزمایش‌های علوم تجربی دوره متوسطه با موتور شبیه‌سازی قطعی و معلم‌یار صوتی هوشمند.
            </p>
            <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px]">
              <span className={`flex items-center gap-1 px-2.5 py-1 rounded-lg border font-medium ${
                isLight ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-slate-900 border-slate-800 text-emerald-400'
              }`}>
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                قواعد علمی معتبر و قطعی
              </span>
              <span className={`flex items-center gap-1 px-2.5 py-1 rounded-lg border font-medium ${
                isLight ? 'bg-sky-50 border-sky-200 text-sky-800' : 'bg-slate-900 border-slate-800 text-cyan-400'
              }`}>
                <Cpu className="w-3.5 h-3.5 text-sky-500" />
                فناوری PWA و دسترسی آفلاین
              </span>
              <span className={`flex items-center gap-1 px-2.5 py-1 rounded-lg border font-medium ${
                isLight ? 'bg-amber-50 border-amber-200 text-amber-800' : 'bg-slate-900 border-slate-800 text-amber-400'
              }`}>
                <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                معلم‌یار صوتی و هوشمند
              </span>
            </div>
          </div>

          <div>
            <h5 className={`font-bold mb-3 text-sm ${isLight ? 'text-slate-900' : 'text-slate-200'}`}>بخش‌های سامانه</h5>
            <ul className="space-y-2">
              <li><a href="/" className={`transition-colors ${isLight ? 'hover:text-sky-600' : 'hover:text-cyan-400'}`}>صفحه اصلی و ویژگی‌ها</a></li>
              <li><a href="/experiments" className={`transition-colors ${isLight ? 'hover:text-sky-600' : 'hover:text-cyan-400'}`}>کاتالوگ آزمایش‌های درسی</a></li>
              <li><a href="/dashboard" className={`transition-colors ${isLight ? 'hover:text-sky-600' : 'hover:text-cyan-400'}`}>داشبورد و سوابق دانش‌آموز</a></li>
              <li><a href="/teacher/dashboard" className={`transition-colors ${isLight ? 'hover:text-sky-600' : 'hover:text-cyan-400'}`}>تحلیل عملکرد در پنل معلم</a></li>
            </ul>
          </div>

          <div>
            <h5 className={`font-bold mb-3 text-sm ${isLight ? 'text-slate-900' : 'text-slate-200'}`}>انطباق آموزشی</h5>
            <ul className="space-y-2">
              <li className={isLight ? 'text-slate-600' : 'text-slate-400'}>علوم تجربی پایه هفتم، هشتم، نهم</li>
              <li className={isLight ? 'text-slate-600' : 'text-slate-400'}>شیمی و فیزیک پایه دهم و یازدهم</li>
              <li className={isLight ? 'text-slate-600' : 'text-slate-400'}>مبتنی بر استانداردهای کتب درسی ملی</li>
            </ul>
          </div>

        </div>

        <div className={`pt-6 border-t flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] ${
          isLight ? 'border-slate-200 text-slate-500' : 'border-slate-900 text-slate-500'
        }`}>
          <p>© تمامی حقوق محفوظ است — پیاده‌سازی شده برای پروژه پایانی کارشناسی مهندسی کامپیوتر</p>
          <div className="flex items-center gap-4">
            <span>نسخهٔ ۱.۰.۰ (PWA Ready)</span>
            <span>طراحی RTL و فارسی</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
