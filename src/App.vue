<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import ContentSection from './components/ContentSection.vue'
import SentenceBlock from './components/SentenceBlock.vue'
import { courseBands, unitDetailMap } from './data/course'
import type {
  CourseUnitDetail,
  LessonLine,
  LessonSection,
  SentenceGroup,
  SentenceItem,
} from './types/course'

const femaleVoiceKeywords = [
  'zira',
  'hazel',
  'aria',
  'jenny',
  'emma',
  'ava',
  'libby',
  'sonia',
  'michelle',
  'samantha',
  'susan',
  'cora',
  'ana',
  'google uk english female',
  'google us english',
  'google',
]
const maleVoiceKeywords = [
  'david',
  'mark',
  'guy',
  'ryan',
  'christopher',
  'davis',
  'tony',
  'daniel',
  'alex',
  'fred',
  'oliver',
  'thomas',
  'roger',
  'george',
  'google uk english male',
  'google us english male',
]

const voiceRetryCount = 3

type PronunciationMode = 'standard' | 'natural' | 'dictation'

const activeUnitId = ref('a1-l1-u1')
const showChinese = ref(true)
const showEnglish = ref(true)
const showSentenceText = ref(true)
const pronunciationMode = ref<PronunciationMode>('standard')
const isMobileViewport = ref(false)
const showMobileRoadmap = ref(false)
const femaleVoiceUri = ref('')
const maleVoiceUri = ref('')
const playbackRate = ref('1')
const voices = ref<SpeechSynthesisVoice[]>([])
const speechSupported = ref(false)
const activeLineId = ref('')
const activeBlockId = ref('')
const playingAll = ref(false)
const voiceNotice = ref('')
const audioManifest = ref<Set<string>>(new Set())

let playbackToken = 0
let probedVoiceUri = ''
let currentAudio: HTMLAudioElement | null = null

const activeUnit = computed<CourseUnitDetail>(() => unitDetailMap[activeUnitId.value])
const activeDisplayUnit = computed<CourseUnitDetail>(() =>
  buildDisplayUnit(activeUnit.value, pronunciationMode.value),
)
const currentSections = computed<LessonSection[]>(() => [
  ...activeDisplayUnit.value.dialogues,
  ...activeDisplayUnit.value.articles,
])
const activeSentenceGroup = computed<SentenceGroup>(() => activeUnit.value.sentences)
function updateViewportState(): void {
  if (typeof window === 'undefined') {
    return
  }
  isMobileViewport.value = window.innerWidth <= 900
  if (!isMobileViewport.value) {
    showMobileRoadmap.value = false
  }
}

function capitalizeLike(source: string, replacement: string): string {
  if (source.length === 0) {
    return replacement
  }
  if (source[0] === source[0].toUpperCase()) {
    return replacement.charAt(0).toUpperCase() + replacement.slice(1)
  }
  return replacement
}

function replacePhrase(text: string, pattern: RegExp, replacement: string): string {
  return text.replace(pattern, (matched) => capitalizeLike(matched, replacement))
}

function applyNaturalSpeech(text: string): string {
  let result = text
  result = replacePhrase(result, /\bgoing to\b/gi, 'gonna')
  result = replacePhrase(result, /\bwant to\b/gi, 'wanna')
  result = replacePhrase(result, /\bgot to\b/gi, 'gotta')
  result = replacePhrase(result, /\bhave to\b/gi, 'hafta')
  result = replacePhrase(result, /\bkind of\b/gi, 'kinda')
  result = replacePhrase(result, /\bout of\b/gi, 'outta')
  result = replacePhrase(result, /\ba lot of\b/gi, 'a lotta')
  result = replacePhrase(result, /\blet me\b/gi, 'lemme')
  result = replacePhrase(result, /\bgive me\b/gi, 'gimme')
  result = replacePhrase(result, /\bdid you\b/gi, 'didja')
  result = replacePhrase(result, /\bwould you\b/gi, 'wouldja')
  result = replacePhrase(result, /\bcould you\b/gi, 'couldja')
  result = replacePhrase(result, /\bshould you\b/gi, 'shouldja')
  result = replacePhrase(result, /\bgot you\b/gi, 'gotcha')
  result = replacePhrase(result, /\bwant you to\b/gi, 'wantcha to')
  return result
}

