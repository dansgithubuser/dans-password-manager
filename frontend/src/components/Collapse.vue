<template>
  <div class="dans-collapse">
    <div class="dans-collapse-header" @click="collapsed = !collapsed">
      <div>{{ label }}</div>
      <div v-if="collapsed">➕</div>
      <div v-else>➖</div>
    </div>
    <div v-if="!collapsed" class="dans-collapse-body">
      <slot></slot>
    </div>
  </div>
</template>

<script>

export default {
  props: {
    label: String,
  },
  data() {
    return {
      collapsed: true,
    };
  },
}

</script>

<style scoped>

.dans-collapse-header {
  border-bottom: 1px solid grey;
  cursor: pointer;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.dans-collapse-body {
  border-left: 1px solid grey;
  border-right: 1px solid grey;
  border-bottom: 1px solid grey;
  padding: 1rem;
  box-shadow: 0px 0px 0.25rem grey inset;
}

</style>
