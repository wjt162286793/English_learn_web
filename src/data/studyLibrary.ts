import nounMarkdown from '../../toai/noun-img.md?raw'
import abstractMarkdown from '../../toai/abstract-noun-verb-sentences.md?raw'
import phraseMarkdown from '../../toai/common-phrases-with-simple-words.md?raw'
import articleMarkdown from '../../toai/short-english-articles-bilingual.md?raw'
import levelOneMarkdown from '../../toai/level1.md?raw'
import { unitDetailMap } from './course'
import type { LessonLine } from '../types/course'

export interface StudyParagraph {
  id: string
  translation: string
  sentences: LessonLine[]
}

export interface StudyItem {
  id: string
  titleEn: string
  titleZh: string
  imageUrl?: string
  wordLine?: LessonLine
  line?: LessonLine
  paragraphs?: StudyParagraph[]
  detail?: string
}

export interface StudySection {
  id: string
  titleEn: string
  titleZh: string
  items: StudyItem[]
}

function stripMarkdown(value: string): string {
  return value.replace(/\*\*/g, '').replace(/<br\s*\/?>/gi, '').trim()
}

function makeLine(id: string, textEn: string, textZh = ''): LessonLine {
  return { id, textEn: stripMarkdown(textEn), textZh }
}

function splitSentences(text: string): string[] {
  return (text.match(/[^.!?]+[.!?]+|[^.!?]+$/g) ?? [text])
    .map((sentence) => sentence.trim())
    .filter(Boolean)
}

function parseNouns(markdown: string): StudySection[] {
  const sections: StudySection[] = []
  let current: StudySection | undefined
  let index = 0

  for (const line of markdown.split(/\r?\n/)) {
    const heading = /^##\s+(.+)$/.exec(line)
    if (heading) {
      current = {
        id: `noun-category-${sections.length + 1}`,
        titleEn: heading[1].trim(),
        titleZh: '',
        items: [],
      }
      sections.push(current)
      continue
    }

    if (!current || !line.startsWith('|')) {
      continue
    }

    const cells = line.split('|')
    if (cells.length < 6) {
      continue
    }

    const word = stripMarkdown(cells[1])
    const imageUrl = cells[2].trim()
    const meaning = cells[3].trim()
    const example = cells[4].trim()
    if (!word || word === '英文名词' || /^-+$/.test(word) || !example) {
      continue
    }

    index += 1
    const id = `library-noun-${String(index).padStart(4, '0')}`
    current.items.push({
      id,
      titleEn: word,
      titleZh: meaning,
      imageUrl: /^https?:\/\//i.test(imageUrl) ? imageUrl : undefined,
      wordLine: makeLine(`${id}-word`, word, meaning),
      line: makeLine(id, example),
    })
  }

  return sections.filter((section) => section.items.length > 0)
}

function parseAbstractSentences(markdown: string): StudySection[] {
  const sections: StudySection[] = []
  let current: StudySection | undefined
  let pendingChinese = ''
  let index = 0

  for (const line of markdown.split(/\r?\n/)) {
    const heading = /^##\s+(.+)$/.exec(line)
    if (heading) {
      current = {
        id: `abstract-category-${sections.length + 1}`,
        titleEn: heading[1].trim(),
        titleZh: '',
        items: [],
      }
      sections.push(current)
      pendingChinese = ''
      continue
    }

    const chinese = /^\d+\.\s*(.+)$/.exec(line.trim())
    if (chinese) {
      pendingChinese = chinese[1].trim()
      continue
    }

    if (current && pendingChinese && /^\s+[A-Z]/.test(line)) {
      index += 1
      const textEn = line.trim()
      const focus = /\*\*(.+?)\*\*/.exec(textEn)?.[1] ?? `Sentence ${index}`
      const id = `library-abstract-${String(index).padStart(3, '0')}`
      current.items.push({
        id,
        titleEn: stripMarkdown(focus),
        titleZh: pendingChinese,
        wordLine: makeLine(`${id}-word`, focus, pendingChinese),
        line: makeLine(id, textEn, pendingChinese),
      })
      pendingChinese = ''
    }
  }

  return sections.filter((section) => section.items.length > 0)
}

