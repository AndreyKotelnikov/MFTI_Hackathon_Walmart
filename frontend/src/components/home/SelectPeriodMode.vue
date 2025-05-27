<script setup lang="ts">
  const periodLocal = ref(null)

  defineProps({
    disabled: {
      type: Boolean,
      default: false
    },
  })
</script>

<template>
  <v-btn-toggle v-model="periodLocal"
    divided
    :disabled="disabled"
    color="success"
    group
  >
    <v-btn value="week" min-width="100">
      <span class="hidden-sm-and-down">Неделя</span>

      <v-icon end>
        ri-calendar-todo-line
      </v-icon>
    </v-btn>

    <v-btn value="month" min-width="100">
      <span class="hidden-sm-and-down">Месяц</span>

      <v-icon end>
        ri-calendar-check-line
      </v-icon>
    </v-btn>

    <v-btn value="season" min-width="100">
      <span class="hidden-sm-and-down">Сезон</span>

      <v-icon end>
        ri-calendar-todo-fill
      </v-icon>
    </v-btn>

    <v-btn value="period" min-width="100">
      <span class="hidden-sm-and-down">Период</span>

      <v-icon end>
        ri-calendar-schedule-line
      </v-icon>
    </v-btn>
  </v-btn-toggle>
</template>
