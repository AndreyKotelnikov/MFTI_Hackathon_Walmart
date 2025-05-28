<script setup lang="ts">
import { useApi } from '@/composables/useApi';
import StopeItemForm from '@/views/search//StopeItemForm.vue';
import PeriodForm from '@/views/search/PeriodForm.vue';

import notRain from '@images/front-pages/not-rain.png';
import '@vuepic/vue-datepicker/dist/main.css';
import { ref } from 'vue';

const $api = useApi()
const $router = useRouter()
const isProcessing = ref(false)
const searchForm = ref({
  mode: 'week',
  period_start: "2014-10-19",
  period_end: "2014-10-26",
  store_code: null,
  store_item_code: null,
  is_rain: false,
  is_snow: false,
  avg_temp: 20,
  precip_amount: 0
})

const tickLabelsTemp = computed(() => {
  const result = {} as any
  for(let i=-50; i<=50; i+=10) {
    result[i] = i + '°C'
  }
  return result
})
const tickLabelsPrecip = computed(() => {
  const result = {} as any
  for(let i=0; i<=5; i+=1) {
    result[i] = i + 'мм'
  }
  return result
})

const createResearch = () => {
  isProcessing.value = true
  $api.post(`/api/researches/`, searchForm.value)
    .then((response: any) => {
      console.log('response.data', response.data)
      isProcessing.value = false
      $router.push({
        path: '/dashboard/' + response.data.id
      })
    })
    .catch(() => {
      isProcessing.value = false
      alert('Ошибка')
    })

}

</script>

<template>
  <VContainer style="min-height: calc(100vh - 96px);">

    <h1 class="h1 text-center my-12">
      Влияние погоды на продажи
    </h1>

    <VRow class="mt-12">
      <VCol cols="12" sm="12" md="6">
        <div class="d-flex flex-column gap-2">
          <h4 class="h4 mb-2">Переод прогнозирования:</h4>
          <PeriodForm
            v-model:mode="searchForm.mode"
            v-model:period-start="searchForm.period_start"
            v-model:period-end="searchForm.period_end"
            :disabled="isProcessing"
          />

          <h4 class="h4 mt-4">Доп. фильтры:</h4>
          <span class="text-disabled text-sm">
            * Предсказание по всем магазинам может занять несколько минут
          </span>
          <StopeItemForm
            v-model:store-id="searchForm.store_code"
            v-model:item-id="searchForm.store_item_code"
            :disabled="isProcessing"
          />

          <!-- {{ searchForm }}! -->
          
          <div class="mt-8 d-flex" style="align-items: center;">

            <VBtn prepend-icon="ri-sparkling-line"
              class="mr-2"
              color="success"
              inline
              :disabled="isProcessing"
              :loading="isProcessing"
              @click="createResearch"
            >Предсказать!</VBtn>

            <label> 🤔 Как изменяться продажи при такой погоде?</label>
          </div>
          
          <div class="mt-4 d-flex" style="align-items: center;">
            <VBtn variant="tonal"
              to="/researches"
              color="primary"
              prepend-icon="ri-calendar-line"
            >История исследований...</VBtn>
          </div>
        </div>

      </VCol>
      <VCol cols="12" sm="12" md="6">
          <div class="d-flex gap-2">
            <v-slider
              v-model="searchForm.avg_temp"
              direction="vertical"
              :label="'Средняя температура (' + searchForm.avg_temp + '°C)'"
              show-ticks="always"
              tick-size="4"
              :ticks="tickLabelsTemp"
              :min="-50"
              :max="50"
              :step="1"
              color="success"
              :disabled="isProcessing"
            ></v-slider>

            <div class="d-flex flex-column gap-2">
              <h2 class="h2">Погода:</h2>
              <img class=" mt-8" :src="notRain" >
              <VSwitch v-model="searchForm.is_snow"
                label="Снег"
                :disabled="isProcessing"
              />
              <VSwitch v-model="searchForm.is_rain"
                color="success"
                label="Дождь"
                :disabled="isProcessing"
              />
            </div>

            <v-slider
              v-model="searchForm.precip_amount"
              direction="vertical"
              :label="'Суточные осадки (' + searchForm.precip_amount + 'мм)'"
              show-ticks="always"
              tick-size="4"
              :ticks="tickLabelsPrecip"
              :min="0"
              :max="5"
              :step="1"
              :disabled="isProcessing"
            ></v-slider>
          </div>

      </VCol>
    </VRow>

  </VContainer>
</template>

<style>

.dp__input {
  background-color: #fff0;
  padding: 8px 30px 8px 35px;
  color: #fff;
}


</style>
