<template>
  <div class="dans-search">
    <div>
      <small>{{ label }}</small>
    </div>
    <div>
      <input
        type="search"
        :list="uuid"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
      >
    </div>
    <datalist :id="uuid">
      <option v-for="option in options" :key="option" :value="option" />
    </datalist>
  </div>
</template>

<script>

export default {
  props: {
    modelValue: {},
    label: String,
    options: Array,
  },
  emits: ['update:modelValue'],
  data() {
    return {
      uuid: self.crypto.randomUUID(),
    };
  },
}

</script>
