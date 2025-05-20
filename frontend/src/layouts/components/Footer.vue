<template>
  <div class="h-100 d-flex align-center justify-md-space-between justify-center">
    <!-- 👉 Footer: left content -->
    <span class="d-flex align-center">
      &copy;
      {{ new Date().getFullYear() }}
      Golden Mean
      для <a
        href="https://mipt.ru/"
        target="_blank"
        rel="noopener noreferrer"
        class="text-primary ms-1"
      >МФТИ</a>
    </span>
    <!-- 👉 Footer: right content -->
    <span class="d-md-flex gap-x-4 text-primary d-none">
      
      <a
        href="https://gitlab.com/mfti6844113/hackaton_2"
        target="noopener noreferrer"
      >Репозиторий проекта</a>
      <span class="text-disabled">Логин и пароль можно получить у команды</span>
    </span>
  </div>
</template>
