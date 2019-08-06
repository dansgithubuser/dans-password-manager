<template>
  <div>
    username<input type='text' v-model='signupUsername'><br>
    password<input type='test' v-model='signupPassword'><br>
    <input type='button' value='signup' @click='signup'>
  </div>
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
