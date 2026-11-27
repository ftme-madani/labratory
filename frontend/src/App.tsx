import { useState, useEffect } from 'react'
import { BrowserRouter } from 'react-router-dom'
import { AppRoutes } from './routes'
import { WifiOff } from 'lucide-react'

export function App() {
  const [isOffline, setIsOffline] = useState(!navigator.onLine)

  useEffect(() => {
    const handleOnline = () => setIsOffline(false)
    const handleOffline = () => setIsOffline(true)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return (
    <BrowserRouter>
      {isOffline && (
        <div className="bg-amber-500 text-slate-950 font-bold px-4 py-2 text-xs flex items-center justify-center gap-2 sticky top-0 z-50 shadow-md">
          <WifiOff className="w-4 h-4 shrink-0" />
          <span>شما در وضعیت آفلاین هستید. آزمایشگاه با داده‌های ذخیره‌شده محلی کار می‌کند.</span>
        </div>
      )}
      <AppRoutes />
    </BrowserRouter>
  )
}

export default App
