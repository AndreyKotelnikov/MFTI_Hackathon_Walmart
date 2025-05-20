<script setup lang="ts">
  
  const is_loading = ref(true)

  const widgetData = ref([
    { title: 'Прогноз продаж', value: '2 343 ед.', desc: 'При текущей погоде', icon: 'ri-rainy-line', iconColor: 'warning' },
    { title: 'Прогноз продаж', value: '2 721 ед.', desc: 'При нормальной погоде', icon: 'ri-temp-hot-line', iconColor: 'success' },
    { title: 'Повышение спроса', value: '+378 ед.', desc: 'Суммарная разница', icon: 'ri-truck-line', iconColor: 'primary' },
    { title: 'Средний коэффициент', value: '14%', desc: 'Доля влияния погоды', icon: 'ri-percent-line', iconColor: 'error' },
  ])

  const loadWidget = () => {
    is_loading.value = false
    // axios.get('/api/consolidated/')
  }

  onMounted(() => {
    loadWidget()
  })

</script>

<template>
  <div class="d-flex mb-6">
    <VRow>
      <template
        v-for="(widgetItem, id) in widgetData"
        :key="id"
      >
        <VCol
          cols="12"
          md="3"
          sm="6"
        >
          <VCard>
            <VCardText>
              <div class="d-flex justify-space-between">
                <div class="d-flex flex-column gap-y-1">
                  <span class="text-body-1 text-medium-emphasis">
                    {{ widgetItem.title }}
                  </span>
                  <div>
                    <h4 class="text-h4">
                      {{ widgetItem.value }}
                      <!-- <span
                        class="text-base "
                        :class="data.change > 0 ? 'text-success' : 'text-error'"
                      >({{ prefixWithPlus(data.change) }}%)</span> -->
                    </h4>
                  </div>
                  <span class="text-sm">{{ widgetItem.desc }}</span>
                </div>
                <VAvatar
                  :color="widgetItem.iconColor"
                  variant="tonal"
                  rounded
                  size="38"
                >
                  <VIcon
                    :icon="widgetItem.icon"
                    size="26"
                  />
                </VAvatar>
              </div>
            </VCardText>
          </VCard>
        </VCol>
      </template>
    </VRow>
  </div>
</template>
