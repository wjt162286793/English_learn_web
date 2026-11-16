<script setup lang="ts">
import type { BreadcrumbItem } from '../types/navigation'

interface Props {
  items: BreadcrumbItem[]
}

defineProps<Props>()

const emit = defineEmits<{
  (event: 'navigate', id: string): void
}>()
</script>

<template>
  <nav v-if="items.length" class="breadcrumbs" aria-label="当前位置">
    <ol class="breadcrumbs__list">
      <li
        v-for="item in items"
        :key="item.id"
        class="breadcrumbs__item"
        :class="{ 'breadcrumbs__item--current': item.current }"
      >
        <span v-if="item.current" aria-current="page">{{ item.label }}</span>
        <button v-else type="button" @click="emit('navigate', item.id)">
          {{ item.label }}
        </button>
      </li>
    </ol>
  </nav>
</template>

<style lang="less" scoped>
.breadcrumbs {
  min-width: 0;
  flex: 1;
}

.breadcrumbs__list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px 0;
  margin: 0;
  padding: 0;
  list-style: none;
}

.breadcrumbs__item {
  display: inline-flex;
  align-items: center;
  min-width: 0;

  & + &::before {
    content: "/";
    padding: 0 10px;
    color: #b4acbf;
    font-size: 12px;
  }

  button,
  span {
    max-width: min(280px, 35vw);
    overflow: hidden;
    color: #766c83;
    font: inherit;
    font-size: 12px;
    line-height: 1.5;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  button {
    padding: 5px 0;
    border: 0;
    background: transparent;
    cursor: pointer;

    &:hover {
      color: #6244bd;
      text-decoration: underline;
      text-underline-offset: 3px;
    }

    &:focus-visible {
      border-radius: 4px;
      outline: 2px solid rgba(124, 58, 237, 0.35);
      outline-offset: 3px;
    }
  }

  span {
    color: #30273e;
    font-weight: 750;
  }
}

.breadcrumbs__item--current span {
  color: #30273e;
}
</style>
