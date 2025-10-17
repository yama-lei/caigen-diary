<template>
  <div class="card">
    <label class="block text-sm font-medium text-gray-700 mb-2 font-sans">
      选择日期
    </label>
    <input
      type="date"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nju-purple focus:border-transparent font-sans"
    />
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

defineEmits(['update:modelValue'])
</script>

