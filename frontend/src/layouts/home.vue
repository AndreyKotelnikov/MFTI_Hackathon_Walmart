<script setup lang="ts">
import Footer from '@/views/front-pages/front-page-footer.vue';
</script>

<template>
  <div
    class="layout-wrapper layout-blank"
    data-allow-mismatch
  >
    <div class="help-center-page">
      <RouterView />
      <div>
      <Footer />
    </div>
  </div>
</div>
</template>

<style>
.layout-wrapper.layout-blank {
  flex-direction: column;
}
</style>

<style lang="scss">
.help-center-page {
  .search-header {
    background-size: cover !important;
    padding-block: 7.25rem 4.75rem !important;
  }

  .help-center-section {
    padding-block: 5.25rem;
  }
}

@media (max-width: 960px) and (min-width: 600px) {
  .help-center-page {
    .v-container {
      padding-inline: 2rem !important;
    }
  }
}

@media (max-width: 599px) {
  .help-center-page {
    .search-header {
      padding-block: 7rem 2rem !important;
      padding-inline: 2rem !important;
      > .v-card-text {
        padding-left: 0;
        padding-right: 0;
      }
    }

    .help-center-section {
      padding-block: 1.5rem;
    }
  }
}

@media (max-width: 400px) {
  .help-center-page {
    .search-header {
      padding-inline: 1rem !important;
    }
  }
}
</style>
