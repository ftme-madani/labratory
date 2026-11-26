import React from 'react'
import { cn } from '../../utils/cn'

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean
  variant?: 'glass' | 'solid' | 'bordered'
}

export const Card: React.FC<CardProps> = ({
  className,
  hoverable = false,
  variant = 'glass',
  children,
  ...props
}) => {
  const variants = {
    glass: 'glass-panel text-slate-100',
    solid: 'bg-slate-900 border border-slate-800 text-slate-100',
    bordered: 'bg-slate-900/40 border border-slate-700/60 text-slate-100'
  }

  return (
    <div
      className={cn(
        'rounded-2xl overflow-hidden transition-all duration-200',
        variants[variant],
        hoverable && 'glass-panel-hover cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => (
  <div className={cn('p-5 border-b border-slate-800/80 flex items-center justify-between', className)} {...props}>
    {children}
  </div>
)

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => (
  <div className={cn('p-5', className)} {...props}>
    {children}
  </div>
)

export const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => (
  <div className={cn('p-5 pt-0 flex items-center gap-3', className)} {...props}>
    {children}
  </div>
)
