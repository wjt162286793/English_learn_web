export interface LessonLine {
  id: string
  speaker?: string
  textEn: string
  textZh: string
}

export interface LessonSection {
  id: string
  type: 'dialogue' | 'article'
  titleEn: string
  titleZh: string
  lines: LessonLine[]
}

export interface SentenceItem {
  id: string
  textEn: string
  note: string
}

export interface SentenceGroup {
  id: string
  titleEn: string
  titleZh: string
  items: SentenceItem[]
}

export interface CourseUnitSummary {
  id: string
  unitNumber: number
  titleEn: string
  titleZh: string
  available: boolean
}

export interface CourseLevel {
  id: string
  levelNumber: number
  title: string
  bandCode: 'A1' | 'A2' | 'B1' | 'B2'
  bandLabel: string
  units: CourseUnitSummary[]
}

export interface CourseBand {
  id: 'A1' | 'A2' | 'B1' | 'B2'
  label: string
  subtitle: string
  levels: CourseLevel[]
}

export interface CourseUnitDetail extends CourseUnitSummary {
  levelId: string
  levelTitle: string
  bandCode: 'A1' | 'A2' | 'B1' | 'B2'
  summaryEn: string
  summaryZh: string
  dialogues: LessonSection[]
  articles: LessonSection[]
  sentences: SentenceGroup
}
