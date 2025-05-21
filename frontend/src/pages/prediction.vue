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
          Сравнение предсказаний по реальной погоде и по "очищенной"
        </h2>
        <h3 class="h3 mb-8 text-disabled">
          Товар: {{ predictionData.store_item_code }}
          дата: {{ predictionData.prediction_date }}
        </h3>
        <p class="text-error">* Раздел в процессе доработки</p>
      </div>
    </div>
    <VRow>
      <VCol cols="12" md="6" sm="12">
        <PredictionCard :item="predictionData" />
      </VCol>
      <VCol cols="12" md="6" sm="12">
        <PredictionCard :item="predictionData" />
      </VCol>
    </VRow>
  </VContainer>
  <div v-else class="text-center pt-16" style="min-height: calc(100vh - 96px);">
    <VProgressCircular class="mt-16"
      :indeterminate="true"
    />
  </div>
</template>
