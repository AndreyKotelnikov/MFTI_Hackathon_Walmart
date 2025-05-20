<template>
  <v-chart ref="chartMap" :option="option" style="height: 600px; width: 100%" />
</template>

<script setup lang="ts">
import usaJson from '@images/USA.json'
// import imageCloudRain from '@images/maps/cloud-rain.png'
import { MapChart, PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, VisualMapComponent } from 'echarts/components'
import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { ref } from 'vue'

// const chartMap = ref<null|any>(null)

// Регистрируем нужные компоненты
echarts.use([MapChart, PieChart, TitleComponent, TooltipComponent, VisualMapComponent, CanvasRenderer])

// const point = echarts.convertToPixel({ geoIndex: 0 }, [37.62, 55.75]) 

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
    text: 'Прогноз продаж с учётом погоды',
    subtext: 'Сеть магазинов Пятёрочка',
    left: 'center',
    textStyle: {
      color: '#868646'
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
  // graphic: [
  //   {
  //     type: 'image',
  //     id: 'cloud-gif',
  //     left: 300, // px по canvas
  //     top: 200,  // px по canvas
  //     image: imageCloudRain, // положи в public или assets
  //     style: {
  //       image: imageCloudRain, // положи в public или assets
  //       // image: '/images/maps/cloud-rain.gif', // положи в public или assets
  //       width: 60,
  //       height: 60,
  //       opacity: 1,
  //       zIndex: 11
  //     }
  //   }
  // ],
  series: [
      randomPieSeries([-86.753504, 33.01077], 15),
      randomPieSeries([-99, 38.5], 25),
      randomPieSeries([-116.853504, 39.8], 25),
      randomPieSeries([-99, 31.5], 30),
      randomPieSeries(
        // it's also supported to use geo region name as center since v5.4.1
        +echarts.version.split('.').slice(0, 3).join('') > 540
          ? 'Maine'
          : // or you can only use the LngLat array
            [-69, 45.5],
        12
      )
    // {
    //   type: 'pie',
    //   coordinateSystem: 'geo',
    //   label: {
    //     show: false
    //   },
    //   data: [
    //     { name: 'California', value: 20 },
    //     { name: 'Texas', value: 15 },
    //     { name: 'New York', value: 10 }
    //   ],
    //   encode: {
    //     value: 'value'
    //   },
    //   center: [120, 40], // условные координаты на карте, можно вручную сместить
    //   radius: 30
    // }
  ]
})
</script>
