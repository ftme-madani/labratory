import React from 'react'
import { cn } from '../../utils/cn'
import { CheckCircle2, AlertTriangle, AlertCircle, Info, Sparkles } from 'lucide-react'

export interface StatusAlertProps {
  type?: 'success' | 'warning' | 'error' | 'info' | 'hint'
  title?: string
  children: React.ReactNode
  className?: string
  action?: React.ReactNode
}

export const StatusAlert: React.FC<StatusAlertProps> = ({
  type = 'info',
  title,
  children,
  className,
  action
}) => {
  const configs = {
    success: {
      container: 'bg-emerald-950/60 border-emerald-800/80 text-emerald-200',
      icon: <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />,
      titleColor: 'text-emerald-300'
    },
    warning: {
      container: 'bg-amber-950/60 border-amber-800/80 text-amber-200',
      icon: <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />,
      titleColor: 'text-amber-300'
    },
    error: {
      container: 'bg-rose-950/60 border-rose-800/80 text-rose-200 animate-shake',
      icon: <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />,
      titleColor: 'text-rose-300'
    },
    info: {
      container: 'bg-blue-950/60 border-blue-800/80 text-blue-200',
      icon: <Info className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />,
      titleColor: 'text-blue-300'
    },
    hint: {
      container: 'bg-indigo-950/60 border-indigo-700/80 text-indigo-200 shadow-md shadow-indigo-950/50',
      icon: <Sparkles className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />,
      titleColor: 'text-cyan-300'
    }
  }

  const current = configs[type]

  return (
    <div
      role="alert"
      className={cn(
        'rounded-xl border p-4 flex items-start gap-3 text-sm text-right transition-all',
        current.container,
        className
      )}
    >
      {current.icon}
      <div className="flex-1">
        {title && <h4 className={cn('font-bold mb-1', current.titleColor)}>{title}</h4>}
        <div className="leading-relaxed opacity-90">{children}</div>
      </div>
      {action && <div className="shrink-0 mr-2">{action}</div>}
    </div>
  )
}
