import React from 'react'
import { FlaskConical } from 'lucide-react'
import { cn } from '../../utils/cn'

export interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: React.ReactNode
  className?: string
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  className
}) => {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-8 text-center rounded-2xl border border-dashed border-slate-800 bg-slate-900/30 text-slate-400',
        className
      )}
    >
      <div className="w-14 h-14 rounded-2xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-cyan-400 mb-4 shadow-inner">
        {icon || <FlaskConical className="w-7 h-7" />}
      </div>
      <h3 className="text-base font-bold text-slate-200 mb-1">{title}</h3>
      {description && <p className="text-xs text-slate-400 max-w-sm mb-5">{description}</p>}
      {action && <div>{action}</div>}
    </div>
  )
}
