<script setup lang="ts">
import UsaMapPie from '@/components/common/UsaMapPie.vue';
import Consolidated from '@/views/dashboard/Consolidated.vue';
import Products from '@/views/dashboard/Products.vue';

</script>

<template>
  <VContainer>

    <Consolidated />

    <UsaMapPie />

    <Products />
    
  </VContainer>

</template>

<style>
.v-btn {
  text-transform: none;
}
</style>
