<template>
  <v-container>
    <v-text-field v-model='signupUsername' label='username'/>
    <v-text-field v-model='signupPassword' label='password'/>
    <v-text-field v-model='signupPasswordConfirmation' label='confirm password'/>
    <v-btn @click='signup'>signup</v-btn>
    <v-text-field v-model='loginUsername' label='username'/>
    <v-text-field v-model='loginPassword' label='password'/>
    <v-btn @click='login'>login</v-btn>
    <template v-if='loggedIn'>
      logged in!
    </template>
  </v-container>
</template>

<script>
import api from '../api.js'

export default {
  name: 'Main',
  data: () => ({
    signupUsername: '',
    signupPassword: '',
    signupPasswordConfirmation: '',
    loginUsername: '',
    loginPassword: '',
    loggedIn: false,
  }),
  methods: {
    signup () {
      api.signup(this.signupUsername, this.signupPassword, this.signupPasswordConfirmation)
        .then(this.updateLoggedIn);
    },
    login () {
      api.login(this.loginUsername, this.loginPassword)
        .then(this.updateLoggedIn);
    },
    updateLoggedIn () {
      this.loggedIn = localStorage.loggedIn;
    },
  },
  mounted () {
    this.updateLoggedIn();
  },
}
</script>