function applyDictationSpeech(text: string): string {
  let result = applyNaturalSpeech(text)
  result = replacePhrase(result, /\bwhat do you\b/gi, 'whaddaya')
  result = replacePhrase(result, /\bwhat are you\b/gi, 'whatcha')
  result = replacePhrase(result, /\bdo you\b/gi, "d'ya")
  result = replacePhrase(result, /\bare you\b/gi, 'are ya')
  result = replacePhrase(result, /\bdon't you\b/gi, 'doncha')
  result = replacePhrase(result, /\bhave you\b/gi, 'have ya')
  result = replacePhrase(result, /\bmeet you\b/gi, 'meetcha')
  result = replacePhrase(result, /\bget you\b/gi, 'getcha')
  result = replacePhrase(result, /\bdidja\b/gi, 'didja')
  return result
}

function applyPronunciationMode(text: string, mode: PronunciationMode): string {
  if (mode === 'natural') {
    return applyNaturalSpeech(text)
  }
  if (mode === 'dictation') {
    return applyDictationSpeech(text)
  }
  return text
}

function toSentenceLine(item: SentenceItem): LessonLine {
  return {
    id: item.id,
    textEn: item.textEn.replace(/\*\*/g, ''),
    textZh: item.note,
  }
}

function buildDisplaySection(section: LessonSection, mode: PronunciationMode): LessonSection {
  return {
    ...section,
    lines: section.lines.map((currentLine) => ({
      ...currentLine,
      textEn: applyPronunciationMode(currentLine.textEn, mode),
    })),
  }
}

function buildDisplayUnit(unit: CourseUnitDetail, mode: PronunciationMode): CourseUnitDetail {
  return {
    ...unit,
    dialogues: unit.dialogues.map((section) => buildDisplaySection(section, mode)),
    articles: unit.articles.map((section) => buildDisplaySection(section, mode)),
  }
}

function getVoiceByUri(voiceUri: string): SpeechSynthesisVoice | null {
  return voices.value.find((voice) => voice.voiceURI === voiceUri) ?? null
}

function pickVoiceByKeywords(
  list: SpeechSynthesisVoice[],
  keywords: string[],
  excludedUri = '',
): SpeechSynthesisVoice | undefined {
  for (const keyword of keywords) {
    const matched = list.find(
      (voice) =>
        voice.voiceURI !== excludedUri &&
        voice.name.toLowerCase().includes(keyword.toLowerCase()),
    )
    if (matched) {
      return matched
    }
  }
  return undefined
}

function pickStableVoice(
  list: SpeechSynthesisVoice[],
  excludedUri = '',
): SpeechSynthesisVoice | undefined {
  return (
    list.find((voice) => voice.voiceURI !== excludedUri && voice.localService) ??
    list.find((voice) => voice.voiceURI !== excludedUri) ??
    list[0]
  )
}

function pickPreferredVoice(
  list: SpeechSynthesisVoice[],
  keywords: string[],
  excludedUri = '',
): SpeechSynthesisVoice | undefined {
  const localVoices = list.filter((voice) => voice.localService)
  return (
    pickVoiceByKeywords(localVoices, keywords, excludedUri) ??
    pickVoiceByKeywords(list, keywords, excludedUri) ??
    pickStableVoice(list, excludedUri)
  )
}

function getDialogueVoiceRole(
  line: LessonLine,
  section: LessonSection | undefined,
): 'female' | 'male' {
  if (!section || section.type !== 'dialogue' || !line.speaker) {
    return 'female'
  }

  const speakers: string[] = []
  for (const currentLine of section.lines) {
    if (!currentLine.speaker || speakers.includes(currentLine.speaker)) {
      continue
    }
    speakers.push(currentLine.speaker)
  }

  const speakerIndex = speakers.indexOf(line.speaker)
  if (speakerIndex === 1) {
    return 'male'
  }
  if (speakerIndex >= 2) {
    return speakerIndex % 2 === 0 ? 'female' : 'male'
  }
  return 'female'
}

type AudioRole = 'female' | 'male'

function getAudioRole(line: LessonLine, section?: LessonSection): AudioRole {
  const resolvedSection = section ?? findSectionByLineId(line.id)
  return getDialogueVoiceRole(line, resolvedSection) === 'male' ? 'male' : 'female'
}

function getAudioPath(line: LessonLine, section?: LessonSection): string {
  const role = getAudioRole(line, section)
  return `/audio/${pronunciationMode.value}/${line.id}-${role}.mp3`
}

function hasStaticAudio(lines: LessonLine[], section?: LessonSection): boolean {
  return (
    audioManifest.value.size > 0 &&
    lines.every((line) => audioManifest.value.has(getAudioPath(line, section)))
  )
}

function loadAudioManifest(): void {
  void fetch('/audio/manifest.json')
    .then((response) => (response.ok ? response.json() : []))
    .then((paths: unknown) => {
      if (!Array.isArray(paths)) {
        return
      }
      audioManifest.value = new Set(paths.filter((path): path is string => typeof path === 'string'))
    })
    .catch(() => {
      audioManifest.value = new Set()
    })
}

function findSectionByLineId(lineId: string): LessonSection | undefined {
  return currentSections.value.find((section) =>
    section.lines.some((line) => line.id === lineId),
  )
}

function getVoiceCandidates(
  line: LessonLine,
  contextSection?: LessonSection,
): SpeechSynthesisVoice[] {
  const section = contextSection ?? findSectionByLineId(line.id)
  const role = getDialogueVoiceRole(line, section)
  const selectedUri = role === 'male' ? maleVoiceUri.value : femaleVoiceUri.value
  const roleKeywords = role === 'male' ? maleVoiceKeywords : femaleVoiceKeywords
  const selectedVoice = getVoiceByUri(selectedUri)
  const preferredFallback = pickVoiceByKeywords(voices.value, roleKeywords, selectedUri)
  const candidates = [selectedVoice, preferredFallback, ...voices.value].filter(
    (voice): voice is SpeechSynthesisVoice => voice !== null && voice !== undefined,
  )

  return candidates.filter(
    (voice, index) => candidates.findIndex((candidate) => candidate.voiceURI === voice.voiceURI) === index,
  )
}

function getSavedVoiceUri(key: string): string {
  try {
    return window.localStorage.getItem(key) ?? ''
  } catch {
    return ''
  }
}

function saveVoiceUri(key: string, voiceUri: string): void {
  try {
    window.localStorage.setItem(key, voiceUri)
  } catch {
    return
  }
}

function readVoicePreferenceVersion(): string {
  try {
    return window.localStorage.getItem('english-learning-voice-version') ?? ''
  } catch {
    return ''
  }
}

function writeVoicePreferenceVersion(version: string): void {
  try {
    window.localStorage.setItem('english-learning-voice-version', version)
  } catch {
    return
  }
}

function probeVoice(voice: SpeechSynthesisVoice, timeoutMs = 2500): Promise<boolean> {
  return new Promise((resolve) => {
    if (!speechSupported.value) {
      resolve(false)
      return
    }

    let settled = false
    const utterance = new SpeechSynthesisUtterance('a')
    utterance.voice = voice
    utterance.lang = voice.lang
    utterance.volume = 0
    utterance.rate = 2

    const finish = (ok: boolean): void => {
      if (settled) {
        return
      }
      settled = true
      window.clearTimeout(timerId)
      utterance.onstart = null
      utterance.onend = null
      utterance.onerror = null
      resolve(ok)
    }

    const timerId = window.setTimeout(() => finish(false), timeoutMs)
    utterance.onstart = () => finish(true)
    utterance.onerror = () => finish(false)
    window.speechSynthesis.speak(utterance)
  })
}

async function warmUpPreferredVoice(): Promise<void> {
  if (!speechSupported.value) {
    return
  }

  const selected = getVoiceByUri(femaleVoiceUri.value)
  if (!selected || selected.localService || probedVoiceUri === selected.voiceURI) {
    return
  }
  probedVoiceUri = selected.voiceURI

  for (let attempt = 0; attempt < voiceRetryCount; attempt += 1) {
    const usable = await probeVoice(selected)
    if (usable) {
      voiceNotice.value = ''
      return
    }
  }

  voiceNotice.value = `${selected.name} 启动较慢，点播放会自动重试`
}

function loadVoices(): void {
  if (!speechSupported.value) {
    return
  }

  const rawVoices = window.speechSynthesis.getVoices()
  const englishVoices = rawVoices.filter((voice) => voice.lang.toLowerCase().startsWith('en'))
  const nextVoices = englishVoices.length > 0 ? englishVoices : rawVoices
  voices.value = nextVoices

  const voicePreferenceVersion = '4'
  const isPreferenceCurrent = readVoicePreferenceVersion() === voicePreferenceVersion
  const savedFemaleVoiceUri = isPreferenceCurrent
    ? getSavedVoiceUri('english-learning-female-voice')
    : ''
  const savedMaleVoiceUri = isPreferenceCurrent
    ? getSavedVoiceUri('english-learning-male-voice')
    : ''
  const hasFemaleVoice = nextVoices.some((voice) => voice.voiceURI === femaleVoiceUri.value)
  const hasMaleVoice = nextVoices.some((voice) => voice.voiceURI === maleVoiceUri.value)

  if (!hasFemaleVoice) {
    femaleVoiceUri.value =
      (nextVoices.some((voice) => voice.voiceURI === savedFemaleVoiceUri)
        ? savedFemaleVoiceUri
        : pickPreferredVoice(nextVoices, femaleVoiceKeywords)?.voiceURI) ??
      nextVoices[0]?.voiceURI ??
      ''
  }

  if (!hasMaleVoice) {
    maleVoiceUri.value =
      (nextVoices.some((voice) => voice.voiceURI === savedMaleVoiceUri)
        ? savedMaleVoiceUri
        : pickPreferredVoice(nextVoices, maleVoiceKeywords, femaleVoiceUri.value)?.voiceURI) ??
      pickStableVoice(nextVoices, femaleVoiceUri.value)?.voiceURI ??
      ''
  }

  writeVoicePreferenceVersion(voicePreferenceVersion)
  void warmUpPreferredVoice()
}

function resetPlaybackState(): void {
  activeLineId.value = ''
  activeBlockId.value = ''
  playingAll.value = false
}

function stopSpeaking(): void {
  playbackToken += 1
  if (currentAudio) {
    currentAudio.pause()
    currentAudio.currentTime = 0
    currentAudio = null
  }
  if (speechSupported.value) {
    window.speechSynthesis.cancel()
    resetPlaybackState()
  }
}

function playStaticLines(
  lines: LessonLine[],
  options: {
    section?: LessonSection
    blockId?: string
    playWholeUnit?: boolean
  },
  currentToken: number,
): void {
  const playNext = (index: number): void => {
    if (currentToken !== playbackToken || index >= lines.length) {
      if (index >= lines.length) {
        resetPlaybackState()
      }
      return
    }

    const line = lines[index]
    const audio = new Audio(getAudioPath(line, options.section))
    currentAudio = audio
    activeLineId.value = line.id
    audio.onended = () => {
      if (currentToken === playbackToken) {
        playNext(index + 1)
      }
    }
    audio.onerror = () => {
      if (currentToken === playbackToken) {
        voiceNotice.value = '静态音频播放失败，已切换浏览器语音'
        playLinesWithBrowserVoice(lines.slice(index), options, currentToken)
      }
    }
    void audio.play().catch(() => {
      audio.onerror?.(new Event('error'))
    })
  }

  activeBlockId.value = options.blockId ?? ''
  playingAll.value = options.playWholeUnit ?? false
  playNext(0)
}

function playLinesWithBrowserVoice(
  lines: LessonLine[],
  options: {
    section?: LessonSection
    blockId?: string
    playWholeUnit?: boolean
  },
  currentToken: number,
): void {
  const speakNext = (index: number): void => {
    if (index >= lines.length) {
      resetPlaybackState()
      return
    }
    const line = lines[index]
    speakLineWithFallback(
      line,
      index,
      currentToken,
      lines,
      options,
      getVoiceCandidates(line, options.section),
      0,
      speakNext,
    )
  }
  speakNext(0)
}

function speakLineWithFallback(
  line: LessonLine,
  index: number,
  currentToken: number,
  lines: LessonLine[],
  options: {
    blockId?: string
    playWholeUnit?: boolean
    section?: LessonSection
  },
  voiceCandidates: SpeechSynthesisVoice[],
  candidateIndex: number,
  speakNext: (index: number) => void,
  attempt = 0,
): void {
  if (currentToken !== playbackToken) {
    return
  }

  const voice = voiceCandidates[candidateIndex]
  const utterance = new SpeechSynthesisUtterance(line.textEn)
  utterance.rate = Number(playbackRate.value)
  utterance.pitch = 1
  utterance.lang = voice?.lang ?? 'en-US'
  if (voice) {
    utterance.voice = voice
  }

  let settled = false
  let started = false
  let watchdogId = 0

  const clearWatchdog = (): void => {
    if (watchdogId !== 0) {
      window.clearTimeout(watchdogId)
      watchdogId = 0
    }
  }

  const retryOrContinue = (): void => {
    if (settled || currentToken !== playbackToken) {
      return
    }
    settled = true
    clearWatchdog()

    if (attempt + 1 < voiceRetryCount) {
      window.speechSynthesis.cancel()
      window.setTimeout(() => {
        speakLineWithFallback(
          line,
          index,
          currentToken,
          lines,
          options,
          voiceCandidates,
          candidateIndex,
          speakNext,
          attempt + 1,
        )
      }, 150)
      return
    }

    const nextCandidateIndex = candidateIndex + 1
    if (nextCandidateIndex >= voiceCandidates.length) {
      window.setTimeout(() => speakNext(index + 1), 100)
      return
    }

    voiceNotice.value = `当前音色${voice?.name ?? ''}未能播放，正在切换备用音色`
    window.speechSynthesis.cancel()
    window.setTimeout(() => {
      speakLineWithFallback(
        line,
        index,
        currentToken,
        lines,
        options,
        voiceCandidates,
        nextCandidateIndex,
        speakNext,
        0,
      )
    }, 150)
  }

  watchdogId = window.setTimeout(() => {
    retryOrContinue()
  }, 4000)

  utterance.onstart = () => {
    started = true
    clearWatchdog()
    watchdogId = window.setTimeout(
      retryOrContinue,
      Math.max(10000, line.textEn.length * 300),
    )
  }
  utterance.onend = () => {
    if (settled || currentToken !== playbackToken) {
      return
    }
    settled = true
    clearWatchdog()
    speakNext(index + 1)
  }
  utterance.onerror = () => {
    if (currentToken !== playbackToken) {
      return
    }
    retryOrContinue()
  }

  if (!started) {
    activeLineId.value = line.id
  }
  window.speechSynthesis.speak(utterance)
}

function playLines(
  lines: LessonLine[],
  options?: {
    blockId?: string
    playWholeUnit?: boolean
    section?: LessonSection
  },
): void {
  if (!speechSupported.value || lines.length === 0) {
    return
  }

  playbackToken += 1
  const currentToken = playbackToken

  window.speechSynthesis.cancel()
  activeBlockId.value = options?.blockId ?? ''
  playingAll.value = options?.playWholeUnit ?? false
  voiceNotice.value = ''

  if (hasStaticAudio(lines, options?.section)) {
    playStaticLines(lines, options ?? {}, currentToken)
    return
  }

  playLinesWithBrowserVoice(lines, options ?? {}, currentToken)
}

function handlePlayLine(line: LessonLine): void {
  stopSpeaking()
  playLines([line], {
    blockId: findSectionByLineId(line.id)?.id ?? '',
    section: findSectionByLineId(line.id),
  })
}

function handlePlaySection(section: LessonSection): void {
  stopSpeaking()
  playLines(section.lines, {
    blockId: section.id,
    section,
  })
}

function handlePlaySentence(item: SentenceItem): void {
  stopSpeaking()
  playLines([toSentenceLine(item)], { blockId: activeSentenceGroup.value.id })
}

function handlePlaySentenceGroup(group: SentenceGroup): void {
  stopSpeaking()
  playLines(group.items.map(toSentenceLine), { blockId: group.id })
}

function selectUnit(unitId: string, available: boolean): void {
  if (!available) {
    return
  }
  stopSpeaking()
  activeUnitId.value = unitId
  if (isMobileViewport.value) {
    showMobileRoadmap.value = false
  }
}

onMounted(() => {
  updateViewportState()
  speechSupported.value = typeof window !== 'undefined' && 'speechSynthesis' in window
  window.addEventListener('resize', updateViewportState)
  if (!speechSupported.value) {
    loadAudioManifest()
    return
  }
  loadAudioManifest()
  loadVoices()
  window.speechSynthesis.addEventListener('voiceschanged', loadVoices)
})

watch(femaleVoiceUri, (voiceUri) => {
  if (voiceUri && typeof window !== 'undefined') {
    saveVoiceUri('english-learning-female-voice', voiceUri)
  }
})

watch(maleVoiceUri, (voiceUri) => {
  if (voiceUri && typeof window !== 'undefined') {
    saveVoiceUri('english-learning-male-voice', voiceUri)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateViewportState)
  if (speechSupported.value) {
    window.speechSynthesis.removeEventListener('voiceschanged', loadVoices)
    window.speechSynthesis.cancel()
  }
  if (currentAudio) {
    currentAudio.pause()
    currentAudio = null
  }
})
</script>

<template>
  <div class="page-shell">
    <div
      v-if="isMobileViewport && showMobileRoadmap"
      class="mobile-backdrop"
      @click="showMobileRoadmap = false"
    />

    <aside
      v-if="!isMobileViewport || showMobileRoadmap"
      class="sidebar"
      :class="{ 'sidebar--drawer': isMobileViewport }"
    >
      <div class="sidebar__top">
        <div class="sidebar__top-bar">
          <p class="sidebar__eyebrow">English Path</p>
          <button
            v-if="isMobileViewport"
            class="sidebar__close"
            type="button"
            @click="showMobileRoadmap = false"
          >
            关闭目录
          </button>
        </div>
        <h1 class="sidebar__title">从 A1 到 B1 的个人英语学习站</h1>
        <p class="sidebar__desc">
          Level 1 到 Level 3 的 18 个单元已全部就绪。每个单元包含对话、文章和句子三种模块，并支持标准版、口语连读版和听力辨音版三种训练方式。
        </p>
      </div>

      <div class="sidebar__roadmap">
        <div v-for="band in courseBands" :key="band.id" class="band-card">
          <div class="band-card__header">
            <div>
              <p class="band-card__code">{{ band.id }}</p>
              <h2 class="band-card__title">{{ band.label }}</h2>
            </div>
            <span class="band-card__subtitle">{{ band.subtitle }}</span>
          </div>

          <div v-for="level in band.levels" :key="level.id" class="level-card">
            <div class="level-card__header">
              <h3 class="level-card__title">{{ level.title }}</h3>
              <span class="level-card__meta">6 units</span>
            </div>

            <button
              v-for="unit in level.units"
              :key="unit.id"
              class="unit-card"
              :class="{
                'unit-card--active': activeUnitId === unit.id,
                'unit-card--locked': !unit.available,
              }"
              type="button"
              :disabled="!unit.available"
              @click="selectUnit(unit.id, unit.available)"
            >
              <span class="unit-card__number">Unit {{ unit.unitNumber }}</span>
              <span class="unit-card__title">{{ unit.titleEn }}</span>
              <span class="unit-card__subtitle">{{ unit.titleZh }}</span>
              <span class="unit-card__status">
                {{ unit.available ? 'Ready' : 'Coming soon' }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </aside>

    <main class="content">
      <section v-if="isMobileViewport" class="mobile-toolbar">
        <button
          class="mobile-toolbar__button"
          type="button"
          @click="showMobileRoadmap = true"
        >
          打开课程目录
        </button>
        <div class="mobile-toolbar__meta">
          <span class="mobile-toolbar__label">当前内容</span>
          <strong class="mobile-toolbar__value">
            Unit {{ activeUnit.unitNumber }} · {{ activeDisplayUnit.titleEn }}
          </strong>
        </div>
      </section>

      <section class="hero-card">
        <div class="hero-card__main">
          <div class="hero-card__heading">
            <p class="hero-card__eyebrow">
              {{ activeUnit.bandCode }} · {{ activeUnit.levelTitle }} · Unit {{ activeUnit.unitNumber }}
            </p>
            <h2 class="hero-card__title">{{ activeDisplayUnit.titleEn }}</h2>
            <p class="hero-card__subtitle">{{ activeDisplayUnit.titleZh }}</p>
          </div>

          <div class="hero-card__summary">
            <p class="hero-card__summary-item">{{ activeDisplayUnit.summaryEn }}</p>
            <p class="hero-card__summary-item hero-card__summary-item--zh">{{ activeDisplayUnit.summaryZh }}</p>
          </div>

          <div class="hero-card__stats">
            <div class="stat-card">
              <span class="stat-card__label">Dialogues</span>
              <strong class="stat-card__value">{{ activeDisplayUnit.dialogues.length }}</strong>
            </div>
            <div class="stat-card">
              <span class="stat-card__label">Articles</span>
              <strong class="stat-card__value">{{ activeDisplayUnit.articles.length }}</strong>
            </div>
            <div class="stat-card">
              <span class="stat-card__label">Sentence drills</span>
              <strong class="stat-card__value">{{ activeSentenceGroup.items.length }}</strong>
            </div>
          </div>
        </div>
      </section>

      <section class="control-card">
        <div class="control-card__actions">
          <button class="secondary-button" type="button" @click="showChinese = !showChinese">
            {{ showChinese ? '隐藏中文' : '显示中文' }}
          </button>
          <button class="secondary-button" type="button" @click="showEnglish = !showEnglish">
            {{ showEnglish ? '隐藏英文' : '显示英文' }}
          </button>
        </div>

        <div class="control-card__selectors">
          <label class="field field--small">
            <span class="field__label">朗读速度</span>
            <select v-model="playbackRate" class="field__input">
              <option value="1">1.0x</option>
              <option value="1.3">1.3x</option>
              <option value="1.5">1.5x</option>
            </select>
          </label>
        </div>
      </section>

      <section class="group-card">
        <div class="group-card__header">
          <div>
            <p class="group-card__eyebrow">Practice 01</p>
            <h2 class="group-card__title">Dialogues</h2>
          </div>
          <span class="group-card__meta">3 short conversations</span>
        </div>

        <div class="group-card__list">
          <ContentSection
            v-for="section in activeDisplayUnit.dialogues"
            :key="section.id"
            :section="section"
            :show-english="showEnglish"
            :show-chinese="showChinese"
            :active-line-id="activeLineId"
            :active-block-id="activeBlockId"
            @play-line="handlePlayLine"
            @play-section="handlePlaySection"
          />
        </div>
      </section>

      <section class="group-card">
        <div class="group-card__header">
          <div>
            <p class="group-card__eyebrow">Practice 02</p>
            <h2 class="group-card__title">Articles</h2>
          </div>
          <span class="group-card__meta">2 short readings</span>
        </div>

        <div class="group-card__list">
          <ContentSection
            v-for="section in activeDisplayUnit.articles"
            :key="section.id"
            :section="section"
            :show-english="showEnglish"
            :show-chinese="showChinese"
            :active-line-id="activeLineId"
            :active-block-id="activeBlockId"
            @play-line="handlePlayLine"
            @play-section="handlePlaySection"
          />
        </div>
      </section>

      <section class="group-card">
        <div class="group-card__header">
          <div>
            <p class="group-card__eyebrow">Practice 03</p>
            <h2 class="group-card__title">Sentences</h2>
          </div>
          <span class="group-card__meta">{{ activeSentenceGroup.items.length }} sentences</span>
        </div>

        <div class="group-card__list">
          <SentenceBlock
            :group="activeSentenceGroup"
            :show-text="showSentenceText"
            :active-item-id="activeLineId"
            @play-item="handlePlaySentence"
            @play-group="handlePlaySentenceGroup"
            @toggle-text="showSentenceText = !showSentenceText"
          />
        </div>
      </section>
    </main>
  </div>
</template>

<style lang="less" scoped>
.page-shell {
  width: min(1500px, 100%);
  min-height: 100vh;
  margin: 0 auto;
  padding: 24px;
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 20px;
  background:
    radial-gradient(circle at top left, rgba(139, 92, 246, 0.1), transparent 26%),
    linear-gradient(180deg, #faf8ff 0%, #f7f9fc 100%);
}

.mobile-backdrop {
  position: fixed;
  inset: 0;
  z-index: 20;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(4px);
}

.sidebar {
  position: sticky;
  top: 24px;
  height: calc(100vh - 48px);
  overflow: auto;
  padding: 22px 18px 24px;
  box-sizing: border-box;
  border: 1px solid #ece4ff;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(14px);
}

.sidebar__top {
  margin-bottom: 22px;
}

.sidebar__top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.sidebar__close {
  border: none;
  border-radius: 999px;
  padding: 10px 12px;
  background: #f5f3ff;
  color: #5b21b6;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.sidebar__eyebrow,
.hero-card__eyebrow,
.group-card__eyebrow {
  margin: 0 0 10px;
  color: #7c3aed;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.sidebar__title {
  margin: 0;
  color: #111827;
  font-size: 24px;
  line-height: 1.25;
}

.sidebar__desc {
  margin: 12px 0 0;
  color: #6b7280;
  font-size: 14px;
  line-height: 1.7;
}

.sidebar__roadmap {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.band-card {
  padding: 16px;
  border: 1px solid #ece8f8;
  border-radius: 20px;
  background: #ffffff;
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.04);
}

.band-card__header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: start;
  margin-bottom: 12px;
}

.band-card__code {
  margin: 0 0 6px;
  color: #7c3aed;
  font-size: 12px;
  font-weight: 800;
}

.band-card__title {
  margin: 0;
  color: #111827;
  font-size: 18px;
}

.band-card__subtitle {
  padding: 6px 10px;
  border-radius: 999px;
  background: #f5f3ff;
  color: #6d28d9;
  font-size: 12px;
  font-weight: 700;
}

.level-card {
  display: flex;
  flex-direction: column;
  gap: 8px;

  & + & {
    margin-top: 14px;
  }
}

.level-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.level-card__title {
  margin: 0;
  color: #374151;
  font-size: 15px;
}

.level-card__meta {
  color: #9ca3af;
  font-size: 12px;
}

.unit-card {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: start;
  gap: 4px;
  padding: 12px 14px;
  border: 1px solid #ebe5ff;
  border-radius: 14px;
  background: #fcfbff;
  cursor: pointer;
  text-align: left;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    background 0.2s ease;

  &:hover:enabled {
    transform: translateY(-1px);
    border-color: #8b5cf6;
    background: #f7f2ff;
  }
}

.unit-card--active {
  border-color: #7c3aed;
  background: #f3ecff;
  box-shadow: 0 10px 20px rgba(124, 58, 237, 0.12);
}

.unit-card--locked {
  opacity: 0.6;
  cursor: not-allowed;
}

.unit-card__number {
  color: #7c3aed;
  font-size: 12px;
  font-weight: 800;
}

.unit-card__title {
  color: #1f2937;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.45;
}

.unit-card__subtitle {
  color: #6b7280;
  font-size: 12px;
}

.unit-card__status {
  margin-top: 4px;
  color: #9ca3af;
  font-size: 11px;
  font-weight: 700;
}

.content {
  min-width: 0;
  max-width: 980px;
  padding: 8px 0 32px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.mobile-toolbar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 18px;
  border: 1px solid #ece8f8;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.04);
}

.mobile-toolbar__button {
  min-height: 44px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%);
  color: #ffffff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.mobile-toolbar__meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mobile-toolbar__label {
  color: #9ca3af;
  font-size: 12px;
  font-weight: 700;
}

.mobile-toolbar__value {
  color: #111827;
  font-size: 16px;
  line-height: 1.4;
}

.hero-card,
.control-card,
.group-card {
  padding: 22px;
  border: 1px solid #ece8f8;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.04);
}

.hero-card__main {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.hero-card__heading {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.hero-card__title {
  margin: 0;
  color: #111827;
  font-size: 34px;
  line-height: 1.1;
}

.hero-card__subtitle {
  margin: 0;
  color: #7c3aed;
  font-size: 18px;
  font-weight: 700;
}

.hero-card__summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hero-card__summary-item {
  margin: 0;
  color: #374151;
  font-size: 15px;
  line-height: 1.7;
}

.hero-card__summary-item--zh {
  color: #6b7280;
}

.hero-card__stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.stat-card {
  padding: 14px 16px;
  border-radius: 18px;
  background: linear-gradient(180deg, #faf7ff 0%, #f5f0ff 100%);
}

.stat-card__label {
  display: block;
  color: #6b7280;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.stat-card__value {
  display: block;
  margin-top: 10px;
  color: #4c1d95;
  font-size: 28px;
}

.control-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mode-switch {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.mode-button {
  border: none;
  border-radius: 999px;
  padding: 10px 14px;
  background: #f5f3ff;
  color: #5b21b6;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    background 0.2s ease,
    color 0.2s ease;

  &:hover {
    transform: translateY(-1px);
  }
}

.mode-button--active {
  background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%);
  color: #ffffff;
}

.mode-note {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.mode-note__text {
  color: #6b7280;
  font-size: 13px;
  line-height: 1.6;
}

.control-card__actions,
.control-card__selectors,
.control-card__status {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.primary-button,
.secondary-button {
  border: none;
  border-radius: 12px;
  padding: 11px 15px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    background 0.2s ease;

  &:hover {
    transform: translateY(-1px);
  }
}

.primary-button {
  background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%);
  color: #ffffff;
}

.secondary-button {
  background: #f5f3ff;
  color: #5b21b6;
}

.field {
  min-width: 250px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field--small {
  min-width: 140px;
}

.field__label {
  color: #6b7280;
  font-size: 12px;
  font-weight: 700;
}

.field__input {
  height: 42px;
  padding: 0 14px;
  border: 1px solid #ddd6fe;
  border-radius: 12px;
  background: #ffffff;
  color: #111827;
  font-size: 14px;
  outline: none;

  &:focus {
    border-color: #7c3aed;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.12);
  }
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  background: #f5f3ff;
  color: #6d28d9;
  font-size: 12px;
  font-weight: 700;
}

.status-pill--female {
  background: #fff7e8;
  color: #9a6700;
}

.status-pill--male {
  background: #eff6ff;
  color: #1d4ed8;
}

.status-pill--mode {
  background: #f3ecff;
  color: #6d28d9;
}

.status-pill--warn {
  background: #fff7ed;
  color: #c2410c;
}

.status-pill--quiet {
  background: #edfdf3;
  color: #15803d;
}

.status-pill--notice {
  background: #fff7ed;
  color: #b45309;
}

.group-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.group-card__title {
  margin: 0;
  color: #111827;
  font-size: 28px;
}

.group-card__meta {
  color: #6b7280;
  font-size: 14px;
  font-weight: 600;
}

.group-card__list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

@media (max-width: 1280px) {
  .page-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
    height: auto;
  }

  .content {
    max-width: none;
  }
}

@media (max-width: 900px) {
  .page-shell {
    padding: 16px;
    gap: 16px;
  }

  .sidebar--drawer {
    position: fixed;
    top: 12px;
    left: 12px;
    right: 12px;
    bottom: 12px;
    z-index: 30;
    height: auto;
    border-radius: 22px;
    overflow: auto;
  }

  .hero-card,
  .control-card,
  .group-card {
    padding: 18px;
    border-radius: 20px;
  }

  .hero-card__stats {
    grid-template-columns: 1fr;
  }

  .control-card__actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .control-card__selectors {
    flex-direction: column;
  }

  .field,
  .field--small {
    min-width: 0;
    width: 100%;
  }

  .primary-button,
  .secondary-button,
  .mode-button {
    min-height: 44px;
  }

  .group-card__header {
    flex-direction: column;
    align-items: start;
  }
}

@media (max-width: 768px) {
  .page-shell {
    padding: 14px;
    gap: 14px;
  }

  .hero-card,
  .control-card,
  .group-card {
    padding: 18px;
    border-radius: 20px;
  }

  .hero-card__title {
    font-size: 28px;
  }

  .hero-card__stats {
    grid-template-columns: 1fr;
  }

  .group-card__header {
    flex-direction: column;
    align-items: start;
  }

  .group-card__title {
    font-size: 24px;
  }

  .mode-switch {
    display: grid;
    grid-template-columns: 1fr;
  }

  .control-card__actions {
    grid-template-columns: 1fr;
  }

  .control-card__status {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
