import React from 'react'
import { cn } from '../../utils/cn'

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'cyan' | 'blue' | 'emerald' | 'amber' | 'rose' | 'slate' | 'indigo'
  size?: 'sm' | 'md'
  icon?: React.ReactNode
}

export const Badge: React.FC<BadgeProps> = ({
  className,
  variant = 'slate',
  size = 'md',
  icon,
  children,
  ...props
}) => {
  const variants = {
    cyan: 'bg-cyan-950/80 text-cyan-300 border-cyan-800/60 shadow-sm shadow-cyan-950/50',
    blue: 'bg-blue-950/80 text-blue-300 border-blue-800/60 shadow-sm shadow-blue-950/50',
    emerald: 'bg-emerald-950/80 text-emerald-300 border-emerald-800/60 shadow-sm shadow-emerald-950/50',
    amber: 'bg-amber-950/80 text-amber-300 border-amber-800/60 shadow-sm shadow-amber-950/50',
    rose: 'bg-rose-950/80 text-rose-300 border-rose-800/60 shadow-sm shadow-rose-950/50',
    indigo: 'bg-indigo-950/80 text-indigo-300 border-indigo-800/60 shadow-sm shadow-indigo-950/50',
    slate: 'bg-slate-800/80 text-slate-300 border-slate-700'
  }

  const sizes = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs font-medium px-2.5 py-1 gap-1.5'
  }

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-lg border font-sans',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {icon && <span className="inline-flex shrink-0">{icon}</span>}
      <span>{children}</span>
    </span>
  )
}
