<template>
  <div class="text-center my-8">
    <h2 class="h2">Коэффициенты соотношений продаж</h2>
  </div>
  <v-card>
    
    <v-card-text class="d-flex gap-4 flex-wrap w-full" style="justify-content: space-around;">
      <!-- Топ-5 лучших -->
      <div v-if="topItems.length" class="mb-6" style="max-width: 600px; min-width: 300px; flex: 1;">
        <div class="text-subtitle-1 text-white mb-2">Топ-5 роста продаж</div>

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
            color="success"
          ></v-progress-linear>
        </div>
      </div>

      <div v-if="bottomItems.length" class="mb-6" style="max-width: 600px; min-width: 300px; flex: 1;">
        <div class="text-subtitle-1 text-white mb-2">Топ-5 падения продаж</div>

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
            color="primary"
          ></v-progress-linear>
        </div>
      </div>
    </v-card-text>


    <v-card-text class="mb-4 text-warning" v-if="!topItems.length && !bottomItems.length">
      Вероятно все предсказания были отсеяны из-за низкой достоверности. Попробуйте более общирное исследование.
    </v-card-text>

    <v-card-text v-else>

      <h4 class="h4">Коэффициенты:</h4>
      <p class="my-1">
        Для каждого товара рассчитывается сумма прогнозных продаж при заданной погоде, которая затем сравнивается с соответствующей суммой при фактической погоде. Полученное отношение показывает изменение спроса.
      </p>
      <p class="">
        Подробную информацию о каждом прогнозе вы найдёте в таблице «Детальный разбор прогнозов продаж».
      </p>
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

const maxValue = computed(() => {
  if (!sortedItems.value) {
    return 100
  }
  return sortedItems.value[0].ratio
})


// Нормализуем значение для прогресс-бара (0-100)
const normalizedValue = (ratio: number) => {
  if (maxValue.value > 100) {
    return ratio / maxValue.value * 100
  }
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
