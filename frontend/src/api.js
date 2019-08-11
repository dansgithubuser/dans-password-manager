import axios from 'axios';
import cryptico from 'cryptico';
import bcrypt from 'bcryptjs';

const api = axios.create({
  baseURL: 'http://localhost:8080/api/',
});

api.defaults.xsrfHeaderName = 'X-CSRFToken';
api.defaults.xsrfCookieName = 'csrftoken';

function storeUserInfo(username, privateKey) {
  window.localStorage.username = username;
  window.localStorage.privateKey = JSON.stringify(privateKey.toJSON());
}

function parseKeyPair(serialized) {
  const privateKey = cryptico.RSAKey.parse(serialized);
  const publicKey = cryptico.publicKeyString(privateKey);
  return { publicKey, privateKey };
}

export default {
  async signup(username, password, password_confirmation) {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password1', password);
    params.append('password2', password_confirmation);
    const salt = bcrypt.genSaltSync(10);
    params.append('salt', salt);
    const hash = bcrypt.hashSync(password, salt);
    const privateKey = cryptico.generateRSAKey(hash, 2048);
    const publicKey = cryptico.publicKeyString(privateKey);
    params.append('publicKey', publicKey);
    const response = await api.post('signup', params);
    if (response.status == 201) storeUserInfo(username, privateKey);
  },
  async login(username, password) {
    const response = await api.post('login', { username, password });
    if (response.status == 200) {
      const hash = bcrypt.hashSync(password, response.salt);
      const privateKey = cryptico.generateRSAKey(hash, 2048);
      storeUserInfo(username, privateKey);
    }
    return response;
  },
  teamCreate(name) {
    const salt = bcrypt.genSaltSync(10);
    var teamSecret = bcrypt.hashSync(window.localStorage.privateKey, salt);
    teamSecret = JSON.stringify(cryptico.generateRSAKey(teamSecret, 2048).toJSON());
    teamSecret = cryptico.encrypt(
      teamSecret,
      parseKeyPair(window.localStorage.privateKey).publicKey,
    ).cipher;
    return api.post('team', { name, teamSecret });
  },
  async teamList() {
    const privateKey = parseKeyPair(window.localStorage.privateKey).privateKey;
    const teams = (await api.get('team')).data;
    window.localStorage.teamSecrets = JSON.stringify(teams.reduce(
      (teamSecrets, team) => {
        teamSecrets[team.id] = cryptico.decrypt(team.secret, privateKey).plaintext;
        return teamSecrets;
      },
      {},
    ));
    for (const team of teams) delete team.secret;
    return teams;
  },
  itemCreate(name, target, value, notes, team) {
    const publicKey = parseKeyPair(JSON.parse(window.localStorage.teamSecrets)[team]).publicKey;
    value = cryptico.encrypt(value, publicKey).cipher;
    notes = cryptico.encrypt(notes, publicKey).cipher;
    return api.post('item', { name, target, value, notes, team });
  },
  async itemList(team) {
    const privateKey = parseKeyPair(JSON.parse(window.localStorage.teamSecrets)[team]).privateKey;
    const items = (await api.get('item', { params: { team } })).data;
    for (const i of items) {
      i.value = cryptico.decrypt(i.value, privateKey).plaintext;
      i.notes = cryptico.decrypt(i.notes, privateKey).plaintext;
    }
    return items;
  },
  async verify(username, team) {
    return (await api.post('verify', { username, team })).data;
  },
};
