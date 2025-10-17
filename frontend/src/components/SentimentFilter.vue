<template>
  <div class="flex flex-wrap gap-2">
    <button
      @click="$emit('update:sentiment', null)"
      :class="['px-4 py-2 rounded-lg font-sans transition-all', 
               sentiment === null ? 'bg-nju-purple text-white' : 'bg-white text-gray-700 hover:bg-gray-100']"
    >
      全部
    </button>
    <button
      @click="$emit('update:sentiment', '正面')"
      :class="['px-4 py-2 rounded-lg font-sans transition-all', 
               sentiment === '正面' ? 'bg-green-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-100']"
    >
      😊 正面
    </button>
    <button
      @click="$emit('update:sentiment', '中性')"
      :class="['px-4 py-2 rounded-lg font-sans transition-all', 
               sentiment === '中性' ? 'bg-gray-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-100']"
    >
      😐 中性
    </button>
    <button
      @click="$emit('update:sentiment', '负面')"
      :class="['px-4 py-2 rounded-lg font-sans transition-all', 
               sentiment === '负面' ? 'bg-red-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-100']"
    >
      😔 负面
    </button>
  </div>
</template>

<script setup>
defineProps({
  sentiment: {
    type: String,
    default: null
  }
})

defineEmits(['update:sentiment'])
</script>

