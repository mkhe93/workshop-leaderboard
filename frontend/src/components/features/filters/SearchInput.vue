<template>
  <BaseInput
    :model-value="modelValue"
    :placeholder="placeholder"
    type="text"
    class="search-input"
    autocomplete="off"
    @update:model-value="handleUpdate"
  />
</template>

<script setup>
import BaseInput from '../../ui/BaseInput.vue'

defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Search...'
  }
})

const emit = defineEmits(['update:modelValue'])

const handleUpdate = (value) => {
  emit('update:modelValue', value)
}
</script>

<style scoped>
.search-input {
  font-size: var(--font-size-xs);
  width: 200px;
}

@media (max-width: 600px) {
  .search-input {
    width: 100%;
  }
}
</style>
