<script setup lang="ts">

  import { useApi } from '@/composables/useApi';

  const $api = useApi()
  const isLoading = ref(true)
  const processingId = ref<number|null>(null)
  const predictionData = ref<Array<any>|null>(null)
  const totalData = ref<any|null>(null)
  const totalPagesCount = ref(0)
  const currentPage = ref(1)
  const MLModels = ref<Array<any>|null>(null)
  const mainMLModel = ref<any|null>(null)
  const metricaFilter = ref<any|null>(null)
  const selectedMarket = ref<number|null>(null)
  // const loyaltyFilterDialog = ref<typeof LoyaltyFilterDialog|null>(null)

  const headers = [
    { title: '#', key: 'store_item_code' },
    { title: 'Дата', key: 'prediction_date' },
    { title: 'Заказов', key: 'units_pred' },
    { title: 'При "0" погоде', key: 'pred_without' },
    { title: 'Рост / Падение', key: 'difference' },
    { title: 'Коэффициент', key: 'coefficient' },
    { title: 'Actions', key: 'actions', sortable: false },
  ]

  const marketsList = ref([
    { id: null, title: 'All markets' },
    { id: 1, title: 'Walmart #1 New York' },
    { id: 2, title: 'Walmart #2 San Francisco' },
    { id: 3, title: 'Walmart #3 Gravity Falls' },
  ])

  const loadData = (isResetPage = true) => {
    if (isResetPage) {
      currentPage.value = 1
    }
    isLoading.value = true
    let url = '/api/predictions/?page=' + currentPage.value

    $api.get(url)
      .then(response => {
        totalData.value = response.data
        predictionData.value = response.data.results
        totalPagesCount.value = response.data.total_pages
        isLoading.value = false
      })
  }

  const isLoadedButEmpty = computed(() => {
    return !isLoading.value && (predictionData.value != null && !predictionData.value.length)
  })

  const gotoPage = (pageNumber: number) => {
    currentPage.value = pageNumber
    loadData(false)
  }

  onMounted(() => {
    loadData()
  })

</script>

<template>
  <div class="text-center">
    <h2 class="h2">Детальное сравнение прогнозов продаж</h2>
  </div>

  <VDivider class="mt-4" />

  <p class="text-sm text-disabled mb-0 mt-1">* Сравнение прогнозируемых продаж при реальной погоде и при «0-погоде»</p>
  <p class="text-sm text-disabled">** «0-погода» - это условное понятие: температура средняя скользящая за 14 дней, синоптические события исключены, осадки = 0</p>

  <VDataTableServer
    :items-per-page="15"
    :page="currentPage"
    :headers="headers"
    :items="predictionData ?? []"
    :loading="isLoading"
    :items-length="predictionData?.length ?? 0"
    class="text-no-wrap"
    :disable-sort="true"
    no-data-text="Продажи не найдены"
  >

    <template #item.prediction_date="{ item }">
      <div v-if="item.prediction_date" class="text-center">
        {{ item.prediction_date }}
      </div>
    </template>

    <template #item.units_pred="{ item }">
      <div v-if="item.units_pred" class="text-center">
        {{ item.units_pred.toFixed(2) }}
      </div>
    </template>

    <template #item.pred_without="{ item }">
      <div v-if="item.pred_without" class="text-center">
        {{ item.pred_without.toFixed(2) }}
      </div>
    </template>

    <template #item.difference="{ item }">
      <div class="text-center">
        <VChip v-if="item.difference"
          :color="item.difference > 0 ? 'success' : 'error'"
          class="mx-auto"
        >
          <VIcon v-if="item.difference > 0" icon="ri-arrow-up-s-fill"/>
          <VIcon v-else icon="ri-arrow-down-s-fill"/>
          {{ item.difference.toFixed(2) }} ед.
        </VChip>
      </div>
    </template>

    <template #item.coefficient="{ item }">
      <div v-if="item.coefficient" class="text-center">
        {{ item.coefficient.toFixed(3) }}
      </div>
    </template>

    <template #item.actions="{ item }">
      <div class="text-center">
        <VBtn prepend-icon="ri-eye-fill" :to="'/prediction/' + item.id" variant="plain"
          class="mx-auto"
          color="success"
        >
          Подробнее...
        </VBtn>
      </div>
    </template>

    <template #bottom>
    </template>
  </VDataTableServer>

  <VPagination v-if="totalPagesCount"
    @update:model-value="gotoPage"
    :model-value="currentPage"
    active-color="primary"
    :length="totalPagesCount"
    :total-visible="$vuetify.display.xs ? 1 : Math.min(totalPagesCount, 5)"
    class="my-8"
  />
</template>

<style>
  .v-data-table-header__content {
    text-align: center !important;
    justify-content: center
  }
</style>
