<script setup lang="ts">

  
  const $props = defineProps({
    modelValue: {
      type: Array as () => Array<string>,
      required: true
    },
    disabled: {
      type: Boolean,
      default: false
    },
  })

  const $emit = defineEmits()

  const localYear = ref<number|null>(null)
  const localSeason = ref<string|null>(null)

  const syncLocalValues = () => {
    const dateStart = new Date($props.modelValue[0])
    const dateEnd = new Date($props.modelValue[1])
    localSeason.value = (dateStart.getMonth() + 1) + '-' + (dateEnd.getMonth() + 1)
    localYear.value = dateStart.getFullYear()
  }

  const changeValue = () => {
    const seasons = localSeason.value?.split('-')
    if (!seasons || ! localYear.value) {
      return
    }
    const dateSelectedStart = localYear.value + '-' + seasons[0] + '-01'
    const dateSelectedEnd = localYear.value + '-' + seasons[1] + '-01'

    $emit('update:modelValue', [
      dateSelectedStart,
      dateSelectedEnd
    ])
  }

  onMounted(() => syncLocalValues())
  watch(() => $props.modelValue, () => syncLocalValues())

</script>

<template>
  <div class="d-flex mt-2 gap-2">
    <VSelect label="Год" :items="[
        { id: 2012, title: '2012' },
        { id: 2013, title: '2013' },
        { id: 2014, title: '2014' },
      ]"
      v-model="localYear"
      :disabled="disabled"
      item-value="id"
      item-title="title"
      @update:model-value="changeValue"
    />

    <VSelect label="Сезон" :items="[
        { id: '12-2', title: 'Зима' },
        { id: '03-5', title: 'Весна' },
        { id: '6-8', title: 'Лето' },
        { id: '9-11', title: 'Осень' },
      ]"
      v-model="localSeason"
      :disabled="disabled"
      item-value="id"
      item-title="title"
      @update:model-value="changeValue"
    />
  </div>
</template>
