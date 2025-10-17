<template>
  <div class="diary-card relative">
    <!-- Date Badge -->
    <div class="absolute -top-3 -left-3 bg-nju-purple text-white px-3 py-1 rounded-full text-sm font-sans shadow-md">
      {{ formatDate(entry.date) }}
    </div>
    <!-- Content -->
    <div class="mt-4">
      <p class="text-library-ink leading-relaxed text-base">
        {{ entry.content }}
        <span>😊 {{ (entry.positive_prob * 100).toFixed(1) }}%</span>
        <span>😔 {{ (entry.negative_prob * 100).toFixed(1) }}%</span>
      </p>
    </div>


    
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  entry: {
    type: Object,
    required: true
  }
})

const sentimentClass = computed(() => {
  switch (props.entry.sentiment) {
    case '正面':
      return 'sentiment-positive'
    case '负面':
      return 'sentiment-negative'
    case '中性':
      return 'sentiment-neutral'
    default:
      return ''
  }
})

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}月${day}日`
}
</script>

