import type { LessonLine, LessonSection } from '../types/course'

export function line(id: string, textEn: string, textZh: string, speaker?: string): LessonLine {
  return {
    id,
    speaker,
    textEn,
    textZh,
  }
}

export function dialogue(
  id: string,
  titleEn: string,
  titleZh: string,
  lines: LessonLine[],
): LessonSection {
  return {
    id,
    type: 'dialogue',
    titleEn,
    titleZh,
    lines,
  }
}

export function article(
  id: string,
  titleEn: string,
  titleZh: string,
  lines: LessonLine[],
): LessonSection {
  return {
    id,
    type: 'article',
    titleEn,
    titleZh,
    lines,
  }
}
