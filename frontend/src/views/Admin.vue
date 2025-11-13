<template>
  <div class="max-w-7xl mx-auto">
    <!-- Login Screen -->
    <div v-if="!isLoggedIn" class="max-w-md mx-auto mt-20">
      <div class="card">
        <h2 class="text-2xl font-bold text-center mb-6 font-serif text-nju-purple">管理员登录</h2>
        
        <form @submit.prevent="login">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2 font-sans">用户名</label>
            <input 
              v-model="loginForm.username" 
              type="text" 
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nju-purple focus:border-transparent"
            >
          </div>
          
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2 font-sans">密码</label>
            <input 
              v-model="loginForm.password" 
              type="password" 
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nju-purple focus:border-transparent"
            >
          </div>
          
          <div v-if="loginError" class="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm font-sans">
            {{ loginError }}
          </div>
          
          <button 
            type="submit" 
            :disabled="loggingIn"
            class="w-full btn-primary py-3"
          >
            {{ loggingIn ? '登录中...' : '登录' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Admin Dashboard -->
    <div v-else>
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold font-serif text-nju-purple">管理后台</h1>
        <button @click="logout" class="px-4 py-2 text-sm bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors font-sans">
          退出登录
        </button>
      </div>

      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="card bg-gradient-to-br from-nju-purple to-nju-dark text-white">
          <div class="text-sm text-nju-light font-sans">总记录数</div>
          <div class="text-3xl font-bold font-serif mt-2">{{ stats.total }}</div>
        </div>
        <div class="card bg-gradient-to-br from-green-500 to-green-600 text-white">
          <div class="text-sm text-green-100 font-sans">最早记录</div>
          <div class="text-xl font-bold font-serif mt-2">{{ formatDate(stats.date_range?.first_date) }}</div>
        </div>
        <div class="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <div class="text-sm text-blue-100 font-sans">最新记录</div>
          <div class="text-xl font-bold font-serif mt-2">{{ formatDate(stats.date_range?.last_date) }}</div>
        </div>
      </div>

      <!-- Search and Filters -->
      <div class="card mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input 
            v-model="filters.query" 
            type="text" 
            placeholder="搜索内容..."
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nju-purple"
            @keyup.enter="loadEntries"
          >
          <input 
            v-model="filters.date_from" 
            type="date" 
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nju-purple"
          >
          <input 
            v-model="filters.date_to" 
            type="date" 
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nju-purple"
          >
          <button 
            @click="loadEntries" 
            class="btn-primary"
          >
            搜索
          </button>
        </div>
      </div>

      <!-- Actions -->
      <div class="mb-4 flex justify-between items-center">
        <div class="text-gray-600 font-sans">
          共 {{ entries.length }} 条记录
        </div>
        <div class="flex gap-2">
          <button 
            @click="showAddDialog = true"
            class="btn-primary"
          >
            + 添加日记
          </button>
          <button 
            @click="loadEntries"
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors font-sans"
          >
            刷新
          </button>
        </div>
      </div>

      <!-- Entries Table -->
      <div class="card overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b-2 border-gray-200">
              <th class="text-left py-3 px-4 font-sans font-semibold text-gray-700">ID</th>
              <th class="text-left py-3 px-4 font-sans font-semibold text-gray-700">日期</th>
              <th class="text-left py-3 px-4 font-sans font-semibold text-gray-700">内容</th>
              <th class="text-left py-3 px-4 font-sans font-semibold text-gray-700">创建时间</th>
              <th class="text-right py-3 px-4 font-sans font-semibold text-gray-700">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="entry in entries" 
              :key="entry.id"
              class="border-b border-gray-100 hover:bg-gray-50 transition-colors"
            >
              <td class="py-3 px-4 font-sans">{{ entry.id }}</td>
              <td class="py-3 px-4 font-sans">{{ entry.date }}</td>
              <td class="py-3 px-4 max-w-md truncate">{{ entry.content }}</td>
              <td class="py-3 px-4 font-sans text-sm text-gray-500">{{ formatDateTime(entry.created_at) }}</td>
              <td class="py-3 px-4 text-right">
                <button 
                  @click="editEntry(entry)"
                  class="text-blue-600 hover:text-blue-800 mr-3 font-sans text-sm"
                >
                  编辑
                </button>
                <button 
                  @click="deleteEntry(entry)"
                  class="text-red-600 hover:text-red-800 font-sans text-sm"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="entries.length === 0" class="text-center py-12 text-gray-500 font-sans">
          暂无数据
        </div>
      </div>

      <!-- Pagination -->
      <div class="flex justify-center gap-2 mt-6">
        <button 
          @click="prevPage"
          :disabled="currentPage === 1"
          class="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors font-sans disabled:opacity-50 disabled:cursor-not-allowed"
        >
          上一页
        </button>
        <span class="px-4 py-2 font-sans">第 {{ currentPage }} 页</span>
        <button 
          @click="nextPage"
          :disabled="entries.length < pageSize"
          class="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors font-sans disabled:opacity-50 disabled:cursor-not-allowed"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <div v-if="showAddDialog || editingEntry" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full">
        <h3 class="text-xl font-bold mb-4 font-serif text-nju-purple">
          {{ editingEntry ? '编辑日记' : '添加日记' }}
        </h3>
        
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2 font-sans">日期</label>
          <input 
            v-model="formData.date" 
            type="date" 
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nju-purple"
          >
        </div>
        
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2 font-sans">内容</label>
          <textarea 
            v-model="formData.content" 
            required
            rows="6"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nju-purple"
          ></textarea>
        </div>
        
        <div v-if="formError" class="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm font-sans">
          {{ formError }}
        </div>
        
        <div class="flex justify-end gap-2">
          <button 
            @click="closeDialog"
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors font-sans"
          >
            取消
          </button>
          <button 
            @click="saveEntry"
            :disabled="saving"
            class="btn-primary"
          >
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <div v-if="deletingEntry" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-xl font-bold mb-4 font-serif text-red-600">确认删除</h3>
        <p class="mb-4 font-sans text-gray-700">确定要删除这条日记吗？此操作不可恢复。</p>
        <p class="mb-6 p-3 bg-gray-50 rounded text-sm font-sans">{{ deletingEntry.content }}</p>
        
        <div class="flex justify-end gap-2">
          <button 
            @click="deletingEntry = null"
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors font-sans"
          >
            取消
          </button>
          <button 
            @click="confirmDelete"
            :disabled="deleting"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors font-sans"
          >
            {{ deleting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

// 本地存储相关常量
const LOCALSTORAGE_KEY = 'nju_diary_admin_creds'

// Auth
const isLoggedIn = ref(false)
const loginForm = ref({ username: '', password: '' })
const credentials = ref({ username: '', password: '' })
const loggingIn = ref(false)
const loginError = ref(null)

// Data
const stats = ref({ total: 0, date_range: {}, monthly_counts: {}, recent_activity: [] })
const entries = ref([])
const filters = ref({ query: '', date_from: '', date_to: '' })
const currentPage = ref(1)
const pageSize = 50

// Dialogs
const showAddDialog = ref(false)
const editingEntry = ref(null)
const deletingEntry = ref(null)
const formData = ref({ date: '', content: '' })
const formError = ref(null)
const saving = ref(false)
const deleting = ref(false)

// 持久化：从本地存储加载
function loadPersistedLogin() {
  try {
    const stored = window.localStorage.getItem(LOCALSTORAGE_KEY)
    if (stored) {
      const creds = JSON.parse(stored)
      if (creds.username && creds.password) {
        credentials.value = { ...creds }
        loginForm.value = { ...creds }
        isLoggedIn.value = true
        // 自动尝试加载数据
        loadStats()
        loadEntries()
        return true
      }
    }
  } catch (e) {
    // noop
  }
  return false
}

// 持久化：保存当前凭据
function persistLogin(creds) {
  window.localStorage.setItem(LOCALSTORAGE_KEY, JSON.stringify(creds))
}

// 持久化：清除
function clearPersistedLogin() {
  window.localStorage.removeItem(LOCALSTORAGE_KEY)
}

// Auth functions
const login = async () => {
  loggingIn.value = true
  loginError.value = null

  try {
    const result = await api.adminLogin(loginForm.value.username, loginForm.value.password)
    if (result.success) {
      credentials.value = { ...loginForm.value }
      isLoggedIn.value = true
      persistLogin(credentials.value)
      loadStats()
      loadEntries()
    } else {
      loginError.value = result.error
    }
  } catch (error) {
    loginError.value = '登录失败，请检查用户名和密码'
  } finally {
    loggingIn.value = false
  }
}

const logout = () => {
  isLoggedIn.value = false
  credentials.value = { username: '', password: '' }
  loginForm.value = { username: '', password: '' }
  entries.value = []
  stats.value = { total: 0, date_range: {}, monthly_counts: {} }
  clearPersistedLogin()
}

// Data functions
const loadStats = async () => {
  try {
    const data = await api.adminGetStats(credentials.value.username, credentials.value.password)
    stats.value = data
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const loadEntries = async () => {
  try {
    const params = {
      ...filters.value,
      limit: pageSize,
      offset: (currentPage.value - 1) * pageSize
    }
    const data = await api.adminGetEntries(credentials.value.username, credentials.value.password, params)
    entries.value = data
  } catch (error) {
    console.error('加载日记失败:', error)
    if (error.response?.status === 401) {
      logout()
    }
  }
}

// Pagination
const nextPage = () => {
  currentPage.value++
  loadEntries()
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadEntries()
  }
}

// CRUD operations
const editEntry = (entry) => {
  editingEntry.value = entry
  formData.value = {
    date: entry.date,
    content: entry.content
  }
  formError.value = null
}

const deleteEntry = (entry) => {
  deletingEntry.value = entry
}

const confirmDelete = async () => {
  deleting.value = true
  try {
    await api.adminDeleteEntry(
      credentials.value.username, 
      credentials.value.password, 
      deletingEntry.value.id
    )
    deletingEntry.value = null
    loadEntries()
    loadStats()
  } catch (error) {
    alert('删除失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    deleting.value = false
  }
}

const saveEntry = async () => {
  if (!formData.value.date || !formData.value.content) {
    formError.value = '请填写所有字段'
    return
  }

  saving.value = true
  formError.value = null

  try {
    if (editingEntry.value) {
      // Update
      await api.adminUpdateEntry(
        credentials.value.username,
        credentials.value.password,
        editingEntry.value.id,
        formData.value
      )
    } else {
      // Create - use batch API
      await api.batchCreateEntries(
        'your_api_key', // TODO: Get from config
        [formData.value]
      )
    }
    closeDialog()
    loadEntries()
    loadStats()
  } catch (error) {
    formError.value = error.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

const closeDialog = () => {
  showAddDialog.value = false
  editingEntry.value = null
  formData.value = { date: '', content: '' }
  formError.value = null
}

// Utilities
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

// Set today as default date for new entries
onMounted(() => {
  const today = new Date().toISOString().split('T')[0]
  formData.value.date = today
  // 自动登录持久化
  if (!isLoggedIn.value) {
    loadPersistedLogin()
  }
})
</script>
