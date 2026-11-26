import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/useAuthStore'
import { useThemeStore } from '../../store/useThemeStore'
import { Button } from '../ui/Button'
import { Badge } from '../ui/Badge'
import {
  FlaskConical,
  BookOpen,
  LayoutDashboard,
  GraduationCap,
  Menu,
  X,
  Download,
  UserCircle,
  LogOut,
  Sparkles,
  Sun,
  Moon
} from 'lucide-react'

export const Navbar: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()
  const { user, isAuthenticated, logout } = useAuthStore()
  const { theme, toggleTheme } = useThemeStore()

  const navLinks = [
    { label: 'صفحه اصلی', to: '/', icon: <FlaskConical className="w-4 h-4" /> },
    { label: 'کاتالوگ آزمایش‌ها', to: '/experiments', icon: <BookOpen className="w-4 h-4" /> },
    { label: 'داشبورد دانش‌آموز', to: '/dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { label: 'پنل معلم', to: '/teacher/dashboard', icon: <GraduationCap className="w-4 h-4" /> }
  ]

  const isActive = (path: string) => {
    if (path === '/' && location.pathname !== '/') return false
    return location.pathname.startsWith(path)
  }

  const isLight = theme === 'light'

  return (
    <header className={`sticky top-0 z-40 w-full transition-colors duration-200 ${
      isLight
        ? 'border-b border-slate-200/90 bg-white/90 backdrop-blur-xl shadow-sm shadow-slate-200/60 text-slate-800'
        : 'border-b border-indigo-500/20 bg-slate-950/85 backdrop-blur-xl shadow-lg shadow-indigo-950/20 text-white'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand / Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-amber-400 via-emerald-400 to-sky-500 p-0.5 shadow-md shadow-sky-500/15 group-hover:scale-105 transition-transform">
            <div className={`w-full h-full rounded-[14px] flex items-center justify-center transition-colors ${
              isLight ? 'bg-white text-emerald-600' : 'bg-slate-950 text-amber-300'
            }`}>
              <FlaskConical className="w-5 h-5 group-hover:rotate-12 transition-transform duration-300" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className={`font-black text-base tracking-tight transition-colors ${
                isLight ? 'text-slate-900 group-hover:text-sky-600' : 'text-white group-hover:text-cyan-300'
              }`}>
                آزمایشگاه علوم تجربی
              </span>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold hidden sm:inline-flex items-center gap-1 ${
                isLight
                  ? 'bg-amber-100 text-amber-800 border border-amber-300'
                  : 'bg-gradient-to-r from-emerald-500/30 to-teal-500/30 text-emerald-300 border border-emerald-500/40'
              }`}>
                <Sparkles className="w-3 h-3 text-amber-500" />
                محیط شاداب دانش‌آموزی
              </span>
            </div>
            <span className={`text-[11px] hidden sm:block ${
              isLight ? 'text-slate-500' : 'text-indigo-300/80'
            }`}>
              آموزش تعاملی و عملی دوره اول و دوم متوسطه
            </span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1.5">
          {navLinks.map((link) => {
            const active = isActive(link.to)
            return (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm font-bold transition-all duration-150 ${
                  active
                    ? isLight
                      ? 'bg-sky-100/80 text-sky-800 border border-sky-300 shadow-sm'
                      : 'bg-gradient-to-r from-indigo-900/80 to-cyan-900/60 text-cyan-200 border border-cyan-400/40 shadow-inner'
                    : isLight
                    ? 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                {link.icon}
                <span>{link.label}</span>
              </Link>
            )
          })}
        </nav>

        {/* Action Controls & Theme Switcher */}
        <div className="flex items-center gap-2">
          
          {/* Day / Night Mode Toggle Button */}
          <button
            onClick={toggleTheme}
            type="button"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all duration-200 shadow-sm ${
              isLight
                ? 'bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 hover:border-amber-300'
                : 'bg-slate-800/90 hover:bg-slate-700 text-amber-300 border border-slate-700'
            }`}
            title={isLight ? 'تغییر به حالت شب' : 'تغییر به حالت روز (روشن و طبیعی)'}
            aria-label="تغییر حالت روز و شب"
          >
            {isLight ? (
              <>
                <Sun className="w-4 h-4 text-amber-500 animate-spin [animation-duration:12s]" />
                <span className="hidden sm:inline">حالت روز ☀️</span>
              </>
            ) : (
              <>
                <Moon className="w-4 h-4 text-cyan-300" />
                <span className="hidden sm:inline">حالت شب 🌙</span>
              </>
            )}
          </button>

          {isAuthenticated && user ? (
            <div className="hidden sm:flex items-center gap-2">
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs ${
                isLight
                  ? 'bg-slate-100 border border-slate-200 text-slate-700'
                  : 'bg-slate-900 border border-slate-800 text-slate-200'
              }`}>
                <UserCircle className={`w-4 h-4 ${isLight ? 'text-sky-600' : 'text-cyan-400'}`} />
                <span className="font-semibold truncate max-w-[120px]">{user.fullName}</span>
                <Badge variant={user.role === 'teacher' ? 'indigo' : 'emerald'} size="sm">
                  {user.role === 'teacher' ? 'دبیر' : 'دانش‌آموز'}
                </Badge>
              </div>
              <button
                onClick={logout}
                title="خروج از حساب"
                className={`p-2 rounded-xl transition-colors ${
                  isLight
                    ? 'text-slate-500 hover:text-rose-600 hover:bg-rose-50'
                    : 'text-slate-400 hover:text-rose-400 hover:bg-slate-800'
                }`}
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <Link to="/auth/login" className="hidden sm:inline-flex">
              <Button variant={isLight ? 'outline' : 'outline'} size="sm" rightIcon={<UserCircle className="w-4 h-4" />}>
                ورود / ثبت‌نام
              </Button>
            </Link>
          )}

          <Button
            variant="cyan"
            size="sm"
            className="hidden lg:inline-flex font-bold"
            rightIcon={<Download className="w-4 h-4" />}
            onClick={() => {
              alert('برای نصب نسخهٔ PWA در تلفن همراه یا مرورگر، از منوی مرورگر گزینه Add to Home Screen را انتخاب کنید.')
            }}
          >
            نصب PWA
          </Button>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="منوی اصلی"
            className={`md:hidden p-2 rounded-xl transition-colors ${
              isLight
                ? 'text-slate-700 hover:bg-slate-100'
                : 'text-slate-300 hover:text-white hover:bg-slate-800'
            }`}
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className={`md:hidden border-b px-4 pt-2 pb-5 space-y-1.5 animate-in slide-in-from-top-2 duration-150 ${
          isLight ? 'border-slate-200 bg-white shadow-lg' : 'border-slate-800 bg-slate-950/95'
        }`}>
          {navLinks.map((link) => {
            const active = isActive(link.to)
            return (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-bold ${
                  active
                    ? isLight
                      ? 'bg-sky-100 text-sky-800 border border-sky-300'
                      : 'bg-slate-800 text-cyan-300 border border-cyan-500/30'
                    : isLight
                    ? 'text-slate-700 hover:bg-slate-100'
                    : 'text-slate-300 hover:bg-slate-900'
                }`}
              >
                {link.icon}
                <span>{link.label}</span>
              </Link>
            )
          })}
          
          <div className={`pt-3 border-t flex flex-col gap-2 ${
            isLight ? 'border-slate-200' : 'border-slate-800/80'
          }`}>
            {isAuthenticated && user ? (
              <div className={`flex items-center justify-between p-2.5 rounded-xl text-xs ${
                isLight ? 'bg-slate-100 border border-slate-200' : 'bg-slate-900 border border-slate-800'
              }`}>
                <span className={`font-bold ${isLight ? 'text-slate-800' : 'text-white'}`}>
                  {user.fullName} ({user.role === 'teacher' ? 'دبیر' : 'دانش‌آموز'})
                </span>
                <button onClick={logout} className="text-rose-600 font-bold">خروج</button>
              </div>
            ) : (
              <Link to="/auth/login" onClick={() => setMobileMenuOpen(false)}>
                <Button variant="outline" size="sm" className="w-full">
                  ورود / ثبت‌نام
                </Button>
              </Link>
            )}
          </div>
        </div>
      )}
    </header>
  )
}
