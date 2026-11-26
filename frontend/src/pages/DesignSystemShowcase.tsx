import React, { useState } from 'react'
import {
  Button,
  Badge,
  Card,
  CardHeader,
  CardContent,
  Input,
  Select,
  Modal,
  StatusAlert,
  Skeleton,
  EmptyState
} from '../components/ui'
import {
  FlaskConical,
  Atom,
  Flame,
  Zap,
  TestTube,
  Beaker,
  Sparkles,
  HelpCircle,
  RotateCcw,
  Play,
  Layers,
  Search,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react'

export const DesignSystemShowcase: React.FC = () => {
  const [modalOpen, setModalOpen] = useState(false)
  const [btnLoading, setBtnLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'tokens' | 'components' | 'lab-preview'>('tokens')
  const [selectedTool, setSelectedTool] = useState<string | null>('litmus_red')
  const [hintLevel, setHintLevel] = useState<1 | 2 | 3>(1)
  const [activeAlert, setActiveAlert] = useState<'success' | 'warning' | 'error' | 'hint'>('hint')

  const triggerLoading = () => {
    setBtnLoading(true)
    setTimeout(() => setBtnLoading(false), 1800)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full space-y-12">
      
      {/* Hero Header */}
      <div className="relative rounded-3xl p-8 sm:p-12 overflow-hidden border border-cyan-500/20 bg-gradient-to-br from-slate-900 via-slate-900/90 to-blue-950/60 shadow-2xl">
        <div className="absolute top-0 left-0 w-full h-full lab-grid-bg opacity-40 pointer-events-none" />
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>سیستم طراحی اختصاصی آزمایشگاه مجازی (Design System v1.0)</span>
          </div>
          
          <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
            هویت بصری، توکن‌های علمی و مؤلفه‌های تعاملی
          </h1>
          
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            طراحی مهندسی‌شده با پالت رنگی علمی (سرمه‌ای تیره، فیروزه‌ای کنترل‌شده و آبی آکادمیک)، تایپوگرافی استاندارد وزیرمتن، چیدمان ۱۰۰٪ راست‌چین (RTL) و دسترس‌پذیری کامل برای دانش‌آموزان و معلمان دوره متوسطه.
          </p>

          {/* Navigation Tabs */}
          <div className="flex flex-wrap gap-2 pt-4">
            <Button
              variant={activeTab === 'tokens' ? 'cyan' : 'secondary'}
              size="sm"
              onClick={() => setActiveTab('tokens')}
              rightIcon={<Layers className="w-4 h-4" />}
            >
              توکن‌های طراحی و رنگ‌ها
            </Button>
            <Button
              variant={activeTab === 'components' ? 'cyan' : 'secondary'}
              size="sm"
              onClick={() => setActiveTab('components')}
              rightIcon={<Atom className="w-4 h-4" />}
            >
              کامپوننت‌های پایه و وضعیت‌ها
            </Button>
            <Button
              variant={activeTab === 'lab-preview' ? 'cyan' : 'secondary'}
              size="sm"
              onClick={() => setActiveTab('lab-preview')}
              rightIcon={<FlaskConical className="w-4 h-4" />}
            >
              پیش‌نمایش تعاملی محیط آزمایشگاه
            </Button>
          </div>
        </div>
      </div>

      {/* TAB 1: DESIGN TOKENS & TYPOGRAPHY */}
      {activeTab === 'tokens' && (
        <section className="space-y-8 animate-in fade-in duration-200">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">۱. پالت رنگی علمی و معنایی (Scientific Palette)</h2>
            <p className="text-sm text-slate-400">
              ترکیب سرمه‌ای عمیق جهت تمرکز دانش‌آموز، سطوح فیروزه‌ای جهت جلب توجه آموزشی و رنگ‌های کنتراست‌بالا برای وضعیت‌های شبیه‌سازی:
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
            {[
              { name: 'سرمه‌ای عمیق', hex: '#040D1A', bg: 'bg-[#040D1A]', border: 'border-slate-700', text: 'text-white', role: 'پس‌زمینه اصلی' },
              { name: 'سرمه‌ای آزمایشگاه', hex: '#0B192C', bg: 'bg-[#0B192C]', border: 'border-slate-700', text: 'text-white', role: 'سطوح کارت‌ها' },
              { name: 'آبی کبالت', hex: '#1E3E62', bg: 'bg-[#1E3E62]', border: 'border-slate-600', text: 'text-white', role: 'خطوط مرزی و هدرها' },
              { name: 'فیروزه‌ای علمی', hex: '#00D2FC', bg: 'bg-[#00D2FC]', border: 'border-cyan-300', text: 'text-slate-950', role: 'نشانگر و آیکون فعال' },
              { name: 'تیل آزمایشگاهی', hex: '#2DD4BF', bg: 'bg-[#2DD4BF]', border: 'border-teal-300', text: 'text-slate-950', role: 'گام فعال' },
              { name: 'زمردی تایید', hex: '#10B981', bg: 'bg-[#10B981]', border: 'border-emerald-300', text: 'text-slate-950', role: 'نتیجه موفق و معتبر' },
              { name: 'رز هشدار خطر', hex: '#F43F5E', bg: 'bg-[#F43F5E]', border: 'border-rose-300', text: 'text-white', role: 'خطای علمی / نقض پیش‌نیاز' }
            ].map((color) => (
              <div key={color.hex} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-3 flex flex-col gap-2">
                <div className={`h-16 w-full rounded-xl ${color.bg} ${color.border} border flex items-center justify-center font-mono text-xs font-bold ${color.text} shadow-inner`}>
                  {color.hex}
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-200">{color.name}</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5">{color.role}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Typography Scale */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-bold text-white">۲. مقیاس تایپوگرافی فارسی (فونت استاندارد Vazirmatn)</h3>
              <Badge variant="cyan">۱۰۰٪ سازگار با مرورگرها و RTL</Badge>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-b border-slate-800/80 pb-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <span className="text-2xl sm:text-3xl font-extrabold text-white">تیتر بزرگ: آزمایش اسید، باز و شناساگرها</span>
                <span className="text-xs font-mono text-slate-400">Display / Extrabold (28-32px)</span>
              </div>
              <div className="border-b border-slate-800/80 pb-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <span className="text-xl font-bold text-slate-200">تیتر بخش: وسایل و مواد مورد نیاز در پایه هشتم</span>
                <span className="text-xs font-mono text-slate-400">Heading / Bold (20px)</span>
              </div>
              <div className="border-b border-slate-800/80 pb-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <span className="text-base font-medium text-slate-300">متن بدنه: کاغذ تورنسل را درون لوله آزمایش فرو ببرید و تغییر رنگ آن را ثبت کنید.</span>
                <span className="text-xs font-mono text-slate-400">Body / Regular (16px)</span>
              </div>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <span className="text-xs text-slate-400">زیرنویس و فراداده: منبع: کتاب علوم تجربی هشتم، فصل دوم، صفحه ۱۶.</span>
                <span className="text-xs font-mono text-slate-400">Caption / Light (12px)</span>
              </div>
            </CardContent>
          </Card>
        </section>
      )}

      {/* TAB 2: UI COMPONENTS & STATES */}
      {activeTab === 'components' && (
        <section className="space-y-8 animate-in fade-in duration-200">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">کامپوننت‌های پایه، تعاملی و وضعیت‌ها</h2>
            <p className="text-sm text-slate-400">
              شامل انواع دکمه‌ها، نشان‌ها، ورودی‌ها، مدال، اسکلت لودینگ و اعلان‌های وضعیت:
            </p>
          </div>

          {/* Buttons Matrix */}
          <Card>
            <CardHeader>
              <h3 className="text-base font-bold text-white">دکمه‌ها و حالت‌های کنشی (Buttons)</h3>
              <Button size="sm" variant="outline" onClick={triggerLoading}>
                تست حالت لودینگ
              </Button>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3 items-center">
                <Button variant="cyan" isLoading={btnLoading} rightIcon={<Play className="w-4 h-4" />}>
                  شروع آزمایش (Cyan)
                </Button>
                <Button variant="primary" isLoading={btnLoading} rightIcon={<Sparkles className="w-4 h-4" />}>
                  درخواست راهنمایی (Primary)
                </Button>
                <Button variant="secondary" isLoading={btnLoading} rightIcon={<RotateCcw className="w-4 h-4" />}>
                  بازنشانی (Secondary)
                </Button>
                <Button variant="outline" isLoading={btnLoading}>
                  مشاهده جزئیات (Outline)
                </Button>
                <Button variant="danger" isLoading={btnLoading} rightIcon={<AlertTriangle className="w-4 h-4" />}>
                  حذف مرحله (Danger)
                </Button>
                <Button variant="ghost" disabled>
                  غیرفعال (Disabled)
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Badges Matrix */}
          <Card>
            <CardHeader>
              <h3 className="text-base font-bold text-white">نشان‌ها و سطوح دشواری و موضوعات (Badges)</h3>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2.5">
                <Badge variant="cyan" icon={<Atom className="w-3.5 h-3.5" />}>علوم هشتم</Badge>
                <Badge variant="blue" icon={<FlaskConical className="w-3.5 h-3.5" />}>شیمی دهم</Badge>
                <Badge variant="emerald" icon={<CheckCircle2 className="w-3.5 h-3.5" />}>سطح آسان</Badge>
                <Badge variant="amber" icon={<Flame className="w-3.5 h-3.5" />}>سطح متوسط</Badge>
                <Badge variant="rose" icon={<Zap className="w-3.5 h-3.5" />}>سطح پیشرفته</Badge>
                <Badge variant="indigo" icon={<Sparkles className="w-3.5 h-3.5" />}>راهنمای سطح ۱</Badge>
                <Badge variant="slate">منبع: کتاب مصوب</Badge>
              </div>
            </CardContent>
          </Card>

          {/* Status Alerts */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white">اعلان‌های وضعیت بازخورد علمی (Feedback States)</h3>
              <div className="flex gap-1">
                {(['hint', 'success', 'warning', 'error'] as const).map((type) => (
                  <Button
                    key={type}
                    size="sm"
                    variant={activeAlert === type ? 'cyan' : 'ghost'}
                    onClick={() => setActiveAlert(type)}
                  >
                    {type === 'hint' ? 'راهنما' : type === 'success' ? 'موفقیت' : type === 'warning' ? 'هشدار' : 'خطا'}
                  </Button>
                ))}
              </div>
            </div>

            {activeAlert === 'hint' && (
              <StatusAlert
                type="hint"
                title="راهنمای هوشمند سطح ۱ (پرسش تفکری)"
                action={
                  <Button size="sm" variant="cyan" onClick={() => setModalOpen(true)}>
                    جزئیات راهنما
                  </Button>
                }
              >
                به نظر شما آیا برای تشخیص اسید و باز، استفاده از کاغذ تورنسل پیش از حل کردن ماده در آب مجاز است؟ به خاصیت یونیزاسیون توجه کنید.
              </StatusAlert>
            )}

            {activeAlert === 'success' && (
              <StatusAlert type="success" title="پدیده علمی ثبت شد">
                کاغذ تورنسل آبی پس از تماس با اسید کلریدریک رقیق بلافاصله به رنگ سرخ درآمد ($pH \approx 2.5$).
              </StatusAlert>
            )}

            {activeAlert === 'warning' && (
              <StatusAlert type="warning" title="پیش‌نیاز رعایت نشده است">
                قبل از ریختن ماده در لوله آزمایش، لازم است لوله آزمایش را با پیپت آب‌مقطر شست‌وشو دهید تا غلظت دقیق بماند.
              </StatusAlert>
            )}

            {activeAlert === 'error' && (
              <StatusAlert type="error" title="وسیله نامناسب انتخاب شد">
                استفاده از دماسنج شیشه‌ای به عنوان میله همزن (استیرر) مجاز نیست زیرا خطر شکستن و نشت جیوه دارد.
              </StatusAlert>
            )}
          </div>

          {/* Input & Form Controls */}
          <Card>
            <CardHeader>
              <h3 className="text-base font-bold text-white">کنترل‌های فرم و فیلترها (Form Controls)</h3>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input
                label="جستجوی آزمایش"
                placeholder="مثلاً: اسید و باز، قانون اهم..."
                rightIcon={<Search className="w-4 h-4" />}
                helperText="جستجو بر اساس عنوان، ابزار یا مبحث کتاب درسی"
              />
              <Select
                label="انتخاب پایه تحصیلی"
                options={[
                  { value: 'all', label: 'تمامی پایه‌ها' },
                  { value: '7', label: 'پایه هفتم' },
                  { value: '8', label: 'پایه هشتم' },
                  { value: '9', label: 'پایه نهم' },
                  { value: '10', label: 'پایه دهم (شیمی/فیزیک)' }
                ]}
              />
              <Input
                label="حجم محلول (میلی‌لیتر)"
                type="number"
                defaultValue={25}
                rightIcon={<Beaker className="w-4 h-4" />}
                error=""
              />
            </CardContent>
          </Card>

          {/* Skeleton & Empty State Preview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <h3 className="text-sm font-bold text-white">حالت لودینگ اسکلتی (Skeleton Loading)</h3>
              </CardHeader>
              <CardContent className="space-y-3">
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
                <div className="flex gap-2 pt-2">
                  <Skeleton className="h-8 w-20 rounded-lg" />
                  <Skeleton className="h-8 w-24 rounded-lg" />
                </div>
              </CardContent>
            </Card>

            <EmptyState
              title="آزمایشی در این دسته یافت نشد"
              description="می‌توانید فیلترهای جستجو را بازنشانی کرده یا با کلیدواژهٔ دیگری امتحان نمایید."
              action={<Button variant="outline" size="sm">بازنشانی فیلترها</Button>}
            />
          </div>
        </section>
      )}

      {/* TAB 3: VIRTUAL LAB WORKBENCH PREVIEW */}
      {activeTab === 'lab-preview' && (
        <section className="space-y-6 animate-in fade-in duration-200">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h2 className="text-2xl font-black text-white">محیط اختصاصی آزمایشگاه مجازی (Virtual Workbench)</h2>
                <Badge variant="cyan">پیش‌نمایش تعاملی</Badge>
              </div>
              <p className="text-xs text-slate-400">
                طراحی مجزا از صفحات عمومی: میز کار با شبکه هدایت‌گر، قفسه ابزارها، ردیاب مراحل و پانل هوشمند
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setSelectedTool(null)
                  setHintLevel(1)
                }}
                rightIcon={<RotateCcw className="w-3.5 h-3.5" />}
              >
                بازنشانی میز
              </Button>
              <Button
                variant="cyan"
                size="sm"
                onClick={() => setModalOpen(true)}
                rightIcon={<HelpCircle className="w-3.5 h-3.5" />}
              >
                راهنمای آموزشی (سطح {hintLevel})
              </Button>
            </div>
          </div>

          {/* Step Progress Tracker */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-4">
            <div className="flex items-center justify-between text-xs mb-2">
              <span className="font-bold text-slate-200">پیشرفت مرحلهٔ فعال: مرحله ۱ از ۳</span>
              <span className="font-mono text-cyan-400">۳۳٪ تکمیل شده</span>
            </div>
            <div className="w-full h-2.5 rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-400 transition-all duration-500 rounded-full"
                style={{ width: '33%' }}
              />
            </div>
            <div className="flex items-center gap-2 mt-3 text-xs text-slate-300">
              <span className="w-5 h-5 rounded-full bg-cyan-500 text-slate-950 font-bold flex items-center justify-center text-[10px]">
                ۱
              </span>
              <span>مرحله جاری: انتخاب شناساگر و آغشته کردن آن به محلول مجهول (آب‌لیمو)</span>
            </div>
          </div>

          {/* Workbench Grid Layout: Inventory + Workbench Surface */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            
            {/* Tool Inventory Shelf (Right Column in RTL) */}
            <div className="lg:col-span-1 rounded-2xl border border-slate-800 bg-slate-900/80 p-4 flex flex-col gap-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                  <Beaker className="w-4 h-4 text-cyan-400" />
                  قفسه وسایل و مواد
                </span>
                <span className="text-[10px] text-slate-400">کلیک یا کشیدن</span>
              </div>

              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: 'litmus_red', name: 'کاغذ تورنسل قرمز', icon: <TestTube className="w-5 h-5 text-rose-400" /> },
                  { id: 'litmus_blue', name: 'کاغذ تورنسل آبی', icon: <TestTube className="w-5 h-5 text-blue-400" /> },
                  { id: 'lemon_juice', name: 'بشر آب‌لیمو', icon: <Beaker className="w-5 h-5 text-amber-400" /> },
                  { id: 'soap_water', name: 'بشر آب‌صابون', icon: <Beaker className="w-5 h-5 text-teal-400" /> },
                  { id: 'pipette', name: 'پیپت آزمایشگاهی', icon: <TestTube className="w-5 h-5 text-slate-300" /> },
                  { id: 'stirrer', name: 'همزن شیشه‌ای', icon: <FlaskConical className="w-5 h-5 text-slate-400" /> }
                ].map((tool) => {
                  const isSelected = selectedTool === tool.id
                  return (
                    <button
                      key={tool.id}
                      onClick={() => setSelectedTool(tool.id)}
                      className={`p-3 rounded-xl border text-right transition-all flex flex-col items-center justify-center gap-1.5 cursor-pointer ${
                        isSelected
                          ? 'border-cyan-400 bg-cyan-950/60 ring-2 ring-cyan-500/30 text-white shadow-lg shadow-cyan-950/50'
                          : 'border-slate-800 bg-slate-900/40 hover:bg-slate-800/60 text-slate-300'
                      }`}
                    >
                      {tool.icon}
                      <span className="text-[11px] font-medium leading-tight text-center">{tool.name}</span>
                    </button>
                  )
                })}
              </div>

              <div className="mt-auto pt-3 border-t border-slate-800/80 text-[11px] text-slate-400 space-y-1">
                <p>💡 برای استفاده با کیبورد: از کلید Tab و Enter استفاده کنید.</p>
              </div>
            </div>

            {/* Interactive Lab Workspace Surface (Left 3 Columns in RTL) */}
            <div className="lg:col-span-3 rounded-3xl border border-cyan-500/30 bg-slate-950 relative overflow-hidden flex flex-col min-h-[460px] shadow-2xl">
              
              {/* Lab Bench Grid Background */}
              <div className="absolute inset-0 lab-grid-bg opacity-35" />

              {/* Workbench Header Bar */}
              <div className="relative z-10 px-5 py-3 border-b border-slate-800/80 bg-slate-900/60 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 text-cyan-300 font-bold">
                  <FlaskConical className="w-4 h-4" />
                  <span>میز کار آزمایشگاه شیمی — آزمایش ۱: شناسایی اسیدها و بازها</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="emerald" size="sm">دما: ۲۵°C</Badge>
                  <Badge variant="slate" size="sm">فشار: ۱ atm</Badge>
                </div>
              </div>

              {/* Lab Visual Interactive Zone */}
              <div className="relative z-10 flex-1 flex flex-col items-center justify-center p-8">
                
                {/* SVG Schematic Simulation Representation */}
                <div className="relative w-80 h-72 flex flex-col items-center justify-end">
                  
                  {/* Glass Beaker with Liquid */}
                  <div className="relative w-36 h-48 border-4 border-slate-500/60 border-t-0 rounded-b-3xl bg-slate-900/40 backdrop-blur-sm flex flex-col justify-end p-2 shadow-2xl">
                    
                    {/* Measurement markings on beaker */}
                    <div className="absolute right-2 top-8 flex flex-col gap-3 text-[9px] font-mono text-slate-400 select-none">
                      <span>- 100ml</span>
                      <span>- 75ml</span>
                      <span>- 50ml</span>
                      <span>- 25ml</span>
                    </div>

                    {/* Liquid fill */}
                    <div className="w-full h-28 rounded-b-2xl bg-gradient-to-t from-amber-600/70 to-amber-400/50 relative overflow-hidden transition-all duration-700">
                      <div className="absolute inset-0 opacity-20 bg-white animate-pulse" />
                      <div className="text-[10px] text-center font-bold text-amber-200 mt-2">
                        محلول آب‌لیمو ($pH \approx 2.5$)
                      </div>
                    </div>

                    {/* Litmus Strip dipping inside */}
                    {selectedTool === 'litmus_blue' && (
                      <div className="absolute top-2 left-12 w-6 h-36 bg-blue-500 border border-blue-400 shadow-md rounded-sm transition-all duration-500 animate-in slide-in-from-top-6">
                        {/* Red submerged tip showing real scientific reaction */}
                        <div className="absolute bottom-0 w-full h-16 bg-rose-500 border-t border-rose-400 transition-colors duration-500 flex items-center justify-center">
                          <span className="text-[7px] font-mono text-white rotate-90">سرخ شد</span>
                        </div>
                      </div>
                    )}

                    {selectedTool === 'litmus_red' && (
                      <div className="absolute top-2 left-12 w-6 h-36 bg-rose-500 border border-rose-400 shadow-md rounded-sm transition-all duration-500 animate-in slide-in-from-top-6">
                        <div className="absolute bottom-0 w-full h-16 bg-rose-500 flex items-center justify-center">
                          <span className="text-[7px] font-mono text-white rotate-90">تغییر نکرد</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Lab Bench Base Surface */}
                  <div className="w-full h-3 bg-gradient-to-r from-slate-800 via-slate-700 to-slate-800 rounded-full mt-3 shadow-lg border-t border-slate-600/40" />
                </div>

                {/* Live Observation Banner */}
                <div className="mt-4 max-w-lg w-full">
                  {selectedTool === 'litmus_blue' ? (
                    <StatusAlert type="success" title="مشاهده علمی معتبر">
                      کاغذ تورنسل آبی بلافاصله در تماس با اسید به رنگ سرخ درآمد؛ این نتیجه خصلت اسیدی آب‌لیمو را اثبات می‌کند.
                    </StatusAlert>
                  ) : selectedTool === 'litmus_red' ? (
                    <StatusAlert type="info" title="مشاهده علمی">
                      کاغذ تورنسل قرمز در محیط اسیدی تغییر رنگ نداد؛ برای تایید ماهیت اسیدی، از تورنسل آبی استفاده کنید.
                    </StatusAlert>
                  ) : (
                    <div className="text-center text-xs text-slate-400 bg-slate-900/80 border border-slate-800 rounded-xl p-3">
                      وسیله‌ای از قفسه انتخاب کنید تا اثر آن روی محلول شبیه‌سازی شود.
                    </div>
                  )}
                </div>
              </div>

              {/* Workbench Bottom Action Bar */}
              <div className="relative z-10 px-5 py-3 border-t border-slate-800/80 bg-slate-900/80 flex flex-wrap items-center justify-between gap-3 text-xs">
                <span className="text-slate-400">
                  وضعیت موتور شبیه‌سازی: <span className="text-emerald-400 font-bold">پایدار و معتبر</span>
                </span>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="cyan"
                    rightIcon={<CheckCircle2 className="w-4 h-4" />}
                    onClick={() => alert('مرحله با موفقیت تایید شد و داده در سوابق ثبت خواهد شد.')}
                  >
                    تایید و ثبت مشاهده
                  </Button>
                </div>
              </div>

            </div>

          </div>
        </section>
      )}

      {/* MODAL: INTELLIGENT HINT SYSTEM PREVIEW */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="راهنمای هوشمند آموزشی (سطوح سه‌گانه)"
        description="کمک به حل مسئله بر مبنای محتوای درسی مصوب و بدون افشای بی‌مورد پاسخ"
      >
        <div className="space-y-4 pt-2">
          
          {/* Level Switcher */}
          <div className="flex rounded-xl bg-slate-950 p-1 border border-slate-800">
            {([1, 2, 3] as const).map((lvl) => (
              <button
                key={lvl}
                onClick={() => setHintLevel(lvl)}
                className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all ${
                  hintLevel === lvl
                    ? 'bg-cyan-500 text-slate-950 shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                سطح {lvl}: {lvl === 1 ? 'سوال تفکری' : lvl === 2 ? 'سرنخ' : 'پاسخ کامل'}
              </button>
            ))}
          </div>

          {/* Level Content */}
          {hintLevel === 1 && (
            <div className="space-y-2 text-sm text-slate-300">
              <Badge variant="indigo">سطح ۱: تحریک تفکر</Badge>
              <p className="leading-relaxed">
                آیا می‌دانید کاغذ تورنسل آبی و قرمز هر کدام در چه محیطی (اسیدی، خنثی یا بازی) چه واکنشی نشان می‌دهند؟ ویژگی محلول آب‌لیمو از نظر طعم ترش چه ارتباطی با $pH$ دارد؟
              </p>
            </div>
          )}

          {hintLevel === 2 && (
            <div className="space-y-2 text-sm text-slate-300">
              <Badge variant="amber">سطح ۲: سرنخ مفهومی</Badge>
              <p className="leading-relaxed">
                آب‌لیمو حاوی اسید سیتریک است و $pH$ آن کمتر از ۷ است. شناساگر تورنسل آبی در برابر اسید به رنگ قرمز تبدیل می‌شود.
              </p>
            </div>
          )}

          {hintLevel === 3 && (
            <div className="space-y-2 text-sm text-slate-300">
              <Badge variant="cyan">سطح ۳: توضیح کامل و اقدام اصلاحی</Badge>
              <p className="leading-relaxed">
                برای اثبات اسیدی بودن آب‌لیمو، باید کاغذ تورنسل آبی را از قفسه انتخاب کرده و در بشر فرو ببرید. تغییر رنگ آن به سرخ، حضور یون‌های هیدرونیوم ($H^+$) را اثبات می‌کند.
              </p>
            </div>
          )}

          <div className="pt-3 border-t border-slate-800 flex justify-end gap-2">
            <Button variant="outline" size="sm" onClick={() => setModalOpen(false)}>
              متوجه شدم
            </Button>
            {hintLevel < 3 && (
              <Button
                variant="cyan"
                size="sm"
                onClick={() => setHintLevel((prev) => (prev + 1) as 1 | 2 | 3)}
              >
                نیاز به راهنمایی بیشتر (سطح {hintLevel + 1})
              </Button>
            )}
          </div>
        </div>
      </Modal>

    </div>
  )
}
