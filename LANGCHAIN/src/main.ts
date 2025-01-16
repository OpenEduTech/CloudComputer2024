import './assets/main.css'

import { createApp } from 'vue'
import { store } from './store/store'
import App from './App.vue'
import router from './router'
import './assets/css/tailwind.css'
import 'vfonts/Lato.css'
import 'vfonts/FiraCode.css'

const app = createApp(App)


app.use(router)
app.use(store)

app.mount('#app')
