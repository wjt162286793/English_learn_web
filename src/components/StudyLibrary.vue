<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { LessonLine } from '../types/course'
import type { StudyItem, StudyParagraph, StudySection } from '../data/studyLibrary'

interface Props {
  mode: 'vocabulary' | 'reading' | 'professional'
  sections: StudySection[]
  showEnglish: boolean
  showChinese: boolean
  activeLineId: string
  navigationResetKey?: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (event: 'play-line', line: LessonLine): void
  (event: 'play-word', line: LessonLine): void
  (event: 'play-lines', lines: LessonLine[], blockId: string): void
  (event: 'section-change', section: StudySection | null): void
}>()

const activeSectionId = ref('')
const search = ref('')
const categorySearch = ref('')
const failedImageIds = ref<Set<string>>(new Set())
const itemVisibility = ref<Record<string, { word: boolean; sentence: boolean }>>({})
const paragraphVisibility = ref<Record<string, boolean>>({})

watch(
  () => props.showEnglish,
  () => {
    itemVisibility.value = {}
    paragraphVisibility.value = {}
  },
)

watch(
  () => props.sections.map((section) => section.id).join('|'),
  () => {
    activeSectionId.value = props.sections[0]?.id ?? ''
    failedImageIds.value = new Set()
    categorySearch.value = ''
    itemVisibility.value = {}
    paragraphVisibility.value = {}
  },
  { immediate: true },
)

watch(
  () => props.navigationResetKey,
  () => {
    activeSectionId.value = props.sections[0]?.id ?? ''
    search.value = ''
    categorySearch.value = ''
  },
)

watch(
  () =>
    `${activeSectionId.value}|${search.value.trim()}|${props.sections
      .map((section) => section.id)
      .join('|')}`,
  () => {
    const section = search.value.trim()
      ? null
      : (props.sections.find((candidate) => candidate.id === activeSectionId.value) ?? null)
    emit('section-change', section)
  },
  { immediate: true },
)

const visibleCategorySections = computed(() => {
  const query = categorySearch.value.trim().toLocaleLowerCase()
  if (!query) {
    return props.sections
  }
  return props.sections.filter((section) =>
    `${section.titleEn} ${section.titleZh}`.toLocaleLowerCase().includes(query),
  )
})

const categoryTitle = computed(() => {
  if (props.mode === 'vocabulary') {
    return '词汇分类'
  }
  return props.mode === 'reading' ? '文章分类' : '专业分类'
})

const categoryEyebrow = computed(() => {
  if (props.mode === 'vocabulary') {
    return 'WORD BANK'
  }
  return props.mode === 'reading' ? 'READ & LISTEN' : 'FOCUSED PRACTICE'
})

const matchingSections = computed(() => {
  const query = search.value.trim().toLocaleLowerCase()
  if (!query) {
    return props.sections.filter((section) => section.id === activeSectionId.value)
  }

  return props.sections
    .map((section) => ({
      ...section,
      items: section.items.filter((item) => itemMatches(item, query)),
    }))
    .filter(
      (section) =>
        section.items.length > 0 ||
        `${section.titleEn} ${section.titleZh}`.toLocaleLowerCase().includes(query),
    )
})

const totalItems = computed(() =>
  props.sections.reduce((count, section) => count + section.items.length, 0),
)

const visibleItemCount = computed(() =>
  matchingSections.value.reduce((count, section) => count + section.items.length, 0),
)

function itemMatches(item: StudyItem, query: string): boolean {
  const content = [
    item.titleEn,
    item.titleZh,
    item.detail,
    item.line?.textEn,
    item.line?.textZh,
    ...(item.paragraphs ?? []).flatMap((paragraph) => [
      paragraph.translation,
      ...paragraph.sentences.map((sentence) => sentence.textEn),
    ]),
  ]
    .filter(Boolean)
    .join(' ')
    .toLocaleLowerCase()
  return content.includes(query)
}

