<style>

.value {
  color: rgba(0, 0, 0, 0) !important;
}
.value::selection {
  color: rgba(0, 0, 0, 0) !important;
}

.notes {
  color: rgba(0, 0, 0, 0) !important;
  resize: none;
}

.hidden {
  visibility: hidden;
}

</style>

<template>
  <div class='row spaced-h'>
    <div class='col'>
      <Input v-model='item.name' label='name'/>
      <Input v-model='item.target' label='target'/>
    </div>
    <div class='col'>
      <Input v-model='item.user' label='user'/>
      <Input v-model='item.value' label='value' class='value'/>
    </div>
    <div class='col'>
      <small class='dans-label'>notes</small>
      <textarea v-model='item.notes' class='notes' style='height: 100%'/>
    </div>
    <div class='col'>
      <template v-if='!create'>
        <small class='hidden'>x</small>
        <button @click='itemUpdate(item, teamId)'>update item</button>
      </template>
      <template v-else>
        <small class='hidden'>x</small>
        <div class="col" style="flex-grow: 1; justify-content: space-between">
          <button @click='itemCreate(teamId)'>create item</button>
          <button @click='random()'>random</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script>

import Input from './Input.vue'

import api from '../api.js'

export default {
  name: 'Item',
  components: {
    Input,
  },
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
    random() {
      const pool = [
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'abcdefghijklmnopqrstuvwxyz',
        '0123456789',
      ].join('');
      this.$emit('value',
        window.crypto.getRandomValues(new Uint8Array(32)).reduce((r, i) => {
          return r + pool[i % pool.length];
        }, ''),
      );
    },
  },
}

</script>
