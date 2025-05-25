<script lang="ts" setup>
import { useApi } from '@/composables/useApi';
import PredictionCard from '@/views/prediction/PredictionCard.vue';
import avatar1 from '@images/avatars/avatar-1.png';
import { useRoute } from 'vue-router';

const route = useRoute()

const $api = useApi()
const $route = useRoute()
const $router = useRouter()
const isLoading = ref(true)
const predictionId = ref<number|null>($route.params.id ? Number($route.params.id) : null)
const predictionData = ref<any|null>(null)

const loadData = () => {
  isLoading.value = true

  $api.get(`/api/predictions/${predictionId.value}/`)
    .then(response => {
      response.data.photo = avatar1
      predictionData.value = response.data
      isLoading.value = false
    })
}

const getDifferentFields = computed(() => {

  if (!predictionData.value) {
    return []
  }

  const realProps = predictionData.value.real_detail
  const withoutProps = predictionData.value.without_detail
  const excludedKeys = [
  'units_pred', 'store_code', 'store_item_code', 'shap'
  ]

  // Собираем все уникальные ключи из обоих объектов
  const allKeys = new Set([...Object.keys(realProps), ...Object.keys(withoutProps)])
  const allKeysList = Array.from(allKeys).filter(k => !excludedKeys.includes(k))
  
  const differentFields = [] as string[]
  
  allKeysList.forEach(key => {
    // Сравниваем значения, учитывая что поля могут отсутствовать в одном из объектов
    if (!Object.is(realProps[key], withoutProps[key])) {
      differentFields.push(key);
    }
  })
  
  return differentFields;
})

const fieldLabels = ref({
  tavg: "Средняя температура",
  RA: "Дождь",
  store_code: "Код магазина",
  store_item_code: "Код товара",

  units_yesterday: "Продаж вчера",
  units_prev_week: "Продаж за прошлую неделю",

  tmax: "Максимальная температура",
  tmin: "Минимальная температура",
  depart: "Отклонение температуры от нормы",
  dewpoint: "Средняя температура точки росы за сутки",
  wetbulb: "Средняя температура по мокрому термометру",
  heat: "Индекс жары",
  cool: "Индекс прохлады",

  sunrise: "Восход",
  sunset: "Закат",

  snowfall: "Снег (дюймы)",
  preciptotal: "Осадки (дюймы)",
  stnpressure: "Давление на уровне станции",
  sealevel: "Давление на уровне моря",

  resultspeed: "Скорость ветра",
  resultdir: "Направление ветра",
  avgspeed: "Средняя скорость ветра",

  year: "Год",
  week: "Неделя",

  BCFG: "Локальный туман",
  BLDU: "Пыль, сдуваемая ветром",
  BLSN: "Метель",
  BR: "Дымка",
  DU: "Пыль",
  DZ: "Морось",
  FG: "Туман",
  FU: "Дым",
  FZDZ: "Переохлажд. морось",
  FZFG: "Переохлажд. туман",
  FZRA: "Ледяной дождь",
  GR: "Град",
  GS: "Мелкий град/градинки",
  HZ: "Мгла",
  MIFG: "Мелкий туман",
  PL: "Ледяные гранулы",
  PRFG: "Частичный туман",
  SG: "Снежные зерна",
  SN: "Снег",
  SQ: "Шквал",
  TS: "Гроза",
  TSRA: "Гроза с дождём",
  TSSN: "Гроза со снегом",
  UP: "Неизвестные осадки",
  VCFG: "Туман поблизости",
  VCTS: "Гроза поблизости",

  day_of_week: "День недели",
  month: "Месяц",
  is_weekend: "Выходной",
  is_holiday: "Праздник",

  rain_streak: "Дней подряд идёт дождь",
  dry_streak: "Дней подряд без дождя",

  avg_temp_next_day: "Температура на завтра",
  rain_next_day: "Завтра будет дождь",
  days_to_holiday: "Дней до праздника"
})

const fieldLabelTitle = computed(() => (key: string) => {
  const labels = fieldLabels.value;
  return key in labels ? labels[key as keyof typeof labels] : key;
})

onMounted(() => {
  loadData()
})

</script>

<template>
  <VContainer v-if="predictionData" class="mb-8">
    <div class="d-flex">
      <VBtn icon="ri-arrow-left-s-line"
        to="/"
        class="mr-4"
      />
      <div>
        <h2 class="h2">
          Товар: {{ predictionData.store_item_code }}
          дата: {{ predictionData.prediction_date }}
        </h2>
        <h3 class="h3 mb-8 text-disabled">
          Сравнение предсказаний по реальной погоде и по "очищенной"
        </h3>
      </div>
    </div>

    <v-list dense class="mb-4">
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="font-weight-bold">Реальное количество покупок:</v-list-item-title>
          <v-list-item-subtitle v-if="predictionData.pred_without < 2.5802225041841567"
            class="text-h6 text-error"
          >
            {{ predictionData.units }} ед. (шум)
          </v-list-item-subtitle>
          <v-list-item-subtitle v-else class="text-h6 text-success">{{ predictionData.units }} ед.</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>

      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="font-weight-bold">Рост / Падение Δ:</v-list-item-title>
          <v-list-item-subtitle class="text-h6"
            :class="predictionData.difference < 0 ? 'text-error' : 'text-success'"
          >
          {{ predictionData.difference ? predictionData.difference : '-' }} ед.
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>

      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="font-weight-bold">Коэффициент:</v-list-item-title>
          <v-list-item-subtitle class="text-h6">
            {{ predictionData.coefficient ? predictionData.coefficient : '-' }}
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="font-weight-bold">В каких параметрах разница:</v-list-item-title>
          <div class="mt-2">
            <v-chip
              small
              v-for="param in getDifferentFields"
              :key="param"
              class="mr-2 mb-2"
              color="primary"
              outlined
            >
              {{ fieldLabelTitle(param) }}
            </v-chip>
          </div>
        </v-list-item-content>
      </v-list-item>
    </v-list>

    <VRow>
      <VCol cols="12" md="6" sm="12">
        <PredictionCard
          :item="predictionData.real_detail"
          title="Реальная погода"
          :different-fields="getDifferentFields"
          :field-labels="fieldLabels"
        />
      </VCol>
      <VCol cols="12" md="6" sm="12">
        <PredictionCard
          :item="predictionData.without_detail"
          title="Очищенная погода"
          :different-fields="getDifferentFields"
          :field-labels="fieldLabels"
          different-color="warning"
        />
      </VCol>
    </VRow>
  </VContainer>
  <div v-else class="text-center pt-16" style="min-height: calc(100vh - 96px);">
    <VProgressCircular class="mt-16"
      :indeterminate="true"
    />
  </div>
</template>