function sectionLines(section: StudySection): LessonLine[] {
  return section.items.flatMap((item) => itemLines(item))
}

function itemLines(item: StudyItem): LessonLine[] {
  return [
    ...(item.line ? [item.line] : []),
    ...(item.paragraphs ?? []).flatMap((paragraph) => paragraph.sentences),
  ]
}

function playSection(section: StudySection): void {
  emit('play-lines', sectionLines(section), section.id)
}

function playItem(item: StudyItem): void {
  const lines = itemLines(item)
  if (lines.length > 1) {
    emit('play-lines', lines, item.id)
  } else if (lines[0]) {
    emit('play-line', lines[0])
  }
}

function playParagraph(item: StudyItem, paragraphIndex: number): void {
  const paragraph = item.paragraphs?.[paragraphIndex]
  if (paragraph) {
    emit('play-lines', paragraph.sentences, paragraph.id)
  }
}

function itemIsVisible(item: StudyItem, field: 'word' | 'sentence'): boolean {
  return itemVisibility.value[item.id]?.[field] ?? props.showEnglish
}

function toggleItemVisibility(item: StudyItem, field: 'word' | 'sentence'): void {
  const current = itemVisibility.value[item.id] ?? {
    word: props.showEnglish,
    sentence: props.showEnglish,
  }
  itemVisibility.value = {
    ...itemVisibility.value,
    [item.id]: { ...current, [field]: !current[field] },
  }
}

function paragraphIsVisible(paragraph: StudyParagraph): boolean {
  return paragraphVisibility.value[paragraph.id] ?? props.showEnglish
}

function toggleParagraphVisibility(paragraph: StudyParagraph): void {
  paragraphVisibility.value = {
    ...paragraphVisibility.value,
    [paragraph.id]: !paragraphIsVisible(paragraph),
  }
}

function playWord(item: StudyItem): void {
  if (item.wordLine) {
    emit('play-word', item.wordLine)
  }
}

function playExample(item: StudyItem): void {
  if (item.line) {
    emit('play-line', item.line)
  }
}

function markImageUnavailable(itemId: string): void {
  failedImageIds.value = new Set(failedImageIds.value).add(itemId)
}

function hasImage(item: StudyItem): boolean {
  return Boolean(item.imageUrl && !failedImageIds.value.has(item.id))
}

function imageFallback(item: StudyItem): string {
  if (itemIsVisible(item, 'word')) {
    return item.titleEn
  }
  return props.showChinese ? item.titleZh : '内容已隐藏'
}
</script>