function parsePhrases(markdown: string): StudySection[] {
  const sections: StudySection[] = []
  let current: StudySection | undefined
  let pending: { phrase: string; meaning: string } | undefined
  let index = 0

  for (const line of markdown.split(/\r?\n/)) {
    const heading = /^##\s+(.+)$/.exec(line)
    if (heading) {
      current = {
        id: `phrase-category-${sections.length + 1}`,
        titleEn: heading[1].trim(),
        titleZh: '',
        items: [],
      }
      pending = undefined
      sections.push(current)
      continue
    }

    const phrase = /^\d+\.\s+\*\*(.+?)\*\*\s+—\s+(.+)$/.exec(line)
    if (phrase) {
      pending = { phrase: phrase[1].trim(), meaning: phrase[2].trim() }
      continue
    }

    if (!current || !pending) {
      continue
    }

    const example = /^\s{3,}(.+?)（(.+)）$/.exec(line.trimEnd())
    if (!example) {
      continue
    }

    index += 1
    const id = `library-phrase-${String(index).padStart(3, '0')}`
    current.items.push({
      id,
      titleEn: pending.phrase,
      titleZh: pending.meaning,
      wordLine: makeLine(`${id}-word`, pending.phrase, pending.meaning),
      line: makeLine(id, example[1].trim(), example[2].trim()),
    })
    pending = undefined
  }

  return sections.filter((section) => section.items.length > 0)
}

function parseArticles(markdown: string): StudyItem[] {
  const articles: StudyItem[] = []
  let currentArticle: StudyItem | undefined
  let currentParagraph: StudyParagraph | undefined
  let language: 'en' | 'zh' | '' = ''

  for (const line of markdown.split(/\r?\n/)) {
    const normalizedLine = line.trim()
    const heading = /^##\s+(\d{2})\.\s+(.+)$/.exec(normalizedLine)
    if (heading) {
      currentArticle = {
        id: `reading-article-${heading[1]}`,
        titleEn: heading[2].trim(),
        titleZh: '双语阅读',
        paragraphs: [],
      }
      articles.push(currentArticle)
      currentParagraph = undefined
      language = ''
      continue
    }

    if (!currentArticle) {
      continue
    }

    if (/^\*\*EN\s+—\s+Paragraph\s+\d+\*\*$/.test(normalizedLine)) {
      const paragraphNumber = Number(/Paragraph\s+(\d+)/.exec(normalizedLine)?.[1] ?? 0)
      currentParagraph = {
        id: `${currentArticle.id}-p${String(paragraphNumber).padStart(2, '0')}`,
        translation: '',
        sentences: [],
      }
      currentArticle.paragraphs?.push(currentParagraph)
      language = 'en'
      continue
    }

    if (/^\*\*中文\s+—\s+第\s*\d+\s*段\*\*$/.test(normalizedLine)) {
      language = 'zh'
      continue
    }

    if (!currentParagraph || !normalizedLine || normalizedLine.startsWith('>')) {
      continue
    }

    if (language === 'en') {
      const sentences = splitSentences(stripMarkdown(normalizedLine))
      sentences.forEach((text) => {
        const sentenceNumber = currentParagraph?.sentences.length ?? 0
        const sentenceId = `${currentParagraph?.id}-s${String(sentenceNumber + 1).padStart(2, '0')}`
        currentParagraph?.sentences.push(makeLine(sentenceId, text))
      })
      continue
    }

    if (language === 'zh') {
      currentParagraph.translation = normalizedLine
      language = ''
    }
  }

  return articles.filter((article) =>
    article.paragraphs?.some((paragraph) => paragraph.sentences.length > 0),
  )
}

