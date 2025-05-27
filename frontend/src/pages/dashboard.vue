<script setup lang="ts">
import CalendarHeatmap from '@/components/common/CalendarHeatmap.vue';
import UsaMapPie from '@/components/common/UsaMapPie.vue';
import { useApi } from '@/composables/useApi';
import Consolidated from '@/views/dashboard/Consolidated.vue';
import Products from '@/views/dashboard/Products.vue';
import ResearchHeader from '@/views/dashboard/ResearchHeader.vue';

const $api = useApi()
const $route = useRoute()
const isLoading = ref(true)
const storesList = ref<Array<any>|null>(null)
const researchData = ref<any|null>(null)
const researchId = ref<number|null>($route.params.id ? Number($route.params.id) : null)

const loadData = async () => {
  isLoading.value = true
   await $api.get(`/api/researches/${researchId.value}/`)
  .then(response => {
    researchData.value = response.data
  })

  let url = '/api/stores/list'
  await $api.get(url)
    .then(response => {
      storesList.value = response.data
    })
  isLoading.value = false
}
  
  const filtersList = [
    'Фильтрация по городам',
    'Фильтрация по магазинам',
    'Фильтрация по товарам',
    'Фильтрация по временным переодам',
  ]


  onMounted(() => {
    loadData()
  })


</script>

<template>
  <VAlert v-if="!researchId" color="error" title="Не указан идентификатор исследования" />
  <VContainer v-else>

    <ResearchHeader v-if="researchData" :research="researchData" />

    <Consolidated />

    <div class="d-flex mb-6">
      <VRow>
        <template
          v-for="(filterName, id) in filtersList"
          :key="id"
        >
          <VCol
            cols="12"
            md="3"
            sm="6"
          >
            TODO: {{filterName}}
          </VCol>
        </template>
      </VRow>
    </div>

    <UsaMapPie v-if="storesList"
      :stores-list="storesList"
      class="mt-4"
    />

    <CalendarHeatmap />

    <Products :research-id="researchId" />
    
  </VContainer>

</template>

<style>
.v-btn {
  text-transform: none;
}
</style>
