<style>
.value input {
  color: rgba(0, 0, 0, 0) !important;
}
.value ::selection {
    color: rgba(0, 0, 0, 0) !important;
}
.notes input {
  color: rgba(0, 0, 0, 0) !important;
}
</style>

<template>
  <v-container>
    <v-btn v-if='isDev()' @click='test' style='position:fixed; right:0; z-index:100'>test</v-btn>
    <v-expansion-panels>
      <v-expansion-panel>
        <v-expansion-panel-header>signup</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-text-field v-model='signupUsername' label='username'/>
          <v-text-field v-model='signupPassword' label='password' :type='"password"'/>
          <v-text-field v-model='signupPasswordConfirmation' label='confirm password' :type='"password"'/>
          <v-btn @click='signup'>signup</v-btn>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>login</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-text-field v-model='loginUsername' label='username'/>
          <v-text-field v-model='loginPassword' label='password' :type='"password"'/>
          <v-btn @click='login'>login</v-btn>
          <template v-if='username'>
            logged in as {{username}}
          </template>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>create team</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-text-field v-model='teamCreateName' label='name'/>
          <v-btn @click='teamCreate'>create team</v-btn>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>items</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-expansion-panels>
            <v-expansion-panel v-for='(team, i) in teams' :key='i'>
              <v-expansion-panel-header>
                {{ team.name }}
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-list>
                  <v-list-item v-for='(item, j) in teamToItems[team.id]' :key='j'>
                    <v-text-field v-model='item.name' label='name'/>
                    <v-text-field v-model='item.target' label='target'/>
                    <v-text-field v-model='item.value' label='value' class='value'/>
                    <v-text-field v-model='item.notes' label='notes' class='notes'/>
                    <v-btn
                      @click='itemUpdate(item, team.id)'
                    >update item</v-btn>
                  </v-list-item>
                  <v-list-item>
                    <v-text-field v-model='itemCreateName' label='name'/>
                    <v-text-field v-model='itemCreateTarget' label='target'/>
                    <v-text-field v-model='itemCreateValue' label='value' class='value'/>
                    <v-text-field v-model='itemCreateNotes' label='notes'/>
                    <v-btn @click='itemCreate(team.id)'>create item</v-btn>
                  </v-list-item>
                </v-list>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>verify</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-text-field v-model='verifyUsername' label='username'/>
          <v-text-field v-model='verifyTeam' label='team'/>
          <v-btn @click='verify'>verify</v-btn>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>invite</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-text-field v-model='inviteUsername' label='username'/>
          <v-text-field v-model='inviteTeam' label='team'/>
          <v-text-field v-model='inviteVerificationValue' label='verification value'/>
          <v-btn @click='invite'>invite</v-btn>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>revoke</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-text-field v-model='revokeUsername' label='username'/>
          <v-text-field v-model='revokeTeam' label='team'/>
          <v-btn @click='revoke'>revoke</v-btn>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>

<script>
import api from '../api.js'
import uuidv4 from 'uuid/v4'

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
    teamToItems: {},
    verifyUsername: '',
    verifyTeam: '',
    inviteUsername: '',
    inviteTeam: '',
    inviteVerificationValue: '',
    revokeUsername: '',
    revokeTeam: '',
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
      this.updateTeams();
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
    itemCreate(team) {
      api.itemCreate(this.itemCreateName, this.itemCreateTarget, this.itemCreateValue, this.itemCreateNotes, team)
        .then(() => this.updateItems(team));
    },
    itemUpdate(item, team) {
      api.itemUpdate(item.id, item.name, item.target, item.value, item.notes, team)
        .then(() => this.updateItems(team));
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
    async revoke() {
      await api.revoke(this.revokeUsername, this.revokeTeam);
      await this.updateTeams();
    },
    isDev() {
      return process.env.NODE_ENV == 'development';
    },
    async test() {
      const password = 'jjo8OSD8882m3osidmcsuoOSID823mIOSDmoim';
      // single-user stuff
      const user1 = uuidv4();
      console.log('user1:', user1); // eslint-disable-line no-console
      await api.signup(user1, password, password);
      await api.teamCreate('test-team-name');
      var teams = await api.teamList();
      const team = teams[0].id;
      await api.itemCreate('test-item-name', 'test-item-target', 'test-item-value', 'test-item-notes', team);
      var items = await api.itemList(team);
      if (items[0].value != 'test-item-value') console.error('wrong value for user1!'); // eslint-disable-line no-console
      // invite
      const user2 = uuidv4();
      console.log('user2:', user2); // eslint-disable-line no-console
      await api.signup(user2, password, password);
      await api.login(user1, password);
      await api.verify(user2, team);
      await api.login(user2, password);
      const verificationValues = await api.verificationValues();
      await api.login(user1, password);
      await api.invite(user2, team, verificationValues[0]);
      await api.login(user2, password);
      await api.teamList();
      items = await api.itemList(team);
      if (items[0].value != 'test-item-value') console.error('wrong value for user2!'); // eslint-disable-line no-console
      // revoke
      await api.login(user1, password);
      await api.revoke(user2, team);
      await api.teamList();
      items = await api.itemList(team);
      if (items[0].value != 'test-item-value') console.error('wrong value for user1 after revoking user2!'); // eslint-disable-line no-console
      await api.login(user2, password);
      teams = await api.teamList();
      if (teams.length != 0) console.error('user2 was not revoked from team!'); // eslint-disable-line no-console
      //
      console.log('done!'); // eslint-disable-line no-console
    },
  },
  mounted() {
    this.updateUsername();
    this.updateTeams();
  },
}
</script>
