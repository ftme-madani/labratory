import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { experimentService } from '../services/experimentService'
import type { Experiment } from '../types/experiment'
import { ExperimentCard } from '../components/catalog/ExperimentCard'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { useThemeStore } from '../store/useThemeStore'
import {
  FlaskConical,
  ShieldCheck,
  Cpu,
  Sparkles,
  ArrowLeft,
  GraduationCap,
  CheckCircle2,
  Atom,
  HelpCircle,
  FileCheck2
} from 'lucide-react'

export const HomePage: React.FC = () => {
  const [featured, setFeatured] = useState<Experiment[]>([])
  const { theme } = useThemeStore()
  const isLight = theme === 'light'

  useEffect(() => {
    experimentService.getFeaturedExperiments().then(setFeatured)
  }, [])

  return (
    <div className="space-y-16 py-8">
      
      {/* 1. HERO SECTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className={`relative rounded-3xl p-8 sm:p-14 overflow-hidden border transition-all ${
          isLight
            ? 'border-slate-200/90 bg-gradient-to-br from-amber-50 via-white to-sky-50 shadow-xl shadow-slate-200/60'
            : 'border-purple-500/30 bg-gradient-to-br from-indigo-950 via-slate-900 to-purple-950/80 shadow-2xl shadow-indigo-950/50'
        }`}>
          <div className={`absolute inset-0 lab-grid-bg pointer-events-none ${isLight ? 'opacity-20' : 'opacity-40'}`} />
          
          <div className="relative z-10 max-w-3xl space-y-6">
            <div className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-bold shadow-sm ${
              isLight
                ? 'bg-amber-100 text-amber-900 border border-amber-300'
                : 'bg-indigo-900/60 border border-indigo-400/40 text-amber-300'
            }`}>
              <Sparkles className="w-3.5 h-3.5 text-amber-500 animate-spin [animation-duration:4s]" />
              <span>محیط شاد و تعاملی آزمایش‌های کتاب‌های علوم تجربی 🧪✨</span>
            </div>

            <h1 className={`text-3xl sm:text-5xl font-black leading-tight ${isLight ? 'text-slate-900' : 'text-white'}`}>
              آزمایشگاه مجازی و هوشمند
              <span className={`block text-transparent bg-clip-text mt-2 ${
                isLight
                  ? 'bg-gradient-to-l from-emerald-600 via-teal-600 to-sky-600'
                  : 'bg-gradient-to-l from-amber-300 via-teal-300 to-cyan-300'
              }`}>
                علوم تجربی دوره متوسطه اول و دوم
              </span>
            </h1>

            <p className={`text-sm sm:text-base leading-relaxed ${isLight ? 'text-slate-600' : 'text-slate-200'}`}>
              انجام مجازی و جذاب آزمایش‌های کتاب درسی همراه با معلم‌یار صوتی فارسی، وسایل واقعی آزمایشگاهی، امتیازدهی و بازخورد هوشمند؛ بدون خطر و بدون هزینه!
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <Link to="/experiments">
                <Button
                  variant="cyan"
                  size="lg"
                  leftIcon={<ArrowLeft className="w-5 h-5" />}
                  className="shadow-lg shadow-emerald-500/20 font-bold bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:from-emerald-600 hover:to-teal-700"
                >
                  شروع آزمایش و کاوش علمی 🚀
                </Button>
              </Link>
              <Link to="/teacher/dashboard">
                <Button
                  variant="outline"
                  size="lg"
                  rightIcon={<GraduationCap className="w-5 h-5" />}
                  className={`font-bold ${
                    isLight
                      ? 'border-slate-300 text-slate-700 hover:bg-slate-100'
                      : 'border-indigo-400/40 text-indigo-200 hover:bg-indigo-950/50'
                  }`}
                >
                  ورود به پنل تحلیلی معلم 🎓
                </Button>
              </Link>
            </div>

            {/* Micro-Features */}
            <div className={`pt-4 border-t grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs ${
              isLight ? 'border-slate-200 text-slate-600' : 'border-slate-800/80 text-slate-300'
            }`}>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                <span>۱۰۰٪ مبتنی بر کتب درسی</span>
              </div>
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-sky-500 shrink-0" />
                <span>موتور شبیه‌سازی قطعی</span>
              </div>
              <div className="flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-amber-500 shrink-0" />
                <span>راهنمای آموزشی ۳ سطحی</span>
              </div>
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-indigo-500 shrink-0" />
                <span>PWA و کارکرد آفلاین</span>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* 2. STATS & SCIENTIFIC PILLARS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            {
              title: 'قواعد علمی اثبات‌پذیر',
              desc: 'تمامی واکنش‌ها، تغییرات pH و مدارها با مدل‌های ریاضی و شیمیایی دقیق محاسبه می‌شوند.',
              icon: <Atom className={`w-6 h-6 ${isLight ? 'text-sky-600' : 'text-cyan-400'}`} />
            },
            {
              title: 'تطابق با کتب درسی ملی',
              desc: 'ارجاع مستقیم به فصل، شماره آزمایش و صفحه کتب علوم تجربی پایه هشتم، نهم و دهم.',
              icon: <FileCheck2 className={`w-6 h-6 ${isLight ? 'text-emerald-600' : 'text-emerald-400'}`} />
            },
            {
              title: 'راهنمای هوشمند چندمرحله‌ای',
              desc: 'از سوال تفکری تا اشاره مفهومی و در نهایت اقدام اصلاحی، متناسب با پیشرفت دانش‌آموز.',
              icon: <Sparkles className={`w-6 h-6 ${isLight ? 'text-amber-500' : 'text-amber-400'}`} />
            },
            {
              title: 'پنل اختصاصی پایش معلم',
              desc: 'تحلیل خطاهای پرتکرار کلاسی، ثبت زمان و دفعات درخواست راهنمایی برای هر آزمایش.',
              icon: <GraduationCap className={`w-6 h-6 ${isLight ? 'text-indigo-600' : 'text-blue-400'}`} />
            }
          ].map((item, idx) => (
            <div
              key={idx}
              className={`rounded-2xl border p-5 space-y-2 transition-all shadow-xs ${
                isLight
                  ? 'border-slate-200 bg-white text-slate-800 hover:border-sky-300 hover:shadow-md'
                  : 'border-slate-800 bg-slate-900/60 text-white hover:border-slate-700'
              }`}
            >
              <div className={`w-12 h-12 rounded-xl border flex items-center justify-center mb-3 ${
                isLight ? 'bg-slate-50 border-slate-200' : 'bg-slate-800/80 border-slate-700/60'
              }`}>
                {item.icon}
              </div>
              <h3 className={`text-sm font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>{item.title}</h3>
              <p className={`text-xs leading-relaxed ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 3. FEATURED EXPERIMENTS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <FlaskConical className={`w-5 h-5 ${isLight ? 'text-emerald-600' : 'text-cyan-400'}`} />
              <h2 className={`text-xl sm:text-2xl font-black ${isLight ? 'text-slate-900' : 'text-white'}`}>
                آزمایش‌های برجسته کتب درسی
              </h2>
            </div>
            <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              طراحی‌شده با ابزارها و مواد ایمن، مراحل استاندارد و تست‌های خودکار اعتبارسنجی
            </p>
          </div>

          <Link to="/experiments">
            <Button variant="outline" size="sm" leftIcon={<ArrowLeft className="w-4 h-4" />}>
              مشاهده تمامی آزمایش‌ها
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {featured.map((exp) => (
            <ExperimentCard key={exp.id} experiment={exp} />
          ))}
        </div>
      </section>

      {/* 4. WORKFLOW: HOW IT WORKS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className={`rounded-3xl border p-8 sm:p-12 space-y-8 shadow-xs ${
          isLight ? 'border-slate-200 bg-white' : 'border-slate-800 bg-slate-900/40'
        }`}>
          <div className="text-center max-w-xl mx-auto space-y-2">
            <Badge variant={isLight ? 'emerald' : 'cyan'}>فرآیند یادگیری تجربی</Badge>
            <h2 className={`text-xl sm:text-3xl font-black ${isLight ? 'text-slate-900' : 'text-white'}`}>
              چهار مرحله ساده برای یادگیری عمیق مفاهیم علمی
            </h2>
            <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              دانش‌آموز با انجام گام‌به‌گام و تصمیم‌گیری واقعی، آزمایش را تجربه می‌کند
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                step: '۱',
                title: 'انتخاب وسایل از قفسه',
                desc: 'بررسی ابزارها و مواد مورد نیاز آزمایش و انتقال آنها به میز کار تعاملی.'
              },
              {
                step: '۲',
                title: 'فرضیه‌سازی علمی',
                desc: 'پیش‌بینی نتیجه آزمایش قبل از اجرا جهت تقویت مهارت‌های تفکر نقادانه.'
              },
              {
                step: '۳',
                title: 'اجرای مرحله به مرحله',
                desc: 'مشاهده تغییرات واقعی، ثبت مشاهدات و دریافت راهنمای صوتی و مفهومی در صورت بروز خطا.'
              },
              {
                step: '۴',
                title: 'تحلیل و ارزیابی نهایی',
                desc: 'ارزیابی خودکار با بازخورد تفصیلی و ارسال نتایج به کارنامه دبیر کلاس.'
              }
            ].map((st, i) => (
              <div
                key={i}
                className={`p-6 rounded-2xl border space-y-3 relative ${
                  isLight ? 'bg-slate-50/80 border-slate-200 text-slate-800' : 'bg-slate-900/80 border-slate-800 text-white'
                }`}
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-400 to-yellow-500 text-slate-950 font-black text-sm flex items-center justify-center shadow-md shadow-amber-400/20">
                  {st.step}
                </div>
                <h4 className={`font-black text-sm ${isLight ? 'text-slate-900' : 'text-white'}`}>{st.title}</h4>
                <p className={`text-xs leading-relaxed ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>{st.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

    </div>
  )
}
