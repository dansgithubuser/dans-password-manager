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

function getKeyPair() {
  const privateKey = cryptico.RSAKey.parse(window.localStorage.privateKey);
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
    teamSecret = cryptico.encrypt(teamSecret, getKeyPair().publicKey);
    return api.post('team', { name, teamSecret });
  },
};
