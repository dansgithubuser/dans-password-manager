<template>
  <div>
    username<input type='text' v-model='signupUsername'><br>
    password<input type='test' v-model='signupPassword'><br>
    <input type='button' value='signup' @click='signup'>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Main',
  data: () => ({
    signupUsername: '',
    signupPassword: '',
  }),
  methods: {
    signup () {
      console.log(axios.get('http://localhost:8000/static/dans_password_manager/index.html'));
    },
  },
}
</script>
