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

.label {
  font-size: small;
  color: gray;
}

.border {
  border-style: solid;
}
.bg-lightgray {
  background-color: lightgray;
}

.row {
  display: flex;
}
.col {
  display: flex;
  flex-direction: column;
}

.mb {
  margin-bottom: 1em;
}

.hidden {
  visibility: hidden;
}

</style>

<template>
  <div class='row'>
    <div class='col'>
      <label class='label'>name</label>
      <input v-model='item.name' class='border mb'/>
      <label class='label'>target</label>
      <input v-model='item.target' class='border mb'/>
    </div>
    <div class='col'>
      <label class='label'>user</label>
      <input v-model='item.user' class='border mb'/>
      <label class='label'>value</label>
      <input v-model='item.value' class='border mb value'/>
    </div>
    <div class='col'>
      <label class='label'>notes</label>
      <textarea v-model='item.notes' class='border mb notes' style='height: 100%'/>
    </div>
    <div class='col'>
      <template v-if='!create'>
        <label class='hidden'>x</label>
        <button @click='itemUpdate(item, teamId)' class='bg-lightgray mb'>update item</button>
      </template>
      <template v-else>
        <label class='hidden'>x</label>
        <button @click='itemCreate(teamId)' class='bg-lightgray mb'>create item</button>
        <label class='hidden'>x</label>
        <button @click='random()' class='bg-lightgray mb'>random</button>
      </template>
    </div>
  </div>
</template>

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
