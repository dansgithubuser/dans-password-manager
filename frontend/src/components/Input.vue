<template>
  <div class="dans-input">
    <div>
      <small class="dans-label">{{ label }}</small>
    </div>
    <div>
      <input
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        v-bind="$attrs"
      >
    </div>
  </div>
</template>

<script>

export default {
  props: {
    modelValue: {},
    label: String,
  },
  emits: ['update:modelValue'],
  inheritAttrs: false,
}

</script>
