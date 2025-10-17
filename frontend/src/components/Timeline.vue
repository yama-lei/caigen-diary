<template>
  <div class="space-y-6">
    <!-- Group entries by date -->
    <div v-for="(group, date) in groupedEntries" :key="date" class="relative">
      <!-- Date Header -->
      <div class="sticky top-20 z-10 bg-nju-purple/90 backdrop-blur text-white px-6 py-3 rounded-lg shadow-lg mb-4">
        <h3 class="text-xl font-bold font-serif">{{ formatDateHeader(date) }}</h3>
        <p class="text-sm text-nju-light font-sans">共 {{ group.length }} 条记录</p>
      </div>

      <!-- Timeline Entries -->
      <div class="space-y-4 pl-4 border-l-4 border-nju-light/30">
        <div v-for="entry in group" :key="entry.id" class="relative">
          <!-- Timeline dot -->
          <div class="absolute -left-[1.6rem] top-6 w-4 h-4 bg-nju-purple rounded-full border-4 border-library-paper"></div>
          
          <DiaryCard :entry="entry" />
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="Object.keys(groupedEntries).length === 0" class="text-center py-12">
      <p class="text-gray-500 font-sans">暂无日记记录</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import DiaryCard from './DiaryCard.vue'

const props = defineProps({
  entries: {
    type: Array,
    default: () => []
  }
})

const groupedEntries = computed(() => {
  const groups = {}
  props.entries.forEach(entry => {
    if (!groups[entry.date]) {
      groups[entry.date] = []
    }
    groups[entry.date].push(entry)
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
</script>

