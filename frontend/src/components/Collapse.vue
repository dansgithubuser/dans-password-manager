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
  border-bottom: 1px solid;
  cursor: pointer;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.dans-collapse-body {
  border-left: 1px solid;
  border-right: 1px solid;
  border-bottom: 1px solid;
}

</style>
