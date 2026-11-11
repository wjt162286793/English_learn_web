<script setup lang="ts">
import { computed } from 'vue'
import SentenceRow from './SentenceRow.vue'
import type { LessonLine, LessonSection } from '../types/course'

interface Props {
  section: LessonSection
  showEnglish: boolean
  showChinese: boolean
  activeLineId: string
  activeBlockId: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (event: 'play-line', line: LessonLine): void
  (event: 'play-section', section: LessonSection): void
}>()

const speakers = computed<string[]>(() => {
  const list: string[] = []
  for (const line of props.section.lines) {
    if (!line.speaker || list.includes(line.speaker)) {
      continue
    }
    list.push(line.speaker)
  }
  return list
})

function getSpeakerIndex(line: LessonLine): number {
  if (!line.speaker || props.section.type !== 'dialogue') {
    return -1
  }
  return speakers.value.indexOf(line.speaker)
}

function getLineVariant(
  line: LessonLine,
): 'speaker-a' | 'speaker-b' | 'speaker-c' | 'narrator' {
  const index = getSpeakerIndex(line)
  if (index === 0) {
    return 'speaker-a'
  }
  if (index === 1) {
    return 'speaker-b'
  }
  if (index >= 2) {
    return 'speaker-c'
  }
  return 'narrator'
}

function getLineMarker(line: LessonLine): string {
  const index = getSpeakerIndex(line)
  if (index === 0) {
    return 'A'
  }
  if (index === 1) {
    return 'B'
  }
  if (index >= 2) {
    return String.fromCharCode(65 + index)
  }
  return 'R'
}
</script>

<template>
  <section
    class="content-section"
    :class="{ 'content-section--active': activeBlockId === section.id }"
  >
    <div class="content-section__header">
      <div class="content-section__title-wrap">
        <span class="content-section__tag">
          {{ section.type === 'dialogue' ? 'Dialogue' : 'Article' }}
        </span>
        <h3 class="content-section__title">{{ section.titleEn }}</h3>
        <p class="content-section__subtitle">{{ section.titleZh }}</p>
      </div>
      <button
        class="content-section__button"
        type="button"
        @click="emit('play-section', section)"
      >
        {{ section.type === 'dialogue' ? 'Play dialogue' : 'Play article' }}
      </button>
    </div>

    <div class="content-section__body">
      <SentenceRow
        v-for="(line, index) in section.lines"
        :key="line.id"
        :line="line"
        :index="index"
        :show-english="showEnglish"
        :show-chinese="showChinese"
        :active="activeLineId === line.id"
        :variant="getLineVariant(line)"
        :marker="getLineMarker(line)"
        @play="emit('play-line', $event)"
      />
    </div>
  </section>
</template>

<style lang="less" scoped>
.content-section {
  padding: 22px 24px 8px;
  border: 1px solid #ece8f8;
  border-radius: 22px;
  background: #ffffff;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.04);
}

.content-section--active {
  border-color: #8b5cf6;
  box-shadow: 0 16px 34px rgba(124, 58, 237, 0.1);
}

.content-section__header {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
}

.content-section__title-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.content-section__tag {
  width: fit-content;
  padding: 5px 12px;
  border-radius: 999px;
  background: #f5f3ff;
  color: #7c3aed;
  font-size: 12px;
  font-weight: 700;
}

.content-section__title {
  margin: 0;
  color: #111827;
  font-size: 20px;
  line-height: 1.3;
}

.content-section__subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.content-section__button {
  flex: none;
  padding: 10px 14px;
  border: none;
  border-radius: 12px;
  background: #f5f3ff;
  color: #5b21b6;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    background 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    background: #ddd6fe;
  }
}

.content-section__body {
  display: flex;
  flex-direction: column;
  gap: 0;
}

@media (max-width: 768px) {
  .content-section {
    padding: 18px 18px 6px;
    border-radius: 20px;
  }

  .content-section__header {
    flex-direction: column;
  }

  .content-section__button {
    width: 100%;
    min-height: 44px;
    justify-content: center;
  }

  .content-section__title {
    font-size: 18px;
  }
}
</style>
