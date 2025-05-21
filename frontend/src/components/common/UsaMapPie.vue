<template>
  <v-chart ref="chartMap" :option="option" style="height: 600px; width: 100%;" />
</template>

<script setup lang="ts">
import usaJson from '@images/USA.json'
import { MapChart, PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, VisualMapComponent } from 'echarts/components'
import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { ref } from 'vue'

const $props = defineProps({
  storesList: {
    type: Array,
    required: true
  }
})

// Регистрируем нужные компоненты
echarts.use([MapChart, PieChart, TitleComponent, TooltipComponent, VisualMapComponent, CanvasRenderer])

// Регистрируем карту США
echarts.registerMap('USA', usaJson as any, {
  Alaska: {
    left: -131,
    top: 25,
    width: 15
  },
  Hawaii: {
    left: -110,
    top: 28,
    width: 5
  },
  'Puerto Rico': {
    left: -76,
    top: 26,
    width: 2
  }
})

const createStorePie = (storeItem: any) => {
  return randomPieSeries([storeItem.station_detail.longitude, storeItem.station_detail.latitude], 25)
}

const randomPieSeries = (center: any, radius: any) => {
  const data = ['12', '11', '45', '34'].map((t) => {
    const value = Math.round(Math.random() * 100) - 50
    const mark = value >= 0 ? '' : '🔻'
    return {
      value: value,
      name: 'Товар #' + t
    };
  });
  return {
    type: 'pie',
    coordinateSystem: 'geo',
    tooltip: {
      formatter: '{b}: 🔻{c} ({d}%)'
    },
    label: {
      show: false
    },
    labelLine: {
      show: false
    },
    animationDuration: 0,
    radius,
    center,
    data
  };
}


const option = ref({
  title: {
    text: 'Отклонение продаж по магазинам',
    subtext: '* Доли по наиболее волатильным товарам',
    left: 'center',
    textStyle: {
      color: '#d4d0e9'
    },
  },
  tooltip: {
    trigger: 'item'
  },
  geo: {
    map: 'USA',
    roam: true,
    label: {
      show: false
    },
    itemStyle: {
      areaColor: '#f3f3f3',
      borderColor: '#999'
    }
  },
  series: $props.storesList.map(s => createStorePie(s))
})
</script>
