<template>
  <button v-if='isDev()' @click='test' style='position:fixed; right:0; z-index:100'>test</button>
  <!-- signup -->
  <Collapse label="signup">
    <Input v-model='signupUsername' label='username'/>
    <Input v-model='signupPassword' label='password' type='password'/>
    <Input v-model='signupPasswordConfirmation' label='confirm password' type='password'/>
    <button @click='signup'>signup</button>
  </Collapse>
  <!-- login -->
  <Collapse label="login">
    <Input v-model='loginUsername' label='username'/>
    <Input v-model='loginPassword' label='password' type='password'/>
    <button @click='login'>login</button>
    <template v-if='username'>
      logged in as {{username}}
    </template>
  </Collapse>
  <!-- create team -->
  <Collapse label="create team">
    <Input v-model='teamCreateName' label='name'/>
    <button @click='teamCreate'>create team</button>
  </Collapse>
  <!-- items -->
  <Collapse label="items">
    <Collapse v-for='(team, i) in teams' :key='i' :label="team.name">
      <Input v-model='teamToFilter[team.id]' label='filter'/>
      <Item
        :item='itemCreate'
        :teamId='team.id'
        :updateItems='updateItems'
        :create=true
        @value='itemCreate.value = $event'
        class="m1t"
      />
      <Item
        v-for='(item, j) in filterItems(team.id)'
        :item='item'
        :teamId='team.id'
        :updateItems='updateItems'
        class="m1t"
      />
    </Collapse>
  </Collapse>
  <!-- verify -->
  <Collapse label="verify">
    <Input v-model='verifyUsername' label='username'/>
    <Search v-model='verifyTeam' label='team' :options=teamNames />
    <button @click='verify'>verify</button>
    <div>
      <p v-for='(value, i) in verificationValues' :key='i'>
        {{ verificationValues[i] }}
      </p>
    </div>
  </Collapse>
  <!-- invite -->
  <Collapse label="invite">
    <Input v-model='inviteUsername' label='username'/>
    <Search v-model='inviteTeam' label='team' :options=teamNames />
    <Input v-model='inviteVerificationValue' label='verification value'/>
    <button @click='invite'>invite</button>
  </Collapse>
  <!-- revoke -->
  <Collapse label="revoke">
    <Input v-model='revokeUsername' label='username'/>
    <Search v-model='revokeTeam' label='team' :options=teamNames />
    <button @click='revoke'>revoke</button>
  </Collapse>
</template>

<script>

import Collapse from './Collapse.vue'
import Input from './Input.vue'
import Item from './Item.vue'
import Search from './Search.vue'

import api from '../api.js'

export default {
  name: 'Main',
  components: {
    Collapse,
    Input,
    Item,
    Search,
  },
  data: () => ({
    signupUsername: '',
    signupPassword: '',
    signupPasswordConfirmation: '',
    loginUsername: '',
    loginPassword: '',
    username: null,
    teamCreateName: '',
    teams: [],
    teamNames: [],
    teamToFilter: {},
    itemCreate: {
      name: '',
      target: '',
      user: '',
      value: '',
      notes: '',
    },
    teamToItems: {},
    verifyUsername: '',
    verifyTeam: '',
    verificationValues: [],
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
      if (this.username) {
        this.updateTeams();
        this.updateVerificationValues();
      }
    },
    teamCreate() {
      api.teamCreate(this.teamCreateName)
        .then(this.updateTeams);
    },
    async updateTeams() {
      this.teams = await api.teamList();
      this.teamNames = this.teams.map(i => ({ text: i.name, value: i.id }));
      this.teamToItems = {};
      for (const team of this.teams) this.updateItems(team.id);
    },
    async updateItems(teamId) {
      this.teamToItems[teamId] = await api.itemList(teamId);
    },
    filterItems(teamId) {
      const filter = this.teamToFilter[teamId];
      const items = this.teamToItems[teamId];
      if (!filter || filter.length < 3) return items;
      const result = {};
      for (const item of items) {
        let score;
        // name starts with
        if (item.name.toLowerCase().startsWith(filter))
          score = 1;
        // name or target contains
        else if (item.name.toLowerCase().includes(filter) || item.target.toLowerCase().includes(filter))
          score = 2;
        // user contains
        else if (item.user.toLowerCase().includes(filter))
          score = 3;
        // add to result
        if (score)
          result[score+item.name] = item;
        // early exit
        if (result.length > 5) break;
      }
      return Object.keys(result).sort().map(i => result[i]);
    },
    verify() {
      api.verify(this.verifyUsername, this.verifyTeam);
    },
    async updateVerificationValues() {
      this.verificationValues = await api.verificationValues();
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
      const user1 = self.crypto.randomUUID();
      console.log('user1:', user1); // eslint-disable-line no-console
      await api.signup(user1, password, password);
      await api.teamCreate('test-team-name');
      var teams = await api.teamList();
      const team = teams[0].id;
      await api.itemCreate(
        'test-item-name',
        'test-item-target',
        'test-item-user',
        'test-item-value',
        'test-item-notes',
        team,
      );
      var items = await api.itemList(team);
      if (items[0].value != 'test-item-value') console.error('wrong value for user1!'); // eslint-disable-line no-console
      // invite
      const user2 = self.crypto.randomUUID();
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
      console.log('revoking'); // eslint-disable-line no-console
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
    window.refs = { app: this };
    this.console = console;
  },
}

</script>
