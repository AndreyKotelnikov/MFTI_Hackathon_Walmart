export const routes = [
  { path: '/' },
  {
    path: '/',
    component: () => import('@/layouts/home.vue'),
    children: [
      {
        path: '',
        component: () => import('@/pages/dashboard.vue'),
      },
    ],
  },
  {
    path: '/',
    component: () => import('@/layouts/default.vue'),
    children: [
    ],
  },
  {
    path: '/',
    component: () => import('@/layouts/blank.vue'),
    children: [
      {
        path: '/:pathMatch(.*)*',
        component: () => import('@/pages/[...error].vue'),
      },
    ],
  },
]
