<template>
  <v-card class="w-full max-w-md shadow" elevation="3">
    <v-card-text>
      <v-row>
        <v-col cols="12">
          <h4 class="text-lg font-semibold mb-1">
            {{ title }}
          </h4>
          Предсказание: {{ item.units_pred.toFixed(4) }} ед.
        </v-col>
      </v-row>

      <v-divider class="my-2" />

      <v-row dense>
        <v-col cols="6" class="text-caption">
          Tavg: {{ fahrenheitToCelsius(item.tavg).toFixed(1) }}°C<br />
          Tmax: {{ fahrenheitToCelsius(item.tmax).toFixed(1) }}°C<br />
          Tmin: {{ fahrenheitToCelsius(item.tmin).toFixed(1) }}°C
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
            <span :class="differentFactorStyle(factor)">
              {{ factor.name }}
              <span>({{ factor.value }})</span>
            </span>
            <span>{{ (factor.score * 100).toFixed(2) }}%</span>
          </div>

          <v-progress-linear
            :model-value="factor.score * 100"
            height="10"
            rounded
            :color="factor.is_different ? differentColor : 'primary'"
          ></v-progress-linear>
        </div>
    </v-card-text>
  </v-card>
</template>

<script lang="ts" setup>

interface PredictionItem {
  id: number
  prediction_date: string
  store_code: string
  store_item_code: string
  tavg: number
  RA: number
  // units: number
  units_pred: number
  units_yesterday: number
  units_prev_week: number
  tmax: number
  tmin: number
  stnpressure: number
  avgspeed: number
  is_weekend: number
  shap: any
}

const $props = withDefaults(defineProps<{
  item: PredictionItem,
  title: string,
  differentFields: string[],
  fieldLabels: any,
  differentColor?: string,
}>(),
  {
    differentColor: 'success'
  }
)

const preditionFactors = computed(() => {
  const result = [] as any[]
  const shap = $props.item.shap as any
  const keys = Object.keys(shap)
  const scores = Object.values(shap) as number[]
  const maxValue = Math.max(...scores)

  keys.forEach(key => {
    
    const value = (key as keyof PredictionItem) in $props.item 
    ? $props.item[key as keyof PredictionItem] 
    : '-';

    result.push({
      name: key in $props.fieldLabels ? $props.fieldLabels[key] : key,
      key: key,
      value: value,
      score: maxValue > 1 ? shap[key] / maxValue : shap[key],
      is_different: $props.differentFields.includes(key)
    })
  })

  return result.sort((a, b) => a.score > b.score ? -1 : 1)
})

const differentFactorStyle = computed(() => (factor: any) => {
  return factor.is_different ? 'text-' + $props.differentColor + ' font-weight-bold' : ''
})

const fahrenheitToCelsius = computed(() => (f: number) => {
  return (f - 32) * 5 / 9;
})
</script>
