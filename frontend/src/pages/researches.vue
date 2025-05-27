<script lang="ts" setup>
import { useApi } from '@/composables/useApi';
import { useRoute } from 'vue-router';

const route = useRoute()

const $api = useApi()
const $route = useRoute()
const $router = useRouter()
const isLoading = ref(true)
const researchesList = ref<any|null>(null)

const loadData = () => {
  isLoading.value = true

  $api.get(`/api/researches/`)
    .then(response => {
      researchesList.value = response.data
      isLoading.value = false
    })
}


onMounted(() => {
  loadData()
})

</script>

<template>
  <VContainer v-if="researchesList" class="mb-8">
    <div class="d-flex">
      <VBtn icon="ri-arrow-left-s-line"
        @click="$router.back()"
        class="mr-4"
      />
      <div>
        <h2 class="h2">
          История исследований
        </h2>
      </div>
    </div>

    <VList>
      <VListItem :to="'/dashboard/' + research.id" v-for="research in researchesList">
        <VListItemTitle>
          <h3 class="h3 mb-1">
            Исследование #{{ research.id }}
          </h3>
          <div class="d-flex align-center flex-wrap">
            <v-icon icon="ri-calendar-fill" size="small" class="mr-1" />
            <span class="text-body-1 mr-2">Период:</span>
            <span class="font-weight-medium">
              {{ research.period_start }} — {{ research.period_end }}
            </span>
          </div>
        </VListItemTitle>
      </VListItem>
    </VList>

  </VContainer>
  <div v-else class="text-center pt-16" style="min-height: calc(100vh - 96px);">
    <VProgressCircular class="mt-16"
      :indeterminate="true"
    />
  </div>
</template>
