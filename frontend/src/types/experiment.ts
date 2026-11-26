export type SubjectType = 'شیمی' | 'فیزیک' | 'زیست' | 'زیست‌شناسی' | 'شیمی و فیزیک' | 'زمین‌شناسی'
export type GradeLevel = 'هفتم' | 'هشتم' | 'نهم' | 'دهم' | 'یازدهم' | 'دوازدهم'
export type DifficultyLevel = 'آسان' | 'متوسط' | 'پیشرفته'
export type ContentStatus = 'DRAFT' | 'VERIFIED' | 'PUBLISHED'

export interface TextbookReference {
  book: string
  grade: GradeLevel
  chapter: string
  chapterNumber: number
  page: number
  curriculumCode?: string
}

export interface EquipmentItem {
  id: string
  name: string
  category: 'reagent' | 'glassware' | 'tool' | 'sensor' | 'electric'
  iconName: string
  description: string
  state?: 'solid' | 'liquid' | 'gas' | 'component'
  colorHex?: string
  ph?: number
  isHazardous?: boolean
}

export interface StepPrediction {
  question: string
  options: string[]
  correctOptionIndex: number
  explanation: string
}

export interface ExperimentStepDef {
  index: number
  title: string
  instruction: string
  expectedAction: string
  targetItems: string[]
  scientificConcept: string
  hintLevels: {
    level1: string // سوال تفکری
    level2: string // اشاره مفهومی
    level3: string // اقدام اصلاحی و توضیح کامل
  }
  prediction?: StepPrediction
}

export interface Experiment {
  id: string
  slug: string
  title: string
  subject: SubjectType
  grade: GradeLevel
  difficulty: DifficultyLevel
  durationMinutes: number
  textbook: TextbookReference
  status: ContentStatus
  version: number
  summary: string
  objectives: string[]
  safetyNotes: string[]
  availableTools: EquipmentItem[]
  steps: ExperimentStepDef[]
  featured?: boolean
  thumbnailSvgType: 'flask' | 'circuit' | 'filter' | 'gauge' | 'leaf' | 'test-tube'
  classCode?: string
  isClassOnly?: boolean
  createdById?: number
}
