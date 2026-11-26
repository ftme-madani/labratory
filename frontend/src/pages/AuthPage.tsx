import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/useAuthStore'
import { authService } from '../services/authService'
import type { UserRole } from '../types/user'
import { Button, Input, Select, Card, CardHeader, CardContent, StatusAlert } from '../components/ui'
import { FlaskConical, GraduationCap, UserCircle, Lock, Mail, School, Sparkles } from 'lucide-react'

export const AuthPage: React.FC = () => {
  const navigate = useNavigate()
  const { login, loginWithCredentials } = useAuthStore()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [role, setRole] = useState<UserRole>('student')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form states
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [schoolName, setSchoolName] = useState('')
  const [grade, setGrade] = useState('هشتم')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      if (mode === 'login') {
        if (!email || !password) {
          setError('لطفاً ایمیل و کلمه عبور را وارد نمایید.')
          setLoading(false)
          return
        }
        const loggedInUser = await loginWithCredentials(email, password)
        setLoading(false)
        if (loggedInUser.role === 'teacher') {
          navigate('/teacher/dashboard')
        } else {
          navigate('/dashboard')
        }
      } else {
        if (!fullName || !email || !password) {
          setError('لطفاً تمامی فیلدهای الزامی را تکمیل کنید.')
          setLoading(false)
          return
        }
        const registeredUser = await authService.register({
          fullName,
          email,
          password,
          role,
          grade,
          schoolName
        })
        setLoading(false)
        if (registeredUser.role === 'teacher') {
          navigate('/teacher/dashboard')
        } else {
          navigate('/dashboard')
        }
      }
    } catch (err: any) {
      setError(err?.detail || err?.message || 'خطا در احراز هویت. لطفاً مجدداً تلاش کنید.')
      setLoading(false)
    }
  }

  const handleQuickDemo = async (selectedRole: UserRole) => {
    setLoading(true)
    await login(selectedRole)
    setLoading(false)
    if (selectedRole === 'teacher') {
      navigate('/teacher/dashboard')
    } else {
      navigate('/dashboard')
    }
  }

  return (
    <div className="max-w-md mx-auto px-4 py-12 w-full space-y-6">
      
      {/* Brand Header */}
      <div className="text-center space-y-2">
        <div className="w-12 h-12 rounded-2xl bg-cyan-950 border border-cyan-500/40 mx-auto flex items-center justify-center text-cyan-400 shadow-lg">
          <FlaskConical className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-black text-white">
          {mode === 'login' ? 'ورود به آزمایشگاه مجازی' : 'ثبت‌نام کاربر جدید'}
        </h1>
        <p className="text-xs text-slate-400">
          سامانه هوشمند آموزش تجربی علوم دوره متوسطه اول و دوم
        </p>
      </div>

      {/* Main Card */}
      <Card className="border-slate-800 bg-slate-900/90 shadow-2xl">
        <CardHeader className="flex flex-col gap-4">
          
          {/* Mode Switcher: Login vs Register */}
          <div className="flex w-full rounded-xl bg-slate-950 p-1 border border-slate-800 text-xs">
            <button
              type="button"
              onClick={() => {
                setMode('login')
                setError(null)
              }}
              className={`flex-1 py-2 font-bold rounded-lg transition-all ${
                mode === 'login'
                  ? 'bg-cyan-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              ورود به حساب
            </button>
            <button
              type="button"
              onClick={() => {
                setMode('register')
                setError(null)
              }}
              className={`flex-1 py-2 font-bold rounded-lg transition-all ${
                mode === 'register'
                  ? 'bg-cyan-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              ثبت‌نام جدید
            </button>
          </div>

          {/* Role Switcher: Student vs Teacher */}
          <div className="flex w-full gap-2 text-xs">
            <button
              type="button"
              onClick={() => setRole('student')}
              className={`flex-1 p-2.5 rounded-xl border flex items-center justify-center gap-1.5 transition-all ${
                role === 'student'
                  ? 'bg-blue-950/80 border-blue-500 text-cyan-300 ring-1 ring-blue-500'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              <UserCircle className="w-4 h-4" />
              <span>دانش‌آموز</span>
            </button>
            <button
              type="button"
              onClick={() => setRole('teacher')}
              className={`flex-1 p-2.5 rounded-xl border flex items-center justify-center gap-1.5 transition-all ${
                role === 'teacher'
                  ? 'bg-blue-950/80 border-blue-500 text-cyan-300 ring-1 ring-blue-500'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              <GraduationCap className="w-4 h-4" />
              <span>دبیر / معلم</span>
            </button>
          </div>

        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <StatusAlert type="error" title="خطای ورودی">
                {error}
              </StatusAlert>
            )}

            {mode === 'register' && (
              <>
                <Input
                  label="نام و نام خانوادگی"
                  placeholder="مثلاً: علیرضا احمدی"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  rightIcon={<UserCircle className="w-4 h-4" />}
                  required
                />
                <Input
                  label="نام مدرسه / آموزشگاه"
                  placeholder="مثلاً: دبیرستان شهید بهشتی"
                  value={schoolName}
                  onChange={(e) => setSchoolName(e.target.value)}
                  rightIcon={<School className="w-4 h-4" />}
                />
                {role === 'student' && (
                  <Select
                    label="پایه تحصیلی"
                    value={grade}
                    onChange={(e) => setGrade(e.target.value)}
                    options={[
                      { value: 'هفتم', label: 'پایه هفتم' },
                      { value: 'هشتم', label: 'پایه هشتم' },
                      { value: 'نهم', label: 'پایه نهم' },
                      { value: 'دهم', label: 'پایه دهم' }
                    ]}
                  />
                )}
              </>
            )}

            <Input
              label="پست الکترونیک (ایمیل)"
              type="email"
              placeholder="name@school.ir"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              rightIcon={<Mail className="w-4 h-4" />}
              required
            />

            <Input
              label="کلمه عبور"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              rightIcon={<Lock className="w-4 h-4" />}
              required
            />

            <Button
              type="submit"
              variant="cyan"
              size="md"
              className="w-full mt-2"
              isLoading={loading}
            >
              {mode === 'login' ? 'ورود به سامانه' : 'تکمیل و ایجاد حساب'}
            </Button>
          </form>

          {/* Quick Demo Access Bar */}
          <div className="pt-6 border-t border-slate-800/80 mt-6 space-y-2">
            <span className="text-[11px] text-slate-400 block text-center">
              دسترسی سریع آزمایشی برای داوران و ارزیابان پایان‌نامه:
            </span>
            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="flex-1 text-xs"
                onClick={() => handleQuickDemo('student')}
                rightIcon={<Sparkles className="w-3.5 h-3.5 text-cyan-400" />}
              >
                ورود دمو دانش‌آموز
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="flex-1 text-xs"
                onClick={() => handleQuickDemo('teacher')}
                rightIcon={<GraduationCap className="w-3.5 h-3.5 text-indigo-400" />}
              >
                ورود دمو دبیر
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

    </div>
  )
}
