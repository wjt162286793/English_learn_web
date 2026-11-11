<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { SentenceGroup, SentenceItem } from '../types/course'

interface Props {
  group: SentenceGroup
  showText: boolean
  activeItemId: string
}

interface BoldSegment {
  text: string
  bold: boolean
}

interface QuizToken {
  text: string
  blankIndex: number
}

interface QuizModel {
  item: SentenceItem
  tokens: QuizToken[]
  targets: string[]
  hint: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (event: 'play-item', item: SentenceItem): void
  (event: 'play-group', group: SentenceGroup): void
  (event: 'toggle-text'): void
}>()

const locallyHiddenIds = ref<string[]>([])
const locallyShownIds = ref<string[]>([])
const isTestMode = ref(false)
const quizInputs = ref<Record<string, string[]>>({})
const quizResults = ref<Record<string, boolean[]>>({})

const quizModels = computed<QuizModel[]>(() => props.group.items.map(buildQuizModel))

function hasId(collection: string[], itemId: string): boolean {
  return collection.includes(itemId)
}

function removeId(collection: string[], itemId: string): string[] {
  return collection.filter((currentId) => currentId !== itemId)
}

function isItemVisible(showText: boolean, itemId: string): boolean {
  if (showText) {
    return !hasId(locallyHiddenIds.value, itemId)
  }
  return hasId(locallyShownIds.value, itemId)
}

function toggleItemText(showText: boolean, itemId: string): void {
  if (showText) {
    if (hasId(locallyHiddenIds.value, itemId)) {
      locallyHiddenIds.value = removeId(locallyHiddenIds.value, itemId)
      return
    }
    locallyHiddenIds.value = [...locallyHiddenIds.value, itemId]
    return
  }

  if (hasId(locallyShownIds.value, itemId)) {
    locallyShownIds.value = removeId(locallyShownIds.value, itemId)
    return
  }
  locallyShownIds.value = [...locallyShownIds.value, itemId]
}

function splitBold(text: string): BoldSegment[] {
  const segments: BoldSegment[] = []
  const pattern = /\*\*(.+?)\*\*/g
  let lastIndex = 0
  let match = pattern.exec(text)

  while (match) {
    if (match.index > lastIndex) {
      segments.push({ text: text.slice(lastIndex, match.index), bold: false })
    }
    segments.push({ text: match[1], bold: true })
    lastIndex = match.index + match[0].length
    match = pattern.exec(text)
  }

  if (lastIndex < text.length) {
    segments.push({ text: text.slice(lastIndex), bold: false })
  }

  return segments
}

