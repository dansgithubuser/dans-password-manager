import axios from 'axios';
import cryptico from 'cryptico';
import bcrypt from 'bcryptjs';

const api = axios.create({
  baseURL: 'http://localhost:8080/api/',
});

api.defaults.xsrfHeaderName = 'X-CSRFToken';
api.defaults.xsrfCookieName = 'csrftoken';

export default {
  async signup (username, password, password_confirmation) {
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
    if (response.status == 201)
      window.localStorage.privateKey = JSON.stringify(privateKey.toJSON());
  },
  async login (username, password) {
    const response = await api.post('login', { username, password });
    if (response.status == 200) {
      const hash = bcrypt.hashSync(password, response.salt);
      const privateKey = cryptico.generateRSAKey(hash, 2048);
      window.localStorage.privateKey = JSON.stringify(privateKey.toJSON());
    }
    return response;
  }
};
