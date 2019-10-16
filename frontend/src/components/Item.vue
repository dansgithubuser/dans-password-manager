<style>
.value input {
  color: rgba(0, 0, 0, 0) !important;
}
.value ::selection {
  color: rgba(0, 0, 0, 0) !important;
}
.notes textarea {
  color: rgba(0, 0, 0, 0) !important;
}
</style>

<template><div>
  <v-row>
    <v-col>
      <v-text-field v-model='item.name' label='name'/>
      <v-text-field v-model='item.target' label='target'/>
    </v-col>
    <v-col>
      <v-text-field v-model='item.user' label='user'/>
      <v-text-field v-model='item.value' label='value' class='value'/>
    </v-col>
    <v-col>
      <v-textarea v-model='item.notes' label='notes' class='notes' :no-resize=true :solo=true />
    </v-col>
    <v-col>
      <v-btn v-if='!create' @click='itemUpdate(item, teamId)'>update item</v-btn>
      <v-btn v-if='create' @click='itemCreate(teamId)'>create item</v-btn>
    </v-col>
  </v-row>
</div></template>

<script>
import api from '../api.js'

export default {
  props: {
    item: Object,
    teamId: Number,
    create: { type: Boolean, default: false },
    updateItems: Function,
  },
  methods: {
    itemCreate(teamId) {
      api.itemCreate(
        this.item.name,
        this.item.target,
        this.item.user,
        this.item.value,
        this.item.notes,
        teamId,
      ).then(() => this.updateItems(teamId));
      this.item.name = '';
      this.item.target = '';
      this.item.user = '';
      this.item.value = '';
      this.item.notes = '';
    },
    itemUpdate(item, teamId) {
      api.itemUpdate(
        item.id,
        item.name,
        item.target,
        item.user,
        item.value,
        item.notes,
        teamId,
      ).then(() => this.updateItems(teamId));
    },
  },
}
</script>