function buildHint(note: string): string {
  return note
    .replace(/[A-Za-z][A-Za-z'’.-]*/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function buildQuizModel(item: SentenceItem): QuizModel {
  const tokens: QuizToken[] = []
  const targets: string[] = []
  const pattern = /\*\*(.+?)\*\*/g
  let lastIndex = 0
  let match = pattern.exec(item.textEn)

  while (match) {
    if (match.index > lastIndex) {
      tokens.push({ text: item.textEn.slice(lastIndex, match.index), blankIndex: -1 })
    }
    tokens.push({ text: match[1], blankIndex: targets.length })
    targets.push(match[1])
    lastIndex = match.index + match[0].length
    match = pattern.exec(item.textEn)
  }

  if (lastIndex < item.textEn.length) {
    tokens.push({ text: item.textEn.slice(lastIndex), blankIndex: -1 })
  }

  return { item, tokens, targets, hint: buildHint(item.note) }
}

function normalizeAnswer(value: string): string {
  return value.trim().toLowerCase().replace(/[’‘]/g, "'")
}

function getAnswer(itemId: string, blankIndex: number): string {
  return quizInputs.value[itemId]?.[blankIndex] ?? ''
}

function setAnswer(itemId: string, blankIndex: number, value: string): void {
  const current = [...(quizInputs.value[itemId] ?? [])]
  current[blankIndex] = value
  quizInputs.value = { ...quizInputs.value, [itemId]: current }

  if (quizResults.value[itemId]) {
    const nextResults = { ...quizResults.value }
    delete nextResults[itemId]
    quizResults.value = nextResults
  }
}

function onAnswerInput(itemId: string, blankIndex: number, event: Event): void {
  setAnswer(itemId, blankIndex, (event.target as HTMLInputElement).value)
}

function blankState(itemId: string, blankIndex: number): boolean | null {
  const result = quizResults.value[itemId]
  if (!result || blankIndex < 0) {
    return null
  }
  return result[blankIndex] ?? null
}

function hasResult(itemId: string): boolean {
  return quizResults.value[itemId] !== undefined
}

function itemPassed(itemId: string): boolean {
  const result = quizResults.value[itemId]
  return result !== undefined && result.every(Boolean)
}

function checkItem(model: QuizModel): void {
  const result = model.targets.map(
    (target, index) =>
      normalizeAnswer(getAnswer(model.item.id, index)) === normalizeAnswer(target),
  )
  quizResults.value = { ...quizResults.value, [model.item.id]: result }
}

function resetQuiz(): void {
  quizInputs.value = {}
  quizResults.value = {}
}

function toggleTestMode(): void {
  isTestMode.value = !isTestMode.value
  resetQuiz()
}

watch(
  () => props.group.id,
  () => {
    resetQuiz()
  },
)
</script>

<template>
  <section
    class="sentence-block"
    :class="{ 'sentence-block--active': activeItemId.startsWith(`${group.id}-`) }"
  >
    <div class="sentence-block__header">
      <div class="sentence-block__title-wrap">
        <span class="sentence-block__tag">Sentences</span>
        <h3 class="sentence-block__title">{{ group.titleEn }}</h3>
        <p class="sentence-block__subtitle">{{ group.titleZh }}</p>
      </div>

      <div class="sentence-block__actions">
        <button
          class="sentence-block__button"
          type="button"
          @click="emit('play-group', group)"
        >
          Play all · {{ group.items.length }}
        </button>
        <button
          v-if="!isTestMode"
          class="sentence-block__button sentence-block__button--ghost"
          type="button"
          @click="emit('toggle-text')"
        >
          {{ showText ? '隐藏句子' : '显示句子' }}
        </button>
        <button
          class="sentence-block__button sentence-block__button--quiz"
          type="button"
          @click="toggleTestMode"
        >
          {{ isTestMode ? '退出测试' : '单词测试' }}
        </button>
        <button
          v-if="isTestMode"
          class="sentence-block__button sentence-block__button--ghost"
          type="button"
          @click="resetQuiz"
        >
          重置
        </button>
      </div>
    </div>

    <ol class="sentence-block__list">
      <li
        v-for="(model, index) in quizModels"
        :key="model.item.id"
        class="sentence-item"
        :class="{ 'sentence-item--active': activeItemId === model.item.id }"
      >
        <span class="sentence-item__index">{{ index + 1 }}</span>

        <div class="sentence-item__main">
          <template v-if="isTestMode">
            <p class="sentence-item__text sentence-item__text--quiz">
              <template v-for="(token, tokenIndex) in model.tokens" :key="tokenIndex">
                <span v-if="token.blankIndex < 0">{{ token.text }}</span>
                <input
                  v-else
                  class="sentence-item__input"
                  :class="{
                    'sentence-item__input--ok': blankState(model.item.id, token.blankIndex) === true,
                    'sentence-item__input--bad': blankState(model.item.id, token.blankIndex) === false,
                  }"
                  type="text"
                  autocomplete="off"
                  autocapitalize="off"
                  spellcheck="false"
                  :value="getAnswer(model.item.id, token.blankIndex)"
                  @input="onAnswerInput(model.item.id, token.blankIndex, $event)"
                />
              </template>
            </p>

            <p v-if="model.hint" class="sentence-item__hint">提示：{{ model.hint }}</p>

            <p
              v-if="hasResult(model.item.id)"
              class="sentence-item__result"
              :class="
                itemPassed(model.item.id)
                  ? 'sentence-item__result--ok'
                  : 'sentence-item__result--bad'
              "
            >
              <template v-if="itemPassed(model.item.id)">✓ 正确</template>
              <template v-else>✗ 正确答案：{{ model.targets.join(' / ') }}</template>
            </p>
          </template>

          <template v-else>
            <p v-if="isItemVisible(showText, model.item.id)" class="sentence-item__text">
              <template
                v-for="(segment, segmentIndex) in splitBold(model.item.textEn)"
                :key="segmentIndex"
              >
                <strong v-if="segment.bold">{{ segment.text }}</strong>
                <span v-else>{{ segment.text }}</span>
              </template>
            </p>
            <p v-else class="sentence-item__hidden">听力模式 · 点击右侧播放</p>

            <p v-if="isItemVisible(showText, model.item.id)" class="sentence-item__note">
              {{ model.item.note }}
            </p>
          </template>
        </div>

        <div class="sentence-item__actions">
          <button
            v-if="!isTestMode"
            class="sentence-item__toggle"
            type="button"
            @click="toggleItemText(showText, model.item.id)"
          >
            {{ isItemVisible(showText, model.item.id) ? '隐藏' : '显示' }}
          </button>

          <button
            v-if="isTestMode"
            class="sentence-item__check"
            type="button"
            @click="checkItem(model)"
          >
            完成
          </button>

          <button
            class="sentence-item__play"
            type="button"
            @click="emit('play-item', model.item)"
          >
            Play
          </button>
        </div>
      </li>
    </ol>
  </section>
</template>

<style lang="less" scoped>
.sentence-block {
  padding: 22px 24px 10px;
  border: 1px solid #ece8f8;
  border-radius: 22px;
  background: #ffffff;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.04);
}

.sentence-block--active {
  border-color: #8b5cf6;
  box-shadow: 0 16px 34px rgba(124, 58, 237, 0.1);
}

.sentence-block__header {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
}

.sentence-block__title-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sentence-block__tag {
  width: fit-content;
  padding: 5px 12px;
  border-radius: 999px;
  background: #eef2ff;
  color: #4338ca;
  font-size: 12px;
  font-weight: 700;
}

.sentence-block__title {
  margin: 0;
  color: #111827;
  font-size: 20px;
  line-height: 1.3;
}

.sentence-block__subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.sentence-block__actions {
  flex: none;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.sentence-block__button {
  padding: 10px 14px;
  border: none;
  border-radius: 12px;
  background: #eef2ff;
  color: #4338ca;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    background 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    background: #e0e7ff;
  }
}

.sentence-block__button--ghost {
  background: #f5f3ff;
  color: #5b21b6;

  &:hover {
    background: #ddd6fe;
  }
}

.sentence-block__list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.sentence-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid #ece8f8;

  &:last-child {
    border-bottom: none;
  }
}

