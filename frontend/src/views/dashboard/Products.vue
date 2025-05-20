<script setup lang="ts">

  import CompactDatePicker from '@/components/common/CompactDatePicker.vue';
import { useApi } from '@/composables/useApi';
// import LoyaltyFilterDialog from '@/views/customers/LoyaltyFilterDialog.vue';

//   import avatar1 from '@images/avatars/avatar-1.png';
// import avatar2 from '@images/avatars/avatar-2.png';
// import avatar3 from '@images/avatars/avatar-3.png';
// import avatar4 from '@images/avatars/avatar-4.png';
// import avatar5 from '@images/avatars/avatar-5.png';
// import avatar6 from '@images/avatars/avatar-6.png';
// import avatar7 from '@images/avatars/avatar-7.png';
// import avatar8 from '@images/avatars/avatar-8.png';

  const $api = useApi()
  const isLoading = ref(true)
  const processingId = ref<number|null>(null)
  const servicesData = ref<Array<any>|null>(null)
  const totalData = ref<any|null>(null)
  const totalPagesCount = ref(0)
  const currentPage = ref(1)
  const MLModels = ref<Array<any>|null>(null)
  const mainMLModel = ref<any|null>(null)
  const metricaFilter = ref<any|null>(null)
  const selectedMarket = ref<number|null>(null)
  // const loyaltyFilterDialog = ref<typeof LoyaltyFilterDialog|null>(null)

  const headers = [
    { title: 'Идентификатор', key: 'id' },
    { title: 'Наименование', key: 'name' },
    { title: 'Заказов', key: 'units' },
    { title: 'При нормальной погоде', key: 'nunits' },
    { title: 'Коэффициент', key: 'koef' },
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
    setTimeout(() => {
      totalData.value = [
        { id: 1, name: 'Зонтик', units: 22, nunits: 13, koef: -0.2 },
        { id: 2, name: 'Бумажные полотенца', units: 312, nunits: 13, koef: -0.23 },
        { id: 3, name: 'Хлеб пшеничный', units: 412, nunits: 13, koef: 0.4 },
        { id: 4, name: 'Яблоки', units: 52, nunits: 513, koef: 0.2 },
        { id: 5, name: 'Куриные крылышки', units: 42, nunits: 13, koef: -0.3 },
        { id: 6, name: 'Кондиционер для белья', units: 212, nunits: 13, koef: 0.2 },
        { id: 7, name: 'Coca-Cola', units: 62, nunits: 13, koef: 0.45 },
        { id: 8, name: 'Пицца замороженная', units: 72, nunits: 13, koef: 0.12 },
        { id: 9, name: 'Корм для кошек', units: 82, nunits: 13, koef: 0.45 },
        { id: 10, name: 'Зубная паста', units: 62, nunits: 13, koef: 0.43 },
      ]
      // totalData.value.forEach((item: any) => {
      //   item.photo = getRundomPhoto()
      // })
      servicesData.value = totalData.value
      totalPagesCount.value = 3
      isLoading.value = false
            
    }, 500);
  }

  // const getRundomPhoto = () => {
  //   const photos = [avatar1, avatar2, avatar3, avatar4, avatar5, avatar6, avatar7, avatar8]
  //   return photos[Math.floor(Math.random() * photos.length)]
  // }

  const isLoadedButEmpty = computed(() => {
    return !isLoading.value && (servicesData.value != null && !servicesData.value.length)
  })

  const gotoPage = (pageNumber: number) => {
    currentPage.value = pageNumber
    loadData(false)
  }

  // const openFilterDialog = () => {
  //   loyaltyFilterDialog.value?.open(
  //     metricaFilter.value ? metricaFilter.value.recall : null
  //   )
  // }

  onMounted(() => {
    loadData()
  })

</script>

<template>
  <div class="d-flex flex-wrap items-center">
    <h3>Товары магазинов</h3>
    <VSpacer />
    <div class="d-flex flex-wrap align-center">

      <VSelect width="200px" 
        v-model="selectedMarket"
        item-value="id"
        :items="marketsList"></VSelect>

      <CompactDatePicker :value="'13.03.2024'" />
      <!-- <VBtn
        :color="metricaFilter ? 'success' : 'primary'"
        prepend-icon="ri-search-line"
        :disabled="!mainMLModel"
        :loading="!mainMLModel"
      >
        {{ metricaFilter 
          ? `Лояльность: массовость: ${metricaFilter.recall}%, точность: ${metricaFilter.precision}%` 
          : 'Фильтрация по уровню лояльности' }}
      </VBtn> -->
    </div>
  </div>

  <VDivider class="mt-4" />

  <VDataTableServer
    :items-per-page="15"
    :page="currentPage"
    :headers="headers"
    :items="servicesData ?? []"
    :loading="isLoading"
    :items-length="servicesData?.length ?? 0"
    class="text-no-wrap"
    :disable-sort="true"
    no-data-text="Клиенты не найдены"
  >
    <template #item.customer_unique_id="{ item }">
      <div class="d-flex align-center gap-x-4" style="min-width: 250px; line-height: 1.2;">
        <VAvatar
          size="38"
          variant="tonal"
          rounded
          :image="item.photo"
        />
        <div class="d-flex flex-column">
          <RouterLink :to="'/customers/' + item.id"
            style="white-space: wrap;"
          >
            {{ item.fullname }}
          </RouterLink>
          <span class="text-body-2">
            {{ item.customer_unique_id }}
          </span>
        </div>
      </div>
    </template>

    <!-- category -->
    <template #item.state_code="{ item }">
      <VChip class="text-uppercase">
        {{ item.state_code }}
      </VChip>
    </template>

    <template #item.orders_total="{ item }">
      <div class="text-center">
        {{ item.orders_total }}
      </div>
    </template>

    <template #item.actions="{ item }">
      <VBtn  icon="ri-eye-fill" :to="'/customers/' + item.id" variant="plain" />
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
