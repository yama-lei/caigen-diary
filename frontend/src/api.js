import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8005/api',
  timeout: 10000,
})

// Create admin API instance with Basic Auth
const createAdminApi = (username, password) => {
  return axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8005/api',
    timeout: 10000,
    auth: {
      username,
      password
    }
  })
}

export default {
  // ==================== 公共接口 ====================
  
  // Get diary entries
  async getDiaries(params = {}) {
    const response = await api.get('/entries', { params })
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

  // ==================== 管理接口 ====================
  
  // Admin login (verify credentials)
  async adminLogin(username, password) {
    try {
      const adminApi = createAdminApi(username, password)
      const response = await adminApi.get('/admin/stats')
      return { success: true, data: response.data }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || '登录失败' }
    }
  },

  // Admin get entries
  async adminGetEntries(username, password, params = {}) {
    const adminApi = createAdminApi(username, password)
    const response = await adminApi.get('/admin/entries', { params })
    return response.data
  },

  // Admin get single entry
  async adminGetEntry(username, password, entryId) {
    const adminApi = createAdminApi(username, password)
    const response = await adminApi.get(`/admin/entries/${entryId}`)
    return response.data
  },

  // Admin update entry
  async adminUpdateEntry(username, password, entryId, data) {
    const adminApi = createAdminApi(username, password)
    const response = await adminApi.put(`/admin/entries/${entryId}`, data)
    return response.data
  },

  // Admin delete entry
  async adminDeleteEntry(username, password, entryId) {
    const adminApi = createAdminApi(username, password)
    const response = await adminApi.delete(`/admin/entries/${entryId}`)
    return response.data
  },

  // Admin get stats
  async adminGetStats(username, password) {
    const adminApi = createAdminApi(username, password)
    const response = await adminApi.get('/admin/stats')
    return response.data
  },

  // Batch create entries (with API key)
  async batchCreateEntries(apiKey, entries) {
    const response = await axios.post(
      `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8005/api'}/admin/entries`,
      { entries },
      {
        headers: {
          'X-Api-Key': apiKey
        }
      }
    )
    return response.data
  }
}

