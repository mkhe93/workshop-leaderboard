<template>
  <BaseBarChart
    :chartData="chartData"
    :loading="loading"
    :error="error"
    title="Token Usage by Model"
    xAxisTitle="Model"
    @retry="emit('retry')"
  />
</template>

<script setup>
import BaseBarChart from '../../ui/BaseBarChart.vue'

defineProps({
  chartData: {
    type: Object,
    required: true,
    default: () => ({ labels: [], datasets: [] })
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['retry'])
</script>
