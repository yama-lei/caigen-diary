<template>
  <div>

    <!-- Search and Filter Box -->
    <div class="card mb-6">
      <div class="space-y-6">
        <!-- Search -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2 font-sans">关键词搜索</label>
          <div class="flex gap-2">
            <input
              v-model="searchQuery"
              @keyup.enter="performSearch"
              type="text"
              placeholder="输入关键词搜索..."
              class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nju-purple focus:border-transparent font-sans"
            />
            <button @click="performSearch" class="btn-primary px-8">
              搜索
            </button>
          </div>
        </div>

        <div class="border-t pt-6">
          <h3 class="text-lg font-semibold mb-3 text-nju-purple font-serif">筛选条件</h3>
          
          <!-- Sentiment Filter -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2 font-sans">情感分类</label>
            <SentimentFilter v-model:sentiment="selectedSentiment" @update:sentiment="applyFilters" />
          </div>

          <!-- Date Filter -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2 font-sans">按日期查询</label>
              <input
                v-model="selectedDate"
                type="date"
                @change="applyFilters"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nju-purple focus:border-transparent font-sans"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2 font-sans">按月份查询</label>
              <input
                v-model="selectedMonth"
                type="month"
                @change="applyFilters"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nju-purple focus:border-transparent font-sans"
              />
            </div>
          </div>

          <!-- Clear Filters -->
          <div>
            <button @click="clearAll" class="btn-secondary w-full md:w-auto">
              清除所有条件
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-nju-purple"></div>
      <p class="mt-4 text-gray-600 font-sans">加载中...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card bg-red-50 border-red-200 text-center">
      <p class="text-red-600 font-sans">{{ error }}</p>
      <button @click="applyFilters" class="btn-primary mt-4">重试</button>
    </div>

    <!-- Results -->
    <div v-else-if="results.length > 0">
      <div class="mb-4 text-gray-600 font-sans">
        找到 <span class="font-bold text-nju-purple">{{ results.length }}</span> 条相关记录
      </div>
      
      <!-- Results grouped by date -->
      <div class="space-y-6">
        <div v-for="(group, date) in groupedResults" :key="date" class="card">
          <!-- Date Header -->
          <div class="bg-nju-purple text-white px-4 py-2 rounded-t-lg -mx-6 -mt-6 mb-4">
            <h3 class="text-lg font-bold font-serif">{{ formatDateHeader(date) }}</h3>
            <p class="text-sm text-nju-light font-sans">{{ group.length }} 条记录</p>
          </div>

          <!-- Entries List -->
          <div class="space-y-3">
            <div 
              v-for="entry in group" 
              :key="entry.id"
              class="py-3 border-b border-gray-200 last:border-0"
            >
              <p class="text-library-ink leading-relaxed text-base">
                {{ entry.content }}
              </p>
              <!-- Sentiment Info -->
              <div v-if="entry.positive_prob !== null" class="mt-2 text-xs font-sans text-gray-500">
                😊 {{ (entry.positive_prob * 100).toFixed(1) }}% 
                <span class="mx-1">·</span>
                😔 {{ (entry.negative_prob * 100).toFixed(1) }}%
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="hasSearched || hasFilters" class="card text-center py-12">
      <p class="text-gray-500 text-lg font-sans">未找到相关记录</p>
      <p class="text-gray-400 text-sm mt-2 font-sans">试试调整搜索或筛选条件</p>
    </div>

    <!-- Initial State -->
    <div v-else class="card text-center py-12">
      <p class="text-gray-500 font-sans">输入关键词搜索或使用筛选条件</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../api'
import SentimentFilter from '../components/SentimentFilter.vue'

const searchQuery = ref('')
const results = ref([])
const loading = ref(false)
const error = ref(null)
const hasSearched = ref(false)

const selectedSentiment = ref(null)
const selectedDate = ref('')
const selectedMonth = ref('')

const hasFilters = computed(() => {
  return selectedSentiment.value || selectedDate.value || selectedMonth.value
})

// Group results by date
const groupedResults = computed(() => {
  const groups = {}
  results.value.forEach(entry => {
    const date = entry.date
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(entry)
  })
  return groups
})

const formatDateHeader = (dateStr) => {
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  const weekday = weekdays[date.getDay()]
  return `${year}年${month}月${day}日 ${weekday}`
}

const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    return
  }

  loading.value = true
  error.value = null
  hasSearched.value = true

  try {
    const data = await api.search(searchQuery.value)
    results.value = data
  } catch (err) {
    error.value = '搜索失败，请稍后重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const applyFilters = async () => {
  if (!hasFilters.value) {
    return
  }

  loading.value = true
  error.value = null
  hasSearched.value = true

  try {
    const params = {}
    
    if (selectedDate.value) {
      params.date = selectedDate.value
    } else if (selectedMonth.value) {
      params.month = selectedMonth.value
    }
    
    if (selectedSentiment.value) {
      params.sentiment = selectedSentiment.value
    }

    const data = await api.getDiaries(params)
    results.value = data
  } catch (err) {
    error.value = '筛选失败，请稍后重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const clearAll = () => {
  searchQuery.value = ''
  selectedSentiment.value = null
  selectedDate.value = ''
  selectedMonth.value = ''
  results.value = []
  hasSearched.value = false
  error.value = null
}
</script>

