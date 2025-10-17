<template>
  <div>
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-nju-purple"></div>
      <p class="mt-4 text-gray-600 font-sans">加载中...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card bg-red-50 border-red-200 text-center">
      <p class="text-red-600 font-sans">{{ error }}</p>
      <button @click="loadStats" class="btn-primary mt-4">重试</button>
    </div>

    <!-- Statistics -->
    <div v-else class="space-y-6">

      <!-- Date Range -->
      <div class="card">
        <h3 class="section-title">时间范围</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div class="text-sm text-gray-600 font-sans">最早有记录的日记是：</div>
            <div class="text-xl font-bold text-nju-purple font-serif">{{ formatDate(stats.date_range.first_date) }}</div>
          </div>
          <div>
            <div class="text-sm text-gray-600 font-sans">最新的日记是：</div>
            <div class="text-xl font-bold text-nju-purple font-serif">{{ formatDate(stats.date_range.last_date) }}</div>
          </div>
        </div>
      </div>

      <!-- Sentiment Distribution -->
      <div class="card">
        <h3 class="section-title">情感分布</h3>
        <div class="space-y-4">
          <div v-for="(count, sentiment) in stats.sentiment_distribution" :key="sentiment">
            <div class="flex justify-between items-center mb-2">
              <span class="font-sans">{{ getSentimentEmoji(sentiment) }} {{ sentiment }}</span>
              <span class="text-gray-600 font-sans">{{ displayedCounts[sentiment] }} ({{ getPercentage(displayedCounts[sentiment], stats.total) }}%)</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-3">
              <div 
                :class="getSentimentBarColor(sentiment)"
                class="h-3 rounded-full transition-all duration-500"
                :style="{ width: getPercentage(displayedCounts[sentiment], stats.total) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Monthly Counts -->
      <div class="card">
        <h3 class="section-title">月度统计</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <div 
            v-for="(count, month) in stats.monthly_counts" 
            :key="month"
            class="bg-library-paper border-2 border-nju-light/30 rounded-lg p-4 text-center hover:shadow-lg transition-shadow"
          >
            <div class="text-sm text-gray-600 font-sans">{{ month }}</div>
            <div class="text-2xl font-bold text-nju-purple font-serif">{{ displayedMonthly[month] || 0 }}</div>
          </div>
        </div>
      </div>

      <!-- Overall Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="card text-center bg-gradient-to-br from-nju-purple to-nju-dark text-white">
          <div class="text-4xl font-bold font-serif">{{ displayedTotal }}</div>
          <div class="text-sm text-nju-light mt-2 font-sans">总记录数</div>
        </div>
        <div class="card text-center bg-gradient-to-br from-green-500 to-green-600 text-white">
          <div class="text-4xl font-bold font-serif">{{ displayedCounts['正面'] || 0 }}</div>
          <div class="text-sm text-green-100 mt-2 font-sans">😊 正面情感</div>
        </div>
        <div class="card text-center bg-gradient-to-br from-red-500 to-red-600 text-white">
          <div class="text-4xl font-bold font-serif">{{ displayedCounts['负面'] || 0 }}</div>
          <div class="text-sm text-red-100 mt-2 font-sans">😔 负面情感</div>
        </div>

      </div>
      
      <div class="div text-center text-gray-600 font-sans">
          注：情绪分析使用的是阿里云的情绪分析模型。
      </div>
    
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const stats = ref({
  total: 0,
  sentiment_distribution: {},
  date_range: { first_date: '', last_date: '' },
  monthly_counts: {}
})
const loading = ref(false)
const error = ref(null)

// For animation
const displayedTotal = ref(0)
const displayedCounts = ref({})
const displayedMonthly = ref({})

const animateNumber = (start, end, callback, duration = 3000) => {
  const startTime = Date.now()
  const updateNumber = () => {
    const currentTime = Date.now()
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    
    // Easing function for smooth animation
    const easeOutQuad = progress => 1 - (1 - progress) * (1 - progress)
    const currentValue = Math.round(start + (end - start) * easeOutQuad(progress))
    
    callback(currentValue)
    
    if (progress < 1) {
      requestAnimationFrame(updateNumber)
    }
  }
  updateNumber()
}

const startAnimations = () => {
  // Animate total count
  animateNumber(0, stats.value.total, (value) => {
    displayedTotal.value = value
  })

  // Animate sentiment distribution
  Object.entries(stats.value.sentiment_distribution).forEach(([sentiment, count]) => {
    animateNumber(0, count, (value) => {
      displayedCounts.value[sentiment] = value
    })
  })

  // Animate monthly counts
  Object.entries(stats.value.monthly_counts).forEach(([month, count]) => {
    animateNumber(0, count, (value) => {
      displayedMonthly.value[month] = value
    })
  })
}

const loadStats = async () => {
  loading.value = true
  error.value = null

  try {
    const data = await api.getStats()
    stats.value = data
    // Start animations after data is loaded
    startAnimations()
  } catch (err) {
    error.value = '加载统计数据失败，请稍后重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
}

const getPercentage = (count, total) => {
  if (total === 0) return 0
  return ((count / total) * 100).toFixed(1)
}

const getSentimentEmoji = (sentiment) => {
  switch (sentiment) {
    case '正面': return '😊'
    case '负面': return '😔'
    case '中性': return '😐'
    default: return ''
  }
}

const getSentimentBarColor = (sentiment) => {
  switch (sentiment) {
    case '正面': return 'bg-green-500'
    case '负面': return 'bg-red-500'
    case '中性': return 'bg-gray-500'
    default: return 'bg-gray-300'
  }
}

const viewPositive = () => {
  router.push('/?sentiment=正面')
}

onMounted(() => {
  loadStats()
})
</script>
