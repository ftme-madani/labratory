import React, { forwardRef } from 'react'
import { cn } from '../../utils/cn'

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, leftIcon, rightIcon, id, ...props }, ref) => {
    const inputId = id || (label ? label.replace(/\s+/g, '-').toLowerCase() : undefined)

    return (
      <div className="w-full text-right">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-slate-300 mb-1.5">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {rightIcon && (
            <div className="absolute right-3.5 flex items-center pointer-events-none text-slate-400">
              {rightIcon}
            </div>
          )}
          <input
            id={inputId}
            ref={ref}
            className={cn(
              'w-full bg-slate-900/90 text-slate-100 placeholder:text-slate-500 text-sm rounded-xl border border-slate-700/80 px-4 py-2.5 transition-all duration-150',
              'focus:border-cyan-500 focus:bg-slate-900 focus:ring-2 focus:ring-cyan-500/20 focus:outline-none',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              rightIcon && 'pr-10',
              leftIcon && 'pl-10',
              error && 'border-rose-500 focus:border-rose-500 focus:ring-rose-500/20',
              className
            )}
            {...props}
          />
          {leftIcon && (
            <div className="absolute left-3.5 flex items-center pointer-events-none text-slate-400">
              {leftIcon}
            </div>
          )}
        </div>
        {error ? (
          <p className="mt-1.5 text-xs text-rose-400 font-medium">{error}</p>
        ) : helperText ? (
          <p className="mt-1.5 text-xs text-slate-400">{helperText}</p>
        ) : null}
      </div>
    )
  }
)

Input.displayName = 'Input'
