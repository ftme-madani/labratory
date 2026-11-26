import React, { forwardRef } from 'react'
import { cn } from '../../utils/cn'
import { ChevronDown } from 'lucide-react'

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  options: { value: string | number; label: string }[]
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, options, id, children, ...props }, ref) => {
    const selectId = id || (label ? label.replace(/\s+/g, '-').toLowerCase() : undefined)

    return (
      <div className="w-full text-right">
        {label && (
          <label htmlFor={selectId} className="block text-sm font-medium text-slate-300 mb-1.5">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          <select
            id={selectId}
            ref={ref}
            className={cn(
              'w-full appearance-none bg-slate-900/90 text-slate-100 text-sm rounded-xl border border-slate-700/80 px-4 py-2.5 pl-10 pr-4 transition-all duration-150 cursor-pointer',
              'focus:border-cyan-500 focus:bg-slate-900 focus:ring-2 focus:ring-cyan-500/20 focus:outline-none',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              error && 'border-rose-500 focus:border-rose-500',
              className
            )}
            {...props}
          >
            {options.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-slate-900 text-slate-100">
                {opt.label}
              </option>
            ))}
          </select>
          <div className="absolute left-3.5 flex items-center pointer-events-none text-slate-400">
            <ChevronDown className="w-4 h-4" />
          </div>
        </div>
        {error && <p className="mt-1.5 text-xs text-rose-400 font-medium">{error}</p>}
      </div>
    )
  }
)

Select.displayName = 'Select'
