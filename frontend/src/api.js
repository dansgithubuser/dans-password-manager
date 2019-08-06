import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8080/api/',
});

export default {
  signup (username, password) {
    return api.post('/signup', {username, password1: password, password2: password});
  },
};
