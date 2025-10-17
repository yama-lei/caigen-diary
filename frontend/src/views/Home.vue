<template>
  <div>
    <!-- Loading State -->
    <div v-if="loading && entries.length === 0" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-nju-purple"></div>
      <p class="mt-4 text-gray-600 font-sans">加载中...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card bg-red-50 border-red-200 text-center">
      <p class="text-red-600 font-sans">{{ error }}</p>
      <button @click="loadInitialEntries" class="btn-primary mt-4">重试</button>
    </div>

    <!-- Diary Entries -->
    <div v-else>
      <div class="mb-4 flex justify-between items-center">
        <div class="text-gray-600 font-sans">
          共 <span class="font-bold text-nju-purple">{{ totalCount }}</span> 条记录
        </div>
        <div class="flex items-center gap-2">
          <input 
            type="checkbox" 
            id="showSentiment"
            v-model="showSentimentInfo"
            class="rounded text-nju-purple focus:ring-nju-purple"
          >
          <label for="showSentiment" class="text-sm text-gray-600 font-sans">显示情感分析</label>
        </div>
      </div>

      <!-- Entries grouped by date -->
      <div class="space-y-6">
        <div v-for="(group, date) in groupedEntries" :key="date" class="card">
          <!-- Date Header -->
          <div class="bg-nju-purple text-white px-4 py-2 rounded-t-lg -mx-6 -mt-6 mb-4">
            <h3 class="text-lg font-bold font-serif">{{ formatDateHeader(date) }}</h3>
            <p class="text-sm text-nju-light font-sans">{{ group.length }} 条记录</p>
          </div>

          <!-- Entries List -->
          <div class="space-y-3">
            <div 
              v-for="(entry, idx) in group" 
              :key="entry.id"
              class="py-3 border-b border-gray-200 last:border-0"
            >
              <p class="text-library-ink leading-relaxed text-base">
                {{ entry.content }}
              </p>
              <!-- Sentiment Info -->
              <div v-if="showSentimentInfo && entry.positive_prob !== null" class="mt-2 text-xs font-sans text-gray-500">
                😊 {{ (entry.positive_prob * 100).toFixed(1) }}% 
                <span class="mx-1">·</span>
                😔 {{ (entry.negative_prob * 100).toFixed(1) }}%
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="hasMore" class="text-center mt-8">
        <button 
          @click="loadMore" 
          :disabled="loading"
          class="btn-primary px-8 py-3"
        >
          <span v-if="loading">加载中...</span>
          <span v-else>加载更多</span>
        </button>
      </div>

      <!-- No More Data -->
      <div v-else-if="entries.length > 0" class="text-center mt-8 text-gray-500 font-sans">
        已加载全部内容
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const entries = ref([])
const loading = ref(false)
const error = ref(null)
const hasMore = ref(true)
const currentOffset = ref(0)
const pageSize = 100
const totalCount = ref(0)
const showSentimentInfo = ref(false)

// Group entries by date
const groupedEntries = computed(() => {
  const groups = {}
  entries.value.forEach(entry => {
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

const loadInitialEntries = async () => {
  loading.value = true
  error.value = null
  currentOffset.value = 0
  entries.value = []

  try {
    // Get statistics first to get total count
    const stats = await api.getStats()
    totalCount.value = stats.total

    // Load first batch
    const data = await api.getDiaries({ limit: pageSize, offset: 0 })
    entries.value = data
    currentOffset.value = pageSize
    hasMore.value = data.length === pageSize
  } catch (err) {
    error.value = '加载数据失败，请稍后重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  if (loading.value || !hasMore.value) return

  loading.value = true
  error.value = null

  try {
    const data = await api.getDiaries({ limit: pageSize, offset: currentOffset.value })
    
    if (data.length === 0) {
      hasMore.value = false
    } else {
      entries.value.push(...data)
      currentOffset.value += data.length
      hasMore.value = data.length === pageSize
    }
  } catch (err) {
    error.value = '加载数据失败，请稍后重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadInitialEntries()
})
</script>
