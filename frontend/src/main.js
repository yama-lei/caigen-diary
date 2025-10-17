import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'
import App from './App.vue'
import Home from './views/Home.vue'
import Search from './views/Search.vue'
import Stats from './views/Stats.vue'
import About from './views/About.vue'

const routes = [
  { path: '/', component: Home, name: 'home' },
  { path: '/search', component: Search, name: 'search' },
  { path: '/stats', component: Stats, name: 'stats' },
  { path: '/about', component: About, name: 'about' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp(App)
app.use(router)
app.mount('#app')

