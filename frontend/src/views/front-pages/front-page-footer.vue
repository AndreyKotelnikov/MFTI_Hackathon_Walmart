<script setup lang="ts">

import { useApi } from '@/composables/useApi';
import footerLightBg from '@images/front-pages/backgrounds/footer-bg-light.png';
import footerLogo from '@images/front-pages/footer-logo.png';

const $api = useApi()
const pagesPragments = ref<any>({
  FooterSignature: { title: '', content: '' },
})

interface Menu {
  title: string
  path: string
}

const pagesList: Menu[] = [
{
  title: 'Распознать заболевание',
    path: '#dashboard-header'
  },
]

const demoList = [
  {
    title: 'О команде',
    path: '#about-company',
  },
]

onMounted(() => {
})

</script>

<template>
  <div class="footer">
    <div
      class="footer-top"
      :style="{ 'background-image': `url(${footerLightBg})` }"
    >
      <VContainer>
        <div class="d-flex" style="justify-content: space-between; align-items: center;">
          <div class="text-body-1 text-white-variant text-wrap me-4">
            Хакатон МФТИ
            &copy;
            {{ new Date().getFullYear() }}
          </div>

          <a
            target="_blank"
            href="https://github.com"
            rel="noopener noreferrer"
            :class="$vuetify.theme.current.dark ? 'text-body-1' : 'text-white-variant'"
          >
            <VIcon
              icon="ri-github-line"
              size="24"
              color="white"
            />
            GitHub проекта
          </a>

          <a
            target="_blank"
            href="https://github.com"
            rel="noopener noreferrer"
            :class="$vuetify.theme.current.dark ? 'text-body-1' : 'text-white-variant'"
          >
            <VIcon
              icon="ri-telegram-line"
              size="24"
              color="white"
            />
            Связь с капитаном
          </a>

          <div class="d-flex align-center gap-3">
            <label class="text-primary font-weight-bold">
              Команда #13
            </label>
            <VAvatar size="64" class="">
              <VImg :src="footerLogo" :size="10" />
            </VAvatar>
          </div>
        </div>
      </VContainer>
    </div>
  </div>
</template>

<style lang="scss" scoped>

.footer-top {
  border-radius: 30px 30px 0 0;
  background-size: cover;
  color: #fff;
}
</style>

<style lang="scss">

.footer {
  border-radius: 50%;

  @media (min-width: 600px) and (max-width: 960px) {
    .v-container {
      padding-inline: 2rem !important;
    }

    .footer-logo-buttons {
      gap: 0.75rem;
    }
  }
}
</style>
