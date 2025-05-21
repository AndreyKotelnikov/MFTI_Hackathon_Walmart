<template>
  <v-card class="w-full max-w-md shadow" elevation="3">
    <v-card-text>
      <v-row>
        <v-col cols="12" class="text-lg font-semibold">
          Предсказание: {{ item.units_pred.toFixed(1) }} шт.
        </v-col>
        <v-col cols="12" class="text-sm">
          Факт: {{ item.units }} шт.
          <br />
          Δ: {{ diff }} (×{{ coef.toFixed(2) }})
        </v-col>
      </v-row>

      <v-divider class="my-2" />

      <v-row dense>
        <v-col cols="6" class="text-caption">
          Tavg: {{ item.tavg }}°C<br />
          Tmax: {{ item.tmax }}°C<br />
          Tmin: {{ item.tmin }}°C
        </v-col>
        <v-col cols="6" class="text-caption">
          Осадки (RA): {{ item.RA }}<br />
          Давление: {{ item.stnpressure }}<br />
          Ветер: {{ item.avgspeed }} м/с
        </v-col>
        <v-col cols="6" class="text-caption">
          Вчера: {{ item.units_yesterday }}<br />
          Неделю назад: {{ item.units_prev_week }}
        </v-col>
        <v-col cols="6" class="text-caption">
          Магазин: {{ item.store_code }}<br />
          Выходной: {{ item.is_weekend ? 'Да' : 'Нет' }}
        </v-col>
      </v-row>

      <v-divider class="my-2" />

      <div class="h5 text-muted mb-1">SHAP-анализ</div>
        <div v-for="(factor, index) in preditionFactors" :key="index" class="mb-3 text-caption">
          <div class="d-flex justify-space-between mb-1">
            <span>
              {{ factor.name }}
              <span v-if="factor.property_value">({{ factor.property_value }})</span>
            </span>
            <span>{{ (factor.value * 100).toFixed(1) }}%</span>
          </div>

          <v-progress-linear
            :model-value="factor.value * 100"
            height="10"
            rounded
            color="primary"
          ></v-progress-linear>
        </div>
    </v-card-text>
  </v-card>
</template>

<script lang="ts" setup>
import { computed } from 'vue';

interface PredictionItem {
  id: number
  prediction_date: string
  store_code: string
  store_item_code: string
  tavg: number
  RA: number
  units: number
  units_pred: number
  units_yesterday: number
  units_prev_week: number
  tmax: number
  tmin: number
  stnpressure: number
  avgspeed: number
  is_weekend: number
}

const props = defineProps<{ item: PredictionItem }>()

const diff = computed(() => props.item.units_pred - props.item.units)
const coef = computed(() => {
  return props.item.units > 0 ? props.item.units_pred / props.item.units : 0
})

const preditionFactors = ref([
{
    name: 'Продажи за вчерашный день',
    property_value: '23',
    value: 0.95,
  },
  {
    name: 'Уровень осадков',
    property_value: '3',
    value: 0.35,
  },
  {
    name: 'Температура средняя',
    property_value: '23',
    value: 0.25,
  },
  {
    name: 'Температура на завтра',
    property_value: '23',
    value: 0.15,
  },
  {
    name: 'Был дождь',
    property_value: '12',
    value: 0.11,
  },
])
</script>