<template>
  <section class="study-library study-library--categorized">
    <aside class="category-sidebar">
      <div class="category-sidebar__heading">
        <div>
          <p class="library-eyebrow">{{ categoryEyebrow }}</p>
          <h2>{{ categoryTitle }}</h2>
        </div>
        <span>{{ sections.length }}</span>
      </div>
      <label class="category-search">
        <span aria-hidden="true">⌕</span>
        <input v-model="categorySearch" type="search" placeholder="搜索分类" />
      </label>
      <nav class="library-categories library-categories--vertical" :aria-label="categoryTitle">
        <button
          v-for="section in visibleCategorySections"
          :key="section.id"
          class="category-chip"
          :class="{ 'category-chip--active': activeSectionId === section.id && !search }"
          :aria-pressed="activeSectionId === section.id && !search"
          type="button"
          @click="(activeSectionId = section.id), (search = '')"
        >
          <span class="category-chip__title">{{ section.titleEn }}</span>
          <small>{{ section.items.length }}</small>
        </button>
        <p v-if="visibleCategorySections.length === 0" class="category-empty">
          没有匹配的分类
        </p>
      </nav>
    </aside>

    <div class="library-main">
      <div class="library-tools">
        <label class="library-search">
          <span aria-hidden="true">⌕</span>
          <input
            v-model="search"
            type="search"
            :placeholder="mode === 'vocabulary' ? '搜索单词、短语或例句' : '搜索主题或正文'"
          />
        </label>
        <span class="library-count">
          {{ visibleItemCount.toLocaleString() }} / {{ totalItems.toLocaleString() }} 项
        </span>
      </div>

      <div v-if="matchingSections.length === 0" class="empty-state">
        没找到匹配内容，试试更短的关键词。
      </div>

      <section
        v-for="section in matchingSections"
        :key="section.id"
        class="library-section"
      >
        <header class="library-section__header">
          <div>
            <p class="library-eyebrow">
              {{ mode === 'professional' ? 'FOCUSED PRACTICE' : mode === 'reading' ? 'READ & LISTEN' : 'WORD BANK' }}
            </p>
            <h2>{{ section.titleEn }}</h2>
            <p v-if="showChinese && section.titleZh">{{ section.titleZh }}</p>
          </div>
          <button
            class="play-all"
            type="button"
            :disabled="sectionLines(section).length === 0"
            @click="playSection(section)"
          >
            ▶ 听本组
          </button>
        </header>

        <div
          v-for="item in section.items"
          :key="item.id"
          class="study-item"
          :class="{
            'study-item--article': item.paragraphs?.length,
            'study-item--vocabulary': mode === 'vocabulary',
          }"
        >
          <template v-if="item.paragraphs?.length">
            <header class="article-heading">
              <span class="article-index">{{ item.id.slice(-2) }}</span>
              <div>
                <h3>{{ item.titleEn }}</h3>
                <p v-if="item.detail">{{ item.detail }}</p>
              </div>
              <button class="item-play" type="button" @click="playItem(item)">
                ▶ 听全文
              </button>
            </header>

            <div
              v-for="(paragraph, paragraphIndex) in item.paragraphs"
              :key="paragraph.id"
              class="reading-paragraph"
            >
              <header class="reading-paragraph__header">
                <span>第 {{ paragraphIndex + 1 }} 段</span>
                <div class="reading-paragraph__actions">
                  <button
                    class="text-action"
                    type="button"
                    @click="toggleParagraphVisibility(paragraph)"
                  >
                    {{ paragraphIsVisible(paragraph) ? '隐藏本段' : '显示本段' }}
                  </button>
                  <button
                    class="paragraph-play"
                    type="button"
                    @click="playParagraph(item, paragraphIndex)"
                  >
                    ▶ 播放本段
                  </button>
                </div>
              </header>

              <div v-if="paragraphIsVisible(paragraph)" class="reading-paragraph__sentences">
                <div
                  v-for="sentence in paragraph.sentences"
                  :key="sentence.id"
                  class="reading-sentence"
                  :class="{ 'reading-sentence--active': activeLineId === sentence.id }"
                >
                  <p class="reading-sentence__text">{{ sentence.textEn }}</p>
                  <button
                    class="sentence-play"
                    type="button"
                    :aria-label="`播放：${sentence.textEn}`"
                    @click="emit('play-line', sentence)"
                  >
                    ▶
                  </button>
                </div>
              </div>
              <p v-else class="paragraph-hidden">
                本段英文已隐藏，仍可播放本段进行听力练习。
              </p>
              <p v-if="showChinese && paragraph.translation" class="reading-paragraph__translation">
                {{ paragraph.translation }}
              </p>
            </div>
          </template>

          <template v-else>
            <div v-if="mode === 'vocabulary'" class="word-visual">
              <img
                v-if="hasImage(item)"
                :src="item.imageUrl"
                :alt="item.titleEn"
                loading="lazy"
                @error="markImageUnavailable(item.id)"
              />
              <span v-else class="word-visual__fallback">{{ imageFallback(item) }}</span>
            </div>

            <div class="study-item__content">
              <template v-if="mode === 'vocabulary'">
                <section class="vocabulary-part">
                  <div class="vocabulary-part__copy">
                    <span class="vocabulary-part__label">单词 / 短语</span>
                    <h3 v-if="itemIsVisible(item, 'word')">{{ item.titleEn }}</h3>
                    <p v-else class="study-item__hidden">单词已隐藏</p>
                    <p v-if="showChinese && item.titleZh" class="study-item__meaning">
                      {{ item.titleZh }}
                    </p>
                  </div>
                  <div class="vocabulary-part__actions">
                    <button
                      class="text-action"
                      type="button"
                      @click="toggleItemVisibility(item, 'word')"
                    >
                      {{ itemIsVisible(item, 'word') ? '隐藏单词' : '显示单词' }}
                    </button>
                    <button
                      class="sound-action"
                      :class="{ 'sound-action--active': activeLineId === item.wordLine?.id }"
                      type="button"
                      :disabled="!item.wordLine"
                      @click="playWord(item)"
                    >
                      <svg viewBox="0 0 24 24" aria-hidden="true">
                        <path d="M4 9v6h4l5 4V5L8 9H4Zm12.5 3a4.5 4.5 0 0 0-2.5-4.04v8.08a4.5 4.5 0 0 0 2.5-4.04ZM14 3.23v2.06a7 7 0 0 1 0 13.42v2.06a9 9 0 0 0 0-17.54Z" />
                      </svg>
                      单词发音
                    </button>
                  </div>
                </section>

                <section v-if="item.line" class="vocabulary-part vocabulary-part--sentence">
                  <div class="vocabulary-part__heading">
                    <span class="vocabulary-part__label">例句</span>
                    <div class="vocabulary-part__actions">
                      <button
                        class="text-action"
                        type="button"
                        @click="toggleItemVisibility(item, 'sentence')"
                      >
                        {{ itemIsVisible(item, 'sentence') ? '隐藏句子' : '显示句子' }}
                      </button>
                      <button
                        class="sound-action"
                        :class="{ 'sound-action--active': activeLineId === item.line.id }"
                        type="button"
                        @click="playExample(item)"
                      >
                        <svg viewBox="0 0 24 24" aria-hidden="true">
                          <path d="M4 9v6h4l5 4V5L8 9H4Zm12.5 3a4.5 4.5 0 0 0-2.5-4.04v8.08a4.5 4.5 0 0 0 2.5-4.04ZM14 3.23v2.06a7 7 0 0 1 0 13.42v2.06a9 9 0 0 0 0-17.54Z" />
                        </svg>
                        句子发音
                      </button>
                    </div>
                  </div>
                  <p v-if="itemIsVisible(item, 'sentence')" class="study-item__example">
                    {{ item.line.textEn }}
                  </p>
                  <p v-else class="study-item__hidden">
                    句子已隐藏 · 可点击“句子发音”练习听力
                  </p>
                  <p v-if="showChinese && item.line.textZh" class="study-item__translation">
                    {{ item.line.textZh }}
                  </p>
                </section>
              </template>

              <template v-else>
                <div class="study-item__heading">
                  <h3 v-if="showEnglish">{{ item.titleEn }}</h3>
                  <span v-if="showChinese && item.titleZh" class="study-item__meaning">
                    {{ item.titleZh }}
                  </span>
                </div>
                <p v-if="item.detail" class="study-item__detail">{{ item.detail }}</p>
                <template v-if="item.line">
                  <p v-if="showEnglish" class="study-item__example">{{ item.line.textEn }}</p>
                  <p v-else class="study-item__hidden">英文已隐藏 · 点击播放练习听力</p>
                  <p v-if="showChinese && item.line.textZh" class="study-item__translation">
                    {{ item.line.textZh }}
                  </p>
                </template>
              </template>
            </div>
            <button
              v-if="mode !== 'vocabulary' && itemLines(item).length"
              class="item-play"
              type="button"
              @click="playItem(item)"
            >
              ▶ 播放
            </button>
          </template>
        </div>
      </section>
    </div>
  </section>
