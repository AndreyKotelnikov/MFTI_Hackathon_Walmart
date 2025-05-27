<script setup lang="ts">

const storeData = [
  { store_id: 's1', items: '1-28, 1-40, 1-47, 1-51, 1-89, 1-9, 1-93, 1-99'.split(', ') },
  { store_id: 's2', items: '2-11, 2-44, 2-5, 2-85, 2-93'.split(', ') },
  { store_id: 's3', items: '3-102, 3-109, 3-2, 3-45, 3-5, 3-93'.split(', ') },
  { store_id: 's4', items: '4-101, 4-27, 4-9, 4-90, 4-93, 4-96, 4-97'.split(', ') },
  { store_id: 's5', items: '5-105, 5-16, 5-20, 5-32, 5-37, 5-93'.split(', ') },
  { store_id: 's6', items: '6-107, 6-14, 6-45, 6-9'.split(', ') },
  { store_id: 's7', items: '7-23, 7-5, 7-7, 7-93, 7-95'.split(', ') },
  { store_id: 's8', items: '8-100, 8-23, 8-5, 8-59, 8-84, 8-93'.split(', ') },
  { store_id: 's9', items: '9-10, 9-105, 9-42, 9-45, 9-5, 9-93'.split(', ') },
  { store_id: 's10', items: '10-21, 10-37, 10-5, 10-86, 10-93'.split(', ') },
  { store_id: 's11', items: '11-110, 11-61, 11-68, 11-86, 11-87, 11-9'.split(', ') },
  { store_id: 's12', items: '12-16, 12-37, 12-79, 12-86, 12-93'.split(', ') },
  { store_id: 's13', items: '13-104, 13-36, 13-46, 13-5, 13-93'.split(', ') },
  { store_id: 's14', items: '14-15, 14-25, 14-33, 14-50, 14-70, 14-88, 14-9, 14-93'.split(', ') },
  { store_id: 's15', items: '15-15, 15-17, 15-45, 15-49, 15-5, 15-61, 15-86, 15-93'.split(', ') },
  { store_id: 's16', items: '16-16, 16-25, 16-39, 16-50, 16-64, 16-77, 16-85, 16-93'.split(', ') },
  { store_id: 's17', items: '17-37, 17-48, 17-71, 17-9'.split(', ') },
  { store_id: 's18', items: '18-37, 18-5, 18-57, 18-72'.split(', ') },
  { store_id: 's19', items: '19-15, 19-16, 19-39, 19-69, 19-75, 19-83, 19-88, 19-93'.split(', ') },
  { store_id: 's20', items: '20-106, 20-18, 20-41, 20-5, 20-74, 20-93'.split(', ') },
  { store_id: 's21', items: '21-109, 21-44, 21-5, 21-91'.split(', ') },
  { store_id: 's22', items: '22-104, 22-54, 22-68, 22-78, 22-9, 22-93'.split(', ') },
  { store_id: 's23', items: '23-29, 23-45, 23-5, 23-56'.split(', ') },
  { store_id: 's24', items: '24-43, 24-6, 24-60, 24-76, 24-97'.split(', ') },
  { store_id: 's25', items: '25-12, 25-45, 25-50, 25-81, 25-84, 25-9, 25-93'.split(', ') },
  { store_id: 's26', items: '26-2, 26-45, 26-5'.split(', ') },
  { store_id: 's27', items: '27-21, 27-68, 27-80, 27-9, 27-93'.split(', ') },
  { store_id: 's28', items: '28-2, 28-35, 28-45, 28-5'.split(', ') },
  { store_id: 's29', items: '29-41, 29-45, 29-56, 29-8'.split(', ') },
  { store_id: 's30', items: '30-13, 30-16, 30-44, 30-49, 30-51, 30-65'.split(', ') },
  { store_id: 's31', items: '31-104, 31-45, 31-67, 31-9, 31-93, 31-98'.split(', ') },
  { store_id: 's32', items: '32-19, 32-45, 32-51, 32-58, 32-86, 32-9, 32-93'.split(', ') },
  { store_id: 's33', items: '33-44, 33-85, 33-9, 33-92, 33-93'.split(', ') },
  { store_id: 's34', items: '34-31, 34-45, 34-52, 34-84, 34-9, 34-93'.split(', ') },
  { store_id: 's35', items: '35-105, 35-16, 35-24, 35-49, 35-50, 35-63, 35-66, 35-93'.split(', ') },
  { store_id: 's36', items: '36-1, 36-30, 36-44, 36-9'.split(', ') },
  { store_id: 's37', items: '37-104, 37-105, 37-15, 37-38, 37-45, 37-5, 37-53'.split(', ') },
  { store_id: 's38', items: '38-45, 38-52, 38-86, 38-9, 38-93, 38-98'.split(', ') },
  { store_id: 's39', items: '39-103, 39-111, 39-36, 39-9'.split(', ') },
  { store_id: 's40', items: '40-106, 40-15, 40-45, 40-5, 40-51, 40-55, 40-93'.split(', ') },
  { store_id: 's41', items: '41-108, 41-16, 41-61, 41-68, 41-86, 41-93'.split(', ') },
  { store_id: 's42', items: '42-45, 42-5, 42-82'.split(', ') },
  { store_id: 's43', items: '43-105, 43-16, 43-3, 43-37, 43-73, 43-93'.split(', ') },
  { store_id: 's44', items: '44-105, 44-5, 44-62, 44-68, 44-93, 44-94'.split(', ') },
  { store_id: 's45', items: '45-22, 45-26, 45-34, 45-4, 45-50, 45-9'.split(', ') },
]

defineProps({
  storeId: {
    type: String as () => string|null,
    refault: null
  },
  itemId: {
    type: String as () => string|null,
    refault: null
  },
  disabled: {
    type: Boolean,
    default: false
  },
})

const $emit = defineEmits()

const selectedStore = ref<null|string>(null)
const selectedItem = ref<null|string>(null)

const storesItems = computed(() => {
  return storeData.map(x => {
    return {
      id: x.store_id,
      title: 'Магазин №' + x.store_id 
    }
  })
})

const itemsItems = computed(() => {
  if (!selectedStore.value) {
    return []
  }
  const store = storeData.find(x => x.store_id == selectedStore.value)
  return store?.items.map((x: any) => {
    return {
      id: x,
      title: 'Товар №' + x
    }
  })
})

const changeStore = () => {
  console.log('Selected store:', selectedStore.value) // Добавьте лог
  selectedItem.value = null
  $emit('update:store-id', selectedStore.value)
  $emit('update:item-id', selectedItem.value)
}

const changeItem = () => {
  $emit('update:item-id', selectedItem.value)
}

</script>

<template>
  <div class="d-flex mt-2 gap-2">
    <VSelect label="Магазин" :items="storesItems"
      v-model="selectedStore"
      item-value="id"
      item-title="title"
      :disabled="disabled"
      @update:model-value="changeStore"
    />
    <VSelect label="Товар" :items="itemsItems"
      :disabled="!selectedStore || disabled"
      v-model="selectedItem"
      item-value="id"
      item-title="title"
      @update:model-value="changeItem"
    />
  </div>
</template>
