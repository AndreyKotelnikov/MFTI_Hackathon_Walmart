<script setup lang="ts">

import SelectPeriodMode from '@/components/home/SelectPeriodMode.vue';
import SelectSeason from '@/components/search/SelectSeason.vue';
import Datepicker from '@vuepic/vue-datepicker';
import moment from 'moment';

  const $props = defineProps({
    mode: {
      type: String,
      required: true
    },
    periodStart: {
      type: String,
      required: true
    },
    periodEnd: {
      type: String,
      required: true
    },
    disabled: {
      type: Boolean,
      default: false
    },
  })

  const $emit = defineEmits()

  const PeriodModes = {
    Week: 'week',
    Month: 'month',
    Period: 'period',
    Season: 'season',
  }
  const periodMode = ref(PeriodModes.Week)
  const selectedRange = ref([ "2014-10-27T18:01:00.000Z", "2014-10-31T18:01:00.000Z" ])
  const selectedWeek = ref([ "2014-10-19T20:00:00.000Z", "2014-10-26T20:59:59.999Z" ])
  const selectedSeason = ref([ "2014-09-01", "2014-11-01" ])
  const selectedMonth = ref({ "month": 9, "year": 2014 } )
  const maxDate = ref(moment('2014-10-31', 'YYYY-MM-DD').toDate())
  const minDate = ref(moment('2012-01-01', 'YYYY-MM-DD').toDate())

  const changeValue = () => {
    $emit('update:mode', periodMode.value)

    switch(periodMode.value) {
      case PeriodModes.Week: {
        const valueStart = moment(selectedWeek.value[0]).format('YYYY-MM-DD')
        const valueEnd = moment(selectedWeek.value[1]).format('YYYY-MM-DD')
        $emit('update:period-start', valueStart)
        $emit('update:period-end', valueEnd)
        break
      }
      case PeriodModes.Month: {
        const value = selectedMonth.value.year + '-' + selectedMonth.value.month + '-01'
        const firsDay = moment(value, 'YYYY-MM-DD')
        const lastDay = moment(value, 'YYYY-MM-DD').add(1, 'months').add(-1, 'days')
        const valueStart = firsDay.format('YYYY-MM-DD')
        const valueEnd = lastDay.format('YYYY-MM-DD')
        $emit('update:period-start', valueStart)
        $emit('update:period-end', valueEnd)
        break
      }
      case PeriodModes.Period: {
        const valueStart = moment(selectedRange.value[0]).format('YYYY-MM-DD')
        const valueEnd = moment(selectedRange.value[1]).format('YYYY-MM-DD')
        $emit('update:period-start', valueStart)
        $emit('update:period-end', valueEnd)
        break
      }
      case PeriodModes.Season: {
        const valueStart = selectedSeason.value[0]
        const valueEnd = moment(selectedSeason.value[1], 'YYYY-MM-DD').add(-1, 'days').format('YYYY-MM-DD')
        $emit('update:period-start', valueStart)
        $emit('update:period-end', valueEnd)
        break
      }
    }
  }

  onMounted(() => changeValue())

</script>

<template>
  <SelectPeriodMode v-model="periodMode" class="mb-2"
    @update:model-value="changeValue"
    :disabled="disabled"
  />
  <Datepicker v-if="periodMode == 'week'"
    v-model="selectedWeek"
    week-picker
    auto-apply
    :enable-time-picker="false"
    :max-date="maxDate"
    :min-date="minDate"
    :disabled="disabled"
    @update:model-value="changeValue"
  />
  <Datepicker v-if="periodMode == 'month'"
    v-model="selectedMonth"
    month-picker
    auto-apply
    :enable-time-picker="false"
    :max-date="maxDate"
    :min-date="minDate"
    :disabled="disabled"
    @update:model-value="changeValue"
  />
  <Datepicker v-if="periodMode == 'period'"
    v-model="selectedRange"
    range
    auto-apply
    :enable-time-picker="false"
    format="dd.MM.yyyy"
    :max-date="maxDate"
    :min-date="minDate"
    :disabled="disabled"
    @update:model-value="changeValue"
  />
  <SelectSeason v-if="periodMode == 'season'"
    v-model="selectedSeason"
    :disabled="disabled"
    @update:model-value="changeValue"
  />
</template>