</template>

<style lang="less" scoped>
.study-library {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.study-library--categorized {
  display: grid;
  grid-template-columns: 252px minmax(0, 1fr);
  align-items: start;
  gap: 20px;
}

.library-main {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.category-sidebar {
  position: sticky;
  top: 16px;
  max-height: calc(100vh - 32px);
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 17px 13px 13px;
  overflow: hidden;
  border: 1px solid #e7e1f1;
  border-radius: 20px;
  background: #ffffff;
  box-shadow: 0 10px 26px rgba(38, 27, 58, 0.045);
}

.category-sidebar__heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 0 5px;

  h2 {
    margin: 0;
    color: #211a2e;
    font-size: 19px;
  }

  > span {
    display: grid;
    min-width: 28px;
    height: 28px;
    place-items: center;
    border-radius: 9px;
    background: #f1edff;
    color: #6849c0;
    font-size: 12px;
    font-weight: 800;
  }
}

.category-search {
  min-height: 40px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 10px;
  border: 1px solid #e7e1f1;
  border-radius: 11px;
  background: #faf9fc;
  color: #8b7f9b;

  span {
    font-size: 20px;
  }

  input {
    width: 100%;
    min-width: 0;
    border: 0;
    outline: 0;
    background: transparent;
    color: #282331;
    font: inherit;
    font-size: 13px;
  }

  &:focus-within {
    border-color: #9b82df;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.09);
  }
}

.library-tools {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 14px;
  border: 1px solid #e9e3f3;
  border-radius: 18px;
  background: #fff;
}

.library-search {
  min-width: 0;
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #8b7f9b;

  span {
    font-size: 22px;
  }

  input {
    width: 100%;
    border: 0;
    outline: 0;
    color: #282331;
    font: inherit;
    font-size: 14px;
    background: transparent;
  }
}

.library-count {
  flex: none;
  color: #776e82;
  font-size: 12px;
}

.library-categories {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 2px 1px 8px;
  scrollbar-width: thin;
}

.library-categories--vertical {
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 5px;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 0 2px 2px 0;
}

.category-chip {
  flex: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 38px;
  padding: 8px 12px;
  border: 1px solid #e9e3f3;
  border-radius: 999px;
  background: #fff;
  color: #5d536b;
  font: inherit;
  font-size: 12px;
  cursor: pointer;

  small {
    display: inline-grid;
    min-width: 20px;
    height: 20px;
    place-items: center;
    border-radius: 99px;
    background: #f1edf7;
    color: #766b83;
  }

  &:hover {
    border-color: #a78bfa;
  }
}

.library-categories--vertical .category-chip {
  width: 100%;
  min-width: 0;
  justify-content: space-between;
  flex: none;
  gap: 8px;
  min-height: 39px;
  padding: 7px 9px;
  border-color: transparent;
  border-radius: 10px;
  background: transparent;
  text-align: left;

  &:hover {
    border-color: #eee8f8;
    background: #faf9fd;
  }
}

.category-chip__title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-empty {
  margin: 0;
  padding: 10px 8px;
  color: #8b8296;
  font-size: 12px;
}

.category-chip--active {
  border-color: #7551d8;
  background: #f2edff;
  color: #5839b8;
  font-weight: 700;
}

.category-chip--active small {
  background: #e2d8ff;
  color: #5839b8;
}

.library-categories--vertical .category-chip--active {
  border-color: #e5dcff;
  background: #f3efff;
}

.library-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.library-section__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 22px;
  border: 1px solid #e9e3f3;
  border-radius: 20px;
  background: linear-gradient(120deg, #fff 15%, #f4f0ff 100%);

  h2 {
    margin: 0;
    color: #211a2e;
    font-size: 21px;
    font-weight: 750;
  }

  p:last-child {
    margin-top: 5px;
    color: #786f83;
    font-size: 13px;
  }
}

.library-eyebrow {
  margin: 0 0 7px;
  color: #7651d4;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.15em;
}

.play-all,
.item-play,
.paragraph-play,
.sentence-play {
  flex: none;
  border: 0;
  border-radius: 999px;
  background: #eee8ff;
  color: #5d3bb6;
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;

  &:hover:not(:disabled) {
    background: #ded3ff;
  }

  &:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }
}

