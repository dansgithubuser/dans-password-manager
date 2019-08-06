<template>
  <v-container>
    <v-text-field v-model='signupUsername' label='username'/>
    <v-text-field v-model='signupPassword' label='password'/>
    <v-btn @click='signup'>signup</v-btn>
  </v-container>
</template>

<script>
import api from '../api.js'

export default {
  name: 'Main',
  data: () => ({
    signupUsername: '',
    signupPassword: '',
  }),
  methods: {
    signup () {
      api.signup(this.signupUsername, this.signupPassword);
    },
  },
}
</script>