.sentence-item--active {
  background: #faf7ff;
}

.sentence-item__index {
  width: 28px;
  flex: none;
  padding-top: 2px;
  color: #9ca3af;
  font-size: 13px;
  font-weight: 700;
  text-align: right;
}

.sentence-item__main {
  min-width: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sentence-item__text {
  margin: 0;
  color: #1f2937;
  font-size: 17px;
  line-height: 1.6;
  word-break: break-word;

  strong {
    color: #4c1d95;
    font-weight: 800;
  }
}

.sentence-item__note {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
  line-height: 1.6;
  word-break: break-word;
}

.sentence-item__hidden {
  margin: 0;
  color: #9ca3af;
  font-size: 13px;
  font-weight: 600;
}

.sentence-item__actions {
  flex: none;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sentence-item__toggle,
.sentence-item__play {
  flex: none;
  margin-top: 2px;
  min-width: 64px;
  padding: 8px 12px;
  border: 1px solid #ddd6fe;
  border-radius: 999px;
  background: #ffffff;
  color: #5b21b6;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    background 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    background: #f5f3ff;
  }
}

.sentence-item__toggle {
  border-color: #d1fae5;
  color: #047857;

  &:hover {
    background: #ecfdf5;
  }
}

.sentence-block__button--quiz {
  background: #fdf4ff;
  color: #a21caf;

  &:hover {
    background: #fae8ff;
  }
}

.sentence-item__input {
  width: 128px;
  min-width: 96px;
  margin: 0 2px;
  padding: 3px 10px 4px;
  border: 1px solid #ddd6fe;
  border-bottom: 2px solid #8b5cf6;
  border-radius: 8px;
  background: #f7f5ff;
  color: #4c1d95;
  font-family: inherit;
  font-size: 17px;
  font-weight: 700;
  vertical-align: baseline;
  outline: none;
  transition:
    border-color 0.2s ease,
    background 0.2s ease,
    color 0.2s ease;

  &:focus {
    border-color: #7c3aed;
    background: #ede9fe;
  }
}

.sentence-item__input--ok {
  border-color: #86efac;
  border-bottom-color: #16a34a;
  background: #ecfdf5;
  color: #15803d;
}

.sentence-item__input--bad {
  border-color: #fecaca;
  border-bottom-color: #dc2626;
  background: #fef2f2;
  color: #b91c1c;
}

.sentence-item__hint {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
  line-height: 1.6;
}

.sentence-item__result {
  margin: 0;
  font-size: 13px;
  font-weight: 700;
}

.sentence-item__result--ok {
  color: #15803d;
}

.sentence-item__result--bad {
  color: #b91c1c;
}

.sentence-item__check {
  flex: none;
  margin-top: 2px;
  min-width: 64px;
  padding: 8px 12px;
  border: 1px solid #bbf7d0;
  border-radius: 999px;
  background: #ffffff;
  color: #047857;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    background 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    background: #ecfdf5;
  }
}

@media (max-width: 768px) {
  .sentence-block {
    padding: 18px 18px 8px;
    border-radius: 20px;
  }

  .sentence-block__header {
    flex-direction: column;
  }

  .sentence-item {
    gap: 10px;
  }

  .sentence-item__index {
    width: 22px;
  }

  .sentence-item__text {
    font-size: 16px;
  }

  .sentence-item__input {
    width: 104px;
    min-width: 80px;
    font-size: 16px;
  }

  .sentence-item__play {
    min-width: 56px;
    padding-inline: 10px;
  }

  .sentence-item__actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
