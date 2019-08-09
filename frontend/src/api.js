import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8080/api/',
});

api.defaults.xsrfHeaderName = 'X-CSRFToken';
api.defaults.xsrfCookieName = 'csrftoken';

export default {
  signup (username, password, password_confirmation) {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password1', password);
    params.append('password2', password_confirmation);
    params.append('publicKey', 'pub');
    params.append('privateKey', 'priv');
    return api.post('signup', params);
  },
  login (username, password) {
    return api.post('login', { username, password });
  }
};
