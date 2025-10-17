import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

export default {
  // Get diary entries
  async getDiaries(params = {}) {
    const response = await api.get('/diaries', { params })
    return response.data
  },

  // Get statistics
  async getStats() {
    const response = await api.get('/stats')
    return response.data
  },

  // Get available dates
  async getDates() {
    const response = await api.get('/dates')
    return response.data
  },

  // Search entries
  async search(query, limit = 50) {
    const response = await api.get('/search', { params: { q: query, limit } })
    return response.data
  },

  // Get random entries
  async getRandom(count = 5) {
    const response = await api.get('/random', { params: { count } })
    return response.data
  },
}

