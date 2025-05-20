import { createApp } from 'vue'

import App from '@/App.vue'
import { registerPlugins } from '@core/utils/plugins'
import 'echarts'
import ECharts from 'vue-echarts'

// Styles
import '@core/scss/template/index.scss'
import '@layouts/styles/index.scss'

// Create vue app
const app = createApp(App)

// Register plugins
registerPlugins(app)

app.component('v-chart', ECharts)

// Mount vue app
app.mount('#app')
