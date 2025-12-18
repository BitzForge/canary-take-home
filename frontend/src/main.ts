import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router'
import vue3GoogleLogin from 'vue3-google-login'
import axios from 'axios'

import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'

// Configure axios to send cookies with every request
axios.defaults.withCredentials = true

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginView },
    { path: '/dashboard', component: DashboardView },
  ],
})

const app = createApp(App)

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

app.use(vue3GoogleLogin, {
  clientId: googleClientId,
})

app.use(router)
app.mount('#app')
