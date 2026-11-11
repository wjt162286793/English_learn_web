<script setup lang="ts">
import { computed, ref } from 'vue'
import type { LessonLine } from '../types/course'

interface Props {
  line: LessonLine
  index: number
  showEnglish: boolean
  showChinese: boolean
  active: boolean
  variant: 'speaker-a' | 'speaker-b' | 'speaker-c' | 'narrator'
  marker: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (event: 'play', line: LessonLine): void
}>()

const locallyHidden = ref(false)
const locallyShown = ref(false)

const hasGlobalText = computed<boolean>(() => props.showEnglish || props.showChinese)
const isTextVisible = computed<boolean>(() => {
  if (hasGlobalText.value) {
    return !locallyHidden.value
  }
  return locallyShown.value
})
const showEnglishEffective = computed<boolean>(() => {
  if (!isTextVisible.value) {
    return false
  }
  return props.showEnglish || !hasGlobalText.value
})
const showChineseEffective = computed<boolean>(() => {
  if (!isTextVisible.value) {
    return false
  }
  return props.showChinese || !hasGlobalText.value
})
const toggleLabel = computed<string>(() => (isTextVisible.value ? '隐藏' : '显示'))

function toggleText(): void {
  if (hasGlobalText.value) {
    locallyHidden.value = !locallyHidden.value
    if (!locallyHidden.value) {
      locallyShown.value = false
    }
    return
  }
  locallyShown.value = !locallyShown.value
}
</script>

<template>
  <div
    class="sentence-row"
    :class="[`sentence-row--${variant}`, { 'sentence-row--active': active }]"
  >
    <span class="sentence-row__side">
      <span class="sentence-row__marker">{{ marker }}</span>
      <span class="sentence-row__index">{{ index + 1 }}</span>
    </span>

    <span class="sentence-row__main">
      <span class="sentence-row__top">
        <span v-if="line.speaker" class="sentence-row__speaker">{{ line.speaker }}</span>
        <span v-else class="sentence-row__speaker sentence-row__speaker--article">Reading</span>
      </span>

      <span class="sentence-row__content">
        <span v-if="showEnglishEffective" class="sentence-row__text sentence-row__text--en">
          {{ line.textEn }}
        </span>
        <span v-if="showChineseEffective" class="sentence-row__text sentence-row__text--zh">
          {{ line.textZh }}
        </span>
        <span v-if="!showEnglishEffective && !showChineseEffective" class="sentence-row__hint">
          Click to listen
        </span>
      </span>
    </span>

    <span class="sentence-row__actions">
      <button class="sentence-row__toggle" type="button" @click="toggleText">
        {{ toggleLabel }}
      </button>
      <button class="sentence-row__play" type="button" @click="emit('play', line)">
        Play
      </button>
    </span>
  </div>
</template>

<style lang="less" scoped>
.sentence-row {
  width: 100%;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px 0;
  border-bottom: 1px solid #ece8f8;
  background: transparent;
  text-align: left;
  transition:
    background 0.2s ease,
    transform 0.2s ease;

  &:hover {
    transform: translateX(2px);
  }
}

.sentence-row--active {
  background: #faf7ff;
}

.sentence-row--speaker-a {
  --row-accent: #f59e0b;
  --row-soft: #fff7e8;
  --row-text: #9a6700;
}

.sentence-row--speaker-b {
  --row-accent: #3b82f6;
  --row-soft: #eff6ff;
  --row-text: #1d4ed8;
}

.sentence-row--speaker-c,
.sentence-row--narrator {
  --row-accent: #22c55e;
  --row-soft: #edfdf3;
  --row-text: #15803d;
}

.sentence-row__side {
  width: 44px;
  flex: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding-top: 2px;
}

.sentence-row__marker {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--row-accent);
  border-radius: 50%;
  background: #ffffff;
  color: var(--row-accent);
  font-size: 14px;
  font-weight: 700;
}

.sentence-row__index {
  color: #9ca3af;
  font-size: 12px;
  font-weight: 700;
}

.sentence-row__speaker {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--row-soft);
  color: var(--row-text);
  font-size: 12px;
  font-weight: 700;
}

.sentence-row__speaker--article {
  background: #f3f4f6;
  color: #4b5563;
}

.sentence-row__main {
  min-width: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sentence-row__top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sentence-row__content {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sentence-row__text {
  display: block;
  line-height: 1.6;
  word-break: break-word;
}

.sentence-row__text--en {
  color: #1f2937;
  font-size: 17px;
  font-weight: 500;
}

.sentence-row__text--zh {
  color: #6b7280;
  font-size: 14px;
}

.sentence-row__hint {
  color: #6b7280;
  font-size: 13px;
  font-weight: 600;
}

.sentence-row__actions {
  flex: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.sentence-row__toggle,
.sentence-row__play {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 64px;
  margin-top: 2px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    background 0.2s ease,
    color 0.2s ease;
}

.sentence-row__toggle {
  border: 1px solid #d8f1df;
  background: #edfdf3;
  color: #15803d;

  &:hover {
    transform: translateY(-1px);
    background: #dcfce7;
  }
}

.sentence-row__play {
  border: 1px solid transparent;
  background: var(--row-soft);
  color: var(--row-text);

  &:hover {
    transform: translateY(-1px);
  }
}

@media (max-width: 768px) {
  .sentence-row {
    display: grid;
    grid-template-columns: 40px minmax(0, 1fr);
    gap: 10px 12px;
    padding: 14px 0;
  }

  .sentence-row__side {
    width: 40px;
  }

  .sentence-row__main {
    gap: 10px;
  }

  .sentence-row__top {
    flex-wrap: wrap;
  }

  .sentence-row__actions {
    grid-column: 2;
    justify-self: start;
    flex-wrap: wrap;
  }

  .sentence-row__toggle,
  .sentence-row__play {
    min-width: 56px;
    min-height: 36px;
    margin-top: 0;
    padding-inline: 12px;
  }

  .sentence-row__text--en {
    font-size: 16px;
    line-height: 1.65;
  }

  .sentence-row__text--zh {
    font-size: 13px;
    line-height: 1.7;
  }
}

@media (max-width: 480px) {
  .sentence-row {
    gap: 8px 10px;
  }

  .sentence-row__marker {
    width: 26px;
    height: 26px;
    font-size: 13px;
  }

  .sentence-row__index {
    font-size: 11px;
  }

  .sentence-row__text--en {
    font-size: 15px;
  }
}
</style>
