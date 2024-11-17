import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Create stores
import { useSolarStore } from './stores/solar'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize store
const solarStore = useSolarStore(pinia)
solarStore.fetchSolarData() // Pre-fetch data

app.mount('#app')