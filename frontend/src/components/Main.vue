<template>
  <v-container>
    <v-text-field v-model='signupUsername' label='username'/>
    <v-text-field v-model='signupPassword' label='password'/>
    <v-text-field v-model='signupPasswordConfirmation' label='confirm password'/>
    <v-btn @click='signup'>signup</v-btn>
    <v-text-field v-model='loginUsername' label='username'/>
    <v-text-field v-model='loginPassword' label='password'/>
    <v-btn @click='login'>login</v-btn>
    <template v-if='username'>
      logged in as {{username}}
    </template>
    <v-text-field v-model='teamCreateName' label='team name'/>
    <v-btn @click='teamCreate'>create team</v-btn>
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
    username: null,
    teamCreateName: '',
  }),
  methods: {
    signup() {
      api.signup(this.signupUsername, this.signupPassword, this.signupPasswordConfirmation)
        .then(this.updateUsername);
    },
    login() {
      api.login(this.loginUsername, this.loginPassword)
        .then(this.updateUsername);
    },
    updateUsername() {
      this.username = localStorage.username;
    },
    teamCreate() {
      api.teamCreate(this.teamCreateName);
    },
  },
  mounted() {
    this.updateUsername();
  },
}
</script>
