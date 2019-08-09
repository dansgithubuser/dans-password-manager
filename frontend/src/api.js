import axios from 'axios';

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
    params.append('publicKey', 'pub');
    params.append('privateKey', 'priv');
    const response = await api.post('signup', params);
    if (response.status == 201) window.localStorage.loggedIn = true;
  },
  async login (username, password) {
    const response = await api.post('login', { username, password });
    if (response.status == 200) window.localStorage.loggedIn = true;
    return response;
  }
};
