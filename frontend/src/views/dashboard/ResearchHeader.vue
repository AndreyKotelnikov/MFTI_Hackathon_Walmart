<template>
  <v-row no-gutters>
    <v-col cols="12">
      <div class="d-flex align-center justify-space-between flex-wrap">
        <VBtn icon="ri-arrow-left-s-line"
          @click="$router.back()"
          class="mr-4"
        />

        <div style="flex: 1;">
          <h1 class="text-h4 font-weight-bold mb-2">
            Исследование #{{ research.id }}
          </h1>

          <div class="d-flex align-center flex-wrap">
            <v-icon icon="ri-calendar-fill" size="small" class="mr-1" />
            <span class="text-body-1 mr-2">Период:</span>
            <span class="font-weight-medium">
              {{ research.period_start }} — {{ research.period_end }}
            </span>
          </div>

        </div>

        <v-chip-group>
          <v-chip
            :color="modeColor"
            variant="outlined"
            prepend-icon="ri-calendar-line"
          >
            {{ modeText }}
          </v-chip>
          <v-chip
            :color="tempColor"
            variant="outlined"
            prepend-icon="ri-temp-hot-line"
          >
            {{ research.avg_temp }}°C
          </v-chip>
          <v-chip
            v-if="research.precip_amount > 0"
            color="blue"
            variant="outlined"
            prepend-icon="ri-hail-line"
          >
            {{ research.precip_amount }} мм
          </v-chip>
            
          <v-chip
            v-if="research.is_rain"
            color="blue-lighten-1"
            prepend-icon="ri-heavy-showers-line"
          >
            Дождь
          </v-chip>
          
          <v-chip
            v-if="research.is_snow"
            color="blue-lighten-4"
            prepend-icon="ri-snowflake-line"
          >
            Снег
          </v-chip>

          <v-chip
            v-if="research.store_code"
            color="blue-lighten-4"
            prepend-icon="ri-snowflake-line"
          >
            Магазин: {{ research.store_code }}
          </v-chip>

          <v-chip
            v-if="research.store_item_code"
            color="blue-lighten-4"
            prepend-icon="ri-snowflake-line"
          >
            Товар: {{ research.store_item_code }}
          </v-chip>

        </v-chip-group>
      </div>

      <v-divider class="my-4" />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Research {
  id: number
  mode: string
  period_start: string
  period_end: string
  avg_temp: number
  precip_amount: number
  created_at: string
  store_code: string | null
  store_item_code: string | null
  is_rain: boolean
  is_snow: boolean
}

const props = defineProps<{
  research: Research
}>()

const modeText = computed(() => {
  switch (props.research.mode) {
    case 'day': return 'День'
    case 'week': return 'Неделя'
    case 'month': return 'Месяц'
    default: return props.research.mode
  }
})

const modeColor = computed(() => {
  switch (props.research.mode) {
    case 'day': return 'green'
    case 'week': return 'orange'
    case 'month': return 'purple'
    default: return 'primary'
  }
})

const tempColor = computed(() => {
  if (props.research.avg_temp > 25) return 'red'
  if (props.research.avg_temp > 15) return 'orange'
  if (props.research.avg_temp > 0) return 'green'
  return 'blue'
})
</script>

<style scoped>
.page-header {
  max-width: 100%;
}
</style>
