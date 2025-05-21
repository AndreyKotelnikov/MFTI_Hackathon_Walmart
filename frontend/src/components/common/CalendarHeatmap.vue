<template>
  <div ref="chartContainer" style="width: 100%; height: 300px"></div>
</template>

<script lang="ts">
import type { EChartsOption } from 'echarts';
import * as echarts from 'echarts';
import { defineComponent, onMounted, ref, watch } from 'vue';

export default defineComponent({
  name: 'CalendarChart',
  props: {
    year: {
      type: String,
      default: '2016',
    },
  },
  setup(props) {
    const chartContainer = ref<HTMLElement | null>(null);
    let chartInstance: echarts.ECharts | null = null;

    const getVirtualData = (year: string): [string, number][] => {
      const date = +echarts.time.parse(year + '-01-01');
      const end = +echarts.time.parse(+year + 1 + '-01-01');
      const dayTime = 3600 * 24 * 1000;
      const data: [string, number][] = [];
      for (let time = date; time < end; time += dayTime) {
        data.push([
          echarts.time.format(time, '{yyyy}-{MM}-{dd}', false),
          Math.floor(Math.random() * 10) - 4.5,
        ]);
      }
      return data;
    };

    const updateChart = () => {
      if (!chartInstance) return;

      const option: EChartsOption = {
        title: {
          top: 0,
          left: 'center',
          text: 'Отклонение продаж от погодной нормы',
          subtext: '* На этом графике пока рандомные данные',
          textStyle: {
            color: '#d4d0e9',
          },
        },
        tooltip: {},
        visualMap: {
          min: -5,
          max: 5,
          type: 'piecewise',
          orient: 'horizontal',
          left: 'center',
          top: 65,
          inRange: {
            color: ['#56ba22', '#cc4c51'],
          },
          textStyle: {
            color: '#d3d3d3'
          }
        },
        calendar: {
          top: 120,
          left: 30,
          right: 30,
          cellSize: ['auto', 13],
          range: props.year,
          itemStyle: {
            borderWidth: 0.5,
          },
          yearLabel: { show: false },
          monthLabel: {
            color: 'white'
          },
          dayLabel: {
            color: 'white'
          }
        },
        series: {
          type: 'heatmap',
          coordinateSystem: 'calendar',
          data: getVirtualData(props.year),
        },
      };

      chartInstance.setOption(option);
    };

    onMounted(() => {
      if (chartContainer.value) {
        chartInstance = echarts.init(chartContainer.value);
        updateChart();

        // Обработка изменения размера окна
        window.addEventListener('resize', () => {
          chartInstance?.resize();
        });
      }
    });

    watch(
      () => props.year,
      () => {
        updateChart();
      }
    );

    return { chartContainer };
  },
});
</script>
