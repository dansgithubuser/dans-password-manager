<template>
  <div :class="class" :style="style">
    <div>
      <small>{{ label }}</small>
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
    class: { default: 'dans-input' },
    style: { default: '' },
  },
  emits: ['update:modelValue'],
  inheritAttrs: false,
}

</script>
