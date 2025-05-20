<script lang="ts" setup>
// import VerticalNavSectionTitle from '@/@layouts/components/VerticalNavSectionTitle.vue';
import VerticalNavLink from '@layouts/components/VerticalNavLink.vue';
</script>

<template>
  <VerticalNavLink :item="{
    title: 'Общая аналитика',
    icon: 'ri-bar-chart-box-line',
    to: '/',
  }" />
  <!-- <VerticalNavSectionTitle :item="{
    heading: 'ML Модели',
  }" />
  <VerticalNavLink :item="{
    title: 'Клиенты/Прогноз',
    icon: 'ri-user-line',
    to: '/customers',
    badgeContent: '!',
    badgeClass: 'bg-light-error text-error',
  }" /> -->
</template>
