<script setup lang="ts">
import UsaMapPie from '@/components/common/UsaMapPie.vue';
import { useApi } from '@/composables/useApi';
import Consolidated from '@/views/dashboard/Consolidated.vue';
import Products from '@/views/dashboard/Products.vue';
import ResearchHeader from '@/views/dashboard/ResearchHeader.vue';
import TopRatingItems from '@/views/dashboard/TopRatingItems.vue';

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

  let url = '/api/stores/list?research_id=' + researchId.value
  await $api.get(url)
    .then(response => {
      storesList.value = response.data
    })
  isLoading.value = false
}

const itemsRating = computed(() => {
  if (!researchData.value) {
    return []
  }

  return JSON.parse(researchData.value.items_ratios_json)

})
  

  onMounted(() => {
    loadData()
  })


</script>

<template>
  <VAlert v-if="!researchId" color="error" title="Не указан идентификатор исследования" />
  
  <VContainer v-else>

    <ResearchHeader v-if="researchData" :research="researchData" />

    <Consolidated class="pb-8" :research="researchData" />

    <UsaMapPie v-if="storesList"
      :stores-list="storesList"
      class="mt-4"
    />

    <TopRatingItems  v-if="researchData" :items="itemsRating" />

    <!-- <CalendarHeatmap /> -->

    <Products :research-id="researchId" />
    
  </VContainer>

</template>

<style>
.v-btn {
  text-transform: none;
}
</style>
