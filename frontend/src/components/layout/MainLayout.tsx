import React from 'react'
import { Outlet } from 'react-router-dom'
import { Navbar } from './Navbar'
import { Footer } from './Footer'
import { useThemeStore } from '../../store/useThemeStore'

export const MainLayout: React.FC = () => {
  const { theme } = useThemeStore()

  return (
    <div className={`min-h-screen flex flex-col transition-colors duration-200 ${
      theme === 'light' ? 'bg-[#f4f7fb] text-slate-800' : 'bg-slate-950 text-slate-100'
    }`}>
      <Navbar />
      <main className="flex-1 flex flex-col">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
