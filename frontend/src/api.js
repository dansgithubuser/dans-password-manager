import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/',
});

export default {
  signup (username, password) {
    return api.post('/signup', {username, password});
  },
};
