import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { MainLayout } from './components/layout/MainLayout'

// 9 Core Pages
import { HomePage } from './pages/HomePage'
import { CatalogPage } from './pages/CatalogPage'
import { ExperimentDetailPage } from './pages/ExperimentDetailPage'
import { VirtualLabPage } from './pages/VirtualLabPage'
import { AuthPage } from './pages/AuthPage'
import { StudentDashboardPage } from './pages/StudentDashboardPage'
import { AttemptHistoryPage } from './pages/AttemptHistoryPage'
import { TeacherDashboardPage } from './pages/TeacherDashboardPage'
import { TeacherManagementPage } from './pages/TeacherManagementPage'
import { TeacherAnalyticsPage } from './pages/TeacherAnalyticsPage'
import { DesignSystemShowcase } from './pages/DesignSystemShowcase'

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        {/* 1. صفحه اصلی */}
        <Route path="/" element={<HomePage />} />

        {/* 2. کاتالوگ آزمایش‌ها */}
        <Route path="/experiments" element={<CatalogPage />} />

        {/* 3. جزئیات آزمایش */}
        <Route path="/experiments/:slug" element={<ExperimentDetailPage />} />

        {/* 4. محیط آزمایشگاه مجازی */}
        <Route path="/experiments/:slug/lab" element={<VirtualLabPage />} />

        {/* 5. ورود و ثبت‌نام */}
        <Route path="/auth/login" element={<AuthPage />} />
        <Route path="/auth/register" element={<AuthPage />} />

        {/* 6. داشبورد دانش‌آموز */}
        <Route path="/dashboard" element={<StudentDashboardPage />} />

        {/* 7. تاریخچه آزمایش‌ها و گزارش کارنامه */}
        <Route path="/history" element={<AttemptHistoryPage />} />
        <Route path="/history/:attemptId" element={<AttemptHistoryPage />} />

        {/* 8. داشبورد معلم */}
        <Route path="/teacher/dashboard" element={<TeacherDashboardPage />} />
        <Route path="/teacher/analytics" element={<TeacherAnalyticsPage />} />

        {/* 9. مدیریت محتوای آزمایش‌ها */}
        <Route path="/teacher/experiments" element={<TeacherManagementPage />} />

        {/* راهنمای سیستم طراحی فاز ۱ */}
        <Route path="/design-system" element={<DesignSystemShowcase />} />

        {/* هدایت مسیرهای ناشناخته */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
