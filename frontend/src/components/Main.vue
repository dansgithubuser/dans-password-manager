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
    <v-text-field v-model='teamCreateName' label='name'/>
    <v-btn @click='teamCreate'>create team</v-btn>
    <v-list>
      <v-list-item v-for='{ id, name } of teams' :key='id'>
        {{ id }}: {{ name }}
      </v-list-item>
    </v-list>
    <v-text-field v-model='itemCreateName' label='name'/>
    <v-text-field v-model='itemCreateTarget' label='target'/>
    <v-text-field v-model='itemCreateValue' label='value'/>
    <v-text-field v-model='itemCreateNotes' label='notes'/>
    <v-text-field v-model='itemCreateTeam' label='team'/>
    <v-btn @click='itemCreate'>create item</v-btn>
    <v-list>
      <v-list-item v-for='(items, team) in teamToItems' :key='team'>
        <v-list>
          <v-list-item v-for='({ name, target, value, notes }, i) of items' :key='i'>
            {{ name }}: {{ target }}, {{ value }}, {{ notes }}
          </v-list-item>
        </v-list>
      </v-list-item>
    </v-list>
    <v-text-field v-model='verifyUsername' label='username'/>
    <v-text-field v-model='verifyTeam' label='team'/>
    <v-btn @click='verify'>verify</v-btn>
    <v-text-field v-model='inviteUsername' label='username'/>
    <v-text-field v-model='inviteTeam' label='team'/>
    <v-text-field v-model='inviteVerificationValue' label='verification value'/>
    <v-btn @click='invite'>invite</v-btn>
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
    teams: [],
    itemCreateName: '',
    itemCreateTarget: '',
    itemCreateValue: '',
    itemCreateNotes: '',
    itemCreateTeam: '',
    teamToItems: {},
    verifyUsername: '',
    verifyTeam: '',
    inviteUsername: '',
    inviteTeam: '',
    inviteVerificationValue: '',
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
      api.teamCreate(this.teamCreateName)
        .then(this.updateTeams);
    },
    async updateTeams() {
      this.teams = await api.teamList();
      this.teamToItems = {};
      for (const team of this.teams) this.updateItems(team.id);
    },
    itemCreate() {
      api.itemCreate(this.itemCreateName, this.itemCreateTarget, this.itemCreateValue, this.itemCreateNotes, this.itemCreateTeam)
        .then(() => this.updateItems(this.itemCreateTeam));
    },
    async updateItems(team) {
      this.$set(this.teamToItems, team, await api.itemList(team));
    },
    verify() {
      api.verify(this.verifyUsername, this.verifyTeam);
    },
    invite() {
      api.invite(this.inviteUsername, this.inviteTeam, this.inviteVerificationValue);
    },
  },
  mounted() {
    this.updateUsername();
    this.updateTeams();
  },
}
</script>
