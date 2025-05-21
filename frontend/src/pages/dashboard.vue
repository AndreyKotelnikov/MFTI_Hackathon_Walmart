<script setup lang="ts">
import CalendarHeatmap from '@/components/common/CalendarHeatmap.vue';
import UsaMapPie from '@/components/common/UsaMapPie.vue';
import { useApi } from '@/composables/useApi';
import Consolidated from '@/views/dashboard/Consolidated.vue';
import Products from '@/views/dashboard/Products.vue';

const $api = useApi()
  const isLoading = ref(true)
  const storesList = ref<Array<any>|null>(null)


const loadData = () => {
    isLoading.value = true
    let url = '/api/stores/list'
    $api.get(url)
      .then(response => {
        storesList.value = response.data
        isLoading.value = false
      })
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
  <VContainer>

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

    <h2 class="h2">Что сделано:</h2>
    <ul class="text-success">
      <li>Сгенерированно 2 таблицы: одна с предоставленными погодными признаками, вторая с очищенными</li>
      <li>По обеим таблицам проставлены предсказания количества проданных позиций</li>
      <li>Загрузка списка городов по api и отображение на карте</li>
      <li>Загрузка списка предсказаний и отображение в таблице с пагинацией</li>
      <li>Детальное отображение предсказание</li>
    </ul>
    <h2 class="h2 mt-4">Что планируется сделать:</h2>
    <ul class="text-warning">
      <li>Подчитать и отобразить действительные общие параметры в шапке</li>
      <li>Фильтрация данных по: городу, магазину, товару</li>
      <li>Группировка данных по переодам: неделя, месяц, сезон</li>
      <li>Фильтрация данных по выбранному временному периоду</li>
      <li>Улучшение качества прогнозов ML модели</li>
      <li>Детальное отображение параметров 2х прогнозов: настоящего и очищенного</li>
      <li>Визуализация SHAPE анализа значимости признаков в деталлизации</li>
      <li>Отображение на карте наиболее значимых долей изменения продаж</li>
      <li>Отображение на heap-map действительных погодных изменений продаж</li>
      <li>Линейный график динамики влияния погоды на продажи за период</li>
    </ul>

    <UsaMapPie v-if="storesList"
      :stores-list="storesList"
      class="mt-4"
    />

    <CalendarHeatmap />

    <Products />
    
  </VContainer>

</template>

<style>
.v-btn {
  text-transform: none;
}
</style>