.play-all,
.item-play,
.paragraph-play {
  padding: 9px 13px;
}

.study-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 17px 18px;
  border: 1px solid #ece8f2;
  border-radius: 17px;
  background: #fff;
  box-shadow: 0 7px 20px rgba(38, 27, 58, 0.035);
}

.study-item--vocabulary {
  align-items: flex-start;
  gap: 17px;
  padding: 16px;
}

.word-visual {
  width: 72px;
  height: 72px;
  flex: none;
  overflow: hidden;
  display: grid;
  place-items: center;
  border-radius: 14px;
  background: linear-gradient(145deg, #f3edff, #e8f3ff);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.word-visual__fallback {
  padding: 6px;
  color: #7052c5;
  font-size: 12px;
  font-weight: 800;
  line-height: 1.3;
  text-align: center;
}

.study-item__content {
  min-width: 0;
  flex: 1;
}

.vocabulary-part {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.vocabulary-part--sentence {
  align-items: flex-start;
  flex-direction: column;
  gap: 7px;
  margin-top: 13px;
  padding-top: 12px;
  border-top: 1px solid #f0edf4;
}

.vocabulary-part__copy {
  min-width: 0;

  h3 {
    margin: 3px 0 0;
    color: #282331;
    font-size: 19px;
    line-height: 1.35;
    overflow-wrap: anywhere;
  }
}

.vocabulary-part__label {
  color: #958ba2;
  font-size: 11px;
  font-weight: 750;
  letter-spacing: 0.04em;
}

.vocabulary-part__heading,
.vocabulary-part__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.vocabulary-part__actions {
  flex: none;
  flex-wrap: wrap;
}

.text-action,
.sound-action {
  min-height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 7px 10px;
  border: 1px solid #e5deef;
  border-radius: 10px;
  background: #ffffff;
  color: #62586f;
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
  transition: border-color 0.18s ease, background 0.18s ease, color 0.18s ease;

  &:hover:not(:disabled) {
    border-color: #b6a5e2;
    background: #f8f5ff;
    color: #5839b8;
  }

  &:focus-visible {
    outline: 3px solid rgba(124, 58, 237, 0.2);
    outline-offset: 2px;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.sound-action {
  border-color: #ded4fb;
  background: #f4f0ff;
  color: #5839b8;

  svg {
    width: 16px;
    height: 16px;
    fill: currentColor;
  }
}

.sound-action--active {
  border-color: #7651d4;
  background: #7651d4;
  color: #ffffff;
}

.vocabulary-part__copy .study-item__meaning {
  display: block;
  margin-top: 5px;
}

.vocabulary-part--sentence .study-item__example,
.vocabulary-part--sentence .study-item__hidden {
  margin-top: 0;
}

.study-item__heading {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 8px 12px;

  h3 {
    margin: 0;
    color: #282331;
    font-size: 17px;
    line-height: 1.4;
  }
}

.study-item__meaning {
  color: #795fba;
  font-size: 13px;
}

.study-item__detail {
  margin-top: 4px;
  color: #7b7185;
  font-size: 12px;
}

.study-item__example,
.reading-sentence__text {
  margin: 8px 0 0;
  color: #3d3747;
  font-size: 14px;
  line-height: 1.7;
}

.study-item__translation {
  margin-top: 4px;
  color: #7b7185;
  font-size: 13px;
  line-height: 1.65;
}

.study-item__hidden,
.reading-sentence__hidden {
  margin: 8px 0 0;
  color: #a098aa;
  font-size: 13px;
}

.study-item--article {
  display: block;
  padding: 20px 22px;
}

.article-heading {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 14px;
  border-bottom: 1px solid #eeeaf3;

  h3 {
    margin: 0;
    color: #292332;
    font-size: 18px;
    line-height: 1.4;
  }

  p {
    margin-top: 3px;
    color: #877d91;
    font-size: 12px;
  }

  .item-play {
    margin-left: auto;
  }
}

.article-index {
  display: grid;
  width: 38px;
  height: 38px;
  flex: none;
  place-items: center;
  border-radius: 12px;
  background: #f1edff;
  color: #6849c0;
  font-size: 12px;
  font-weight: 800;
}

.reading-paragraph {
  padding: 14px 0 12px;
  border-bottom: 1px solid #f0edf4;

  &:last-child {
    border-bottom: 0;
  }
}

.reading-paragraph__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 0 8px 8px;
  color: #8b8296;
  font-size: 11px;
  font-weight: 750;
}

.reading-paragraph__actions {
  display: flex;
  align-items: center;
  gap: 7px;
}

.reading-paragraph__actions .text-action,
.reading-paragraph__actions .paragraph-play {
  min-height: 32px;
  padding: 6px 9px;
  font-size: 11px;
}

.paragraph-hidden {
  margin: 0 8px;
  padding: 13px;
  border-radius: 10px;
  background: #faf9fc;
  color: #9990a4;
  font-size: 12px;
}

.reading-sentence {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 3px 8px;
  border-radius: 9px;
}

.reading-sentence--active {
  background: #f4f0ff;
}

.reading-sentence__text,
.reading-sentence__hidden {
  min-width: 0;
  flex: 1;
  margin: 0;
  color: #3d3747;
  font-size: 14px;
  line-height: 1.75;
}

.reading-sentence__hidden {
  color: #a098aa;
}

.sentence-play {
  width: 32px;
  height: 32px;
  margin-top: 3px;
  background: #f4f1f9;
}

.reading-paragraph__translation {
  margin: 9px 8px 0;
  color: #756c80;
  font-size: 13px;
  line-height: 1.8;
}

.paragraph-play {
  margin: 10px 8px 0;
  background: #f4f1f9;
}

.empty-state {
  padding: 36px 20px;
  border: 1px dashed #d8d0e4;
  border-radius: 18px;
  color: #81778c;
  text-align: center;
}

@media (max-width: 650px) {
  .study-library--categorized {
    grid-template-columns: minmax(0, 1fr);
  }

  .category-sidebar {
    position: static;
    max-height: none;
  }

  .library-categories--vertical {
    max-height: 220px;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    align-content: start;
  }

  .library-tools {
    align-items: flex-start;
    flex-direction: column;
  }

  .library-search {
    width: 100%;
  }

  .library-section__header {
    align-items: flex-start;
    padding: 17px;
  }

  .library-section__header h2 {
    font-size: 18px;
  }

  .study-item {
    gap: 11px;
    padding: 14px;
  }

  .study-item--vocabulary {
    align-items: flex-start;
    gap: 10px;
  }

  .vocabulary-part {
    align-items: flex-start;
    flex-direction: column;
    gap: 9px;
  }

  .vocabulary-part__actions {
    width: 100%;
  }

  .vocabulary-part__actions > button {
    flex: 1;
  }

  .vocabulary-part__heading {
    width: 100%;
    align-items: flex-start;
  }

  .vocabulary-part__heading .vocabulary-part__actions {
    width: auto;
    justify-content: flex-end;
  }

  .word-visual {
    width: 54px;
    height: 54px;
  }

  .word-visual__fallback {
    font-size: 18px;
  }

  .study-item__heading h3 {
    font-size: 15px;
  }

  .study-item > .item-play {
    padding: 8px 10px;
  }

  .study-item--article {
    padding: 14px;
  }

  .article-heading {
    align-items: flex-start;
  }

  .article-heading h3 {
    font-size: 16px;
  }
}
</style>
