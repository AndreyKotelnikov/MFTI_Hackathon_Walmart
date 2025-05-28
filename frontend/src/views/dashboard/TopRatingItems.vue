<template>
  <v-card>
    <v-card-title class="mb-4">Анализ соотношений продаж</v-card-title>
    
    <v-card-text class="d-flex gap-4 flex-wrap w-full">
      <!-- Топ-5 лучших -->
      <div class="mb-6" style="max-width: 600px; min-width: 300px; flex: 1;">
        <div class="text-subtitle-1 text-white mb-2">Топ-5 лучших показателей</div>

        <div v-for="(item, index) in topItems" :key="index" class="mb-3 text-caption">
          <div class="d-flex justify-space-between mb-1">
            <span>
              Товар: {{ item.store_item_code }}
            </span>
            <span>{{ (item.ratio * 100).toFixed(2) }}%</span>
          </div>

          <v-progress-linear
            :key="'top-' + item.store_item_code"
            :model-value="normalizedValue(item.ratio)"
            height="10"
            rounded
            :color="getColor(item.ratio)"
          ></v-progress-linear>
        </div>
      </div>

      <div class="mb-6" style="max-width: 600px; min-width: 300px; flex: 1;">
        <div class="text-subtitle-1 text-white mb-2">Топ-5 худших показателей</div>

        <div v-for="(item, index) in bottomItems" :key="index" class="mb-3 text-caption">
          <div class="d-flex justify-space-between mb-1">
            <span>
              Товар: {{ item.store_item_code }}
            </span>
            <span>{{ (item.ratio * 100).toFixed(2) }}%</span>
          </div>

          <v-progress-linear
            :key="'top-' + item.store_item_code"
            :model-value="normalizedValue(item.ratio)"
            height="10"
            rounded
            :color="getColor(item.ratio)"
          ></v-progress-linear>
        </div>
      </div>
    </v-card-text>

    <v-card-text>

      <!-- Легенда -->
      <div class="mt-4 text-caption text-medium-emphasis">
        <div class="d-flex align-center mb-1">
          <v-icon icon="mdi-circle" color="green-darken-3" size="small" class="mr-1" />
          <span>Соотношение ≥ 1.0 (превышение спроса)</span>
        </div>
        <div class="d-flex align-center mb-1">
          <v-icon icon="mdi-circle" color="orange-darken-2" size="small" class="mr-1" />
          <span>Соотношение 0.9-1.0 (близко к норме)</span>
        </div>
        <div class="d-flex align-center">
          <v-icon icon="mdi-circle" color="red-darken-2" size="small" class="mr-1" />
          <span>Соотношение меньше 0.9 (падение спроса)</span>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface RatioItem {
  store_item_code: string
  ratio: number
}

const props = defineProps<{
  items: RatioItem[]
}>()

// Сортируем элементы по ratio
const sortedItems = computed(() => {
  return [...props.items].sort((a, b) => b.ratio - a.ratio)
})

// Топ-5 лучших
const topItems = computed(() => {
  return sortedItems.value.slice(0, 5)
})

// Топ-5 худших
const bottomItems = computed(() => {
  return sortedItems.value.slice(-5).reverse()
})

// Нормализуем значение для прогресс-бара (0-100)
const normalizedValue = (ratio: number) => {
  // Для значений > 1.0 (превышение спроса) показываем полный прогресс-бар
  if (ratio >= 1.0) return 100
  // Для остальных - масштабируем от 0 до 100
  return ratio * 100
}

// Определяем цвет в зависимости от значения ratio
const getColor = (ratio: number) => {
  if (ratio >= 1.0) return 'success' // Превышение спроса
  if (ratio >= 0.9) return 'primary' // Близко к норме
  return 'primary-light' // Падение спроса
}
</script>

<style scoped>
.v-progress-linear {
  transition: all 0.3s ease;
}
</style>