function parseLevelOne(markdown: string): StudySection[] {
  const sections: StudySection[] = []
  let current: StudySection | undefined
  let sentenceNumber = 0

  for (const line of markdown.split(/\r?\n/)) {
    const heading = /^##\s+Unit\s+(\d+)\s+·\s+(.+)$/.exec(line.trim())
    if (heading) {
      const title = heading[2].trim()
      const englishTitle = title.match(/[A-Za-z][A-Za-z &]+$/)?.[0].trim() ?? title
      const chineseTitle = title.slice(0, title.length - englishTitle.length).trim()
      current = {
        id: `level1-unit-${String(Number(heading[1])).padStart(2, '0')}`,
        titleEn: `Unit ${Number(heading[1])} · ${englishTitle}`,
        titleZh: chineseTitle,
        items: [],
      }
      sections.push(current)
      sentenceNumber = 0
      continue
    }

    const entry = /^\d+\.\s+(.+)$/.exec(line.trim())
    if (!current || !entry) {
      continue
    }

    const separator = entry[1].lastIndexOf(' — ')
    if (separator < 0) {
      continue
    }

    const textEn = stripMarkdown(entry[1].slice(0, separator))
    const definition = stripMarkdown(entry[1].slice(separator + 3))
    const focus = /\*\*(.+?)\*\*/.exec(entry[1].slice(0, separator))?.[1]?.trim()
    if (!focus || !textEn) {
      continue
    }

    sentenceNumber += 1
    const id = `${current.id}-s${String(sentenceNumber).padStart(3, '0')}`
    const meaning = definition.replace(new RegExp(`^${focus}\\s*`, 'i'), '')
    current.items.push({
      id,
      titleEn: focus,
      titleZh: meaning,
      line: makeLine(id, textEn),
    })
  }

  return sections.filter((section) => section.items.length > 0)
}

const nounSections = parseNouns(nounMarkdown)
const abstractSections = parseAbstractSentences(abstractMarkdown)
const phraseSections = parsePhrases(phraseMarkdown)

export const levelOneSections = parseLevelOne(levelOneMarkdown)
export const vocabularySections: StudySection[] = [
  ...nounSections,
  ...abstractSections,
  ...phraseSections,
]

export const sentenceSections: StudySection[] = abstractSections.map((section) => ({
  ...section,
  id: `reading-${section.id}`,
  titleEn: `Long sentences · ${section.titleEn}`,
}))
const articleItems = parseArticles(articleMarkdown)
const articleSection: StudySection = {
  id: 'reading-articles',
  titleEn: 'Bilingual articles',
  titleZh: '双语短文',
  items: articleItems,
}
export const readingSections = [...sentenceSections, articleSection]

function articleCollection(titleEn: string, titleZh: string, articleNumbers: string[]): StudySection {
  const allowed = new Set(articleNumbers.map((number) => `reading-article-${number}`))
  return {
    id: `professional-${articleNumbers.join('-')}`,
    titleEn,
    titleZh,
    items: articleItems
      .filter((article) => allowed.has(article.id))
      .map((article) => article),
  }
}

const workUnits = Object.values(unitDetailMap).filter((unit) =>
  /\b(work|jobs?|business|companies|company|careers?|interview|negotiat\w*|sales?)\b/i.test(
    unit.titleEn,
  ),
)

const workCourseSections: StudySection[] = workUnits.map((unit) => ({
  id: `professional-course-${unit.id}`,
  titleEn: unit.titleEn,
  titleZh: unit.titleZh,
  items: [...unit.dialogues, ...unit.articles].flatMap((section) =>
    section.lines.map((line) => ({
      id: line.id,
      titleEn: section.titleEn,
      titleZh: section.titleZh,
      line,
    })),
  ),
}))

const professionalVocabularySections: StudySection[] = nounSections
  .filter((section) => /工作与办公室|常见职业|商业与金钱|电脑与数字设备|互联网与媒体/.test(section.titleEn))
  .map((section) => ({
    ...section,
    id: `professional-vocabulary-${section.id}`,
    titleEn: `Vocabulary · ${section.titleEn}`,
  }))

export const professionalSections: StudySection[] = [
  ...professionalVocabularySections,
  ...workCourseSections,
  articleCollection('Work, careers & money', '工作、职业与财务', ['06', '10', '11', '19']),
  articleCollection('Technology & society', '科技与社会', ['01', '13', '14']),
]
