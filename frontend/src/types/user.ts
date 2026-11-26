export type UserRole = 'student' | 'teacher' | 'admin'

export interface User {
  id: string
  username: string
  fullName: string
  email: string
  role: UserRole
  grade?: string
  schoolName?: string
  avatarUrl?: string
  createdAt: string
}

export interface UserProgressStats {
  completedExperiments: number
  totalAttempts: number
  averageScore: number
  hintsRequestedTotal: number
  badges: {
    id: string
    title: string
    description: string
    icon: string
    earnedAt: string
  }[]
}
