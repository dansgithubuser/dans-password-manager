import axios from 'axios';

const crypto = window.crypto;
const subtle = crypto.subtle;

const pairAlg = { name: 'RSA-OAEP', hash: 'SHA-256' };
const publicOps = ['encrypt', 'wrapKey'];
const privateOps = ['decrypt', 'unwrapKey'];
const teamSecretOps = ['encrypt', 'decrypt'];
const symmetricKeyOps = ['wrapKey', 'unwrapKey'];

const api = axios.create({
  baseURL: 'http://localhost:8080/api/',
});

api.defaults.xsrfHeaderName = 'X-CSRFToken';
api.defaults.xsrfCookieName = 'csrftoken';

// key: key object
// return: string
async function jwkify(key) {
  return JSON.stringify(await subtle.exportKey('jwk', key));
}

// n: number of bytes
// return: Uint8Array(n)
function genRandom(n) {
  return crypto.getRandomValues(new Uint8Array(n));
}

// return: Uint8Array(12)
function genIv() {
  return genRandom(12);
}

// key: key object
// symmetricKey: key object
// return: object
async function wrapPrivateKey(key, symmetricKey) {
  const iv = genIv();
  return {
    wrap: Array.from(new Uint8Array(await subtle.wrapKey(
      'jwk',
      key,
      symmetricKey,
      { name: 'AES-GCM', iv },
    ))),
    iv: Array.from(iv),
  };
}

// key: result of wrapPrivateKey
// symmetricKey: key object
// return: key object
function unwrapPrivateKey(key, symmetricKey) {
  return subtle.unwrapKey(
    'jwk',
    (new Uint8Array(key.wrap)).buffer,
    symmetricKey,
    { name: 'AES-GCM', iv: new Uint8Array(key.iv) },
    pairAlg,
    true,
    privateOps,
  );
}

// key: key object
// publicKey: key object
// return: object
async function wrapTeamSecret(key, publicKey) {
  return Array.from(new Uint8Array(await subtle.wrapKey(
    'jwk',
    key,
    publicKey,
    { name: pairAlg.name },
  )));
}

// key: result of wrapTeamSecret
// privateKey: key object
// return: key object
function unwrapTeamSecret(key, privateKey) {
  return subtle.unwrapKey(
    'jwk',
    (new Uint8Array(key)).buffer,
    privateKey,
    { name: pairAlg.name },
    'AES-GCM',
    true,
    teamSecretOps,
  );
}

// key: parsed JSON web key
// return: key object
function importKey(key, keyOps = ['encrypt', 'decrypt'], keyAlgo = 'AES-GCM') {
  return subtle.importKey('jwk', key, keyAlgo, true, keyOps);
}

// text: string
// return: Uint8Array
function textEncode(text) {
  return (new TextEncoder()).encode(text);
}

// password: string
// salt: Uint8Array(16)
// return: key object
async function getUserSymmetricKey(password, salt) {
  if (password === undefined) return importKey(
    JSON.parse(localStorage.symmetricKey),
    symmetricKeyOps,
  );
  const material = await subtle.importKey(
    'raw',
    textEncode(password),
    { name: 'PBKDF2' },
    false,
    ['deriveKey'],
  );
  return subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt,
      iterations: 100000,
      hash: 'SHA-256',
    },
    material,
    { 'name': 'AES-GCM', length: 256 },
    true,
    symmetricKeyOps,
  );
}

// username: string
// symmmetricKey: key object
// publicKey: serialized JWK
// privateKey: key object
async function storeUserInfo(username, symmetricKey, publicKey, privateKey) {
  window.localStorage.username = username;
  window.localStorage.symmetricKey = await jwkify(symmetricKey);
  window.localStorage.publicKey = publicKey;
  window.localStorage.privateKey = await jwkify(privateKey);
}

// return: key object
function getUserPublicKey() {
  return importKey(
    JSON.parse(window.localStorage.publicKey),
    publicOps,
    pairAlg,
  );
}

// return: key object
function getUserPrivateKey() {
  return importKey(
    JSON.parse(window.localStorage.privateKey),
    privateOps,
    pairAlg,
  );
}

// team: int or string
// return: key object
function getTeamSecret(team) {
  return importKey(JSON.parse(window.localStorage.teamSecrets)[team]);
}

// value: string
// key: key object
// return: string
async function encrypt(value, key) {
  const iv = genIv();
  return JSON.stringify({
    ciphertext: Array.from(new Uint8Array(await subtle.encrypt(
      { name: 'AES-GCM', iv },
      key,
      textEncode(value),
    ))),
    iv: Array.from(iv),
  });
}

// value: result of encrypt
// key: key object
// return: string
async function decrypt(value, key) {
  const { ciphertext, iv } = JSON.parse(value);
  return (new TextDecoder).decode(await subtle.decrypt(
    { name: 'AES-GCM', iv: new Uint8Array(iv) },
    key,
    new Uint8Array(ciphertext),
  ));
}

export default {
  async signup(username, password, password_confirmation) {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password1', password);
    params.append('password2', password_confirmation);
    const salt = genRandom(16);
    params.append('salt', JSON.stringify(Array.from(salt)));
    const symmetricKey = await getUserSymmetricKey(password, salt);
    const pair = await subtle.generateKey(
      {
        ...pairAlg,
        modulusLength: 4096,
        publicExponent: new Uint8Array([1, 0, 1]),
      },
      true,
      publicOps.concat(privateOps),
    );
    const publicKey = await jwkify(pair.publicKey);
    params.append('publicKey', publicKey);
    const privateKey = JSON.stringify(await wrapPrivateKey(pair.privateKey, symmetricKey));
    params.append('privateKey', privateKey);
    const response = await api.post('signup', params);
    if (response.status == 201)
      await storeUserInfo(username, symmetricKey, publicKey, pair.privateKey);
    return response;
  },
  async login(username, password) {
    const response = await api.post('login', { username, password });
    if (response.status == 200) {
      const symmetricKey = await getUserSymmetricKey(password, new Uint8Array(response.data.salt));
      const privateKey = await unwrapPrivateKey(response.data.privateKey, symmetricKey);
      await storeUserInfo(username, symmetricKey, response.data.publicKey, privateKey);
    }
    return response;
  },
  async teamCreate(name) {
    var teamSecret = await subtle.generateKey(
      { name: 'AES-GCM', length: 256 },
      true,
      teamSecretOps,
    );
    const publicKey = await getUserPublicKey();
    teamSecret = JSON.stringify(await wrapTeamSecret(teamSecret, publicKey));
    api.post('team', { name, teamSecret });
  },
  async teamList() {
    const privateKey = await getUserPrivateKey();
    const teams = (await api.get('team')).data.teams;
    window.localStorage.teamSecrets = JSON.stringify(await teams.reduce(
      async (teamSecrets, team) => {
        teamSecrets[team.id] = await subtle.exportKey(
          'jwk',
          await unwrapTeamSecret(team.secret, privateKey)
        );
        return teamSecrets;
      },
      {},
    ));
    return teams;
  },
  async itemCreate(name, target, value, notes, team) {
    const teamSecret = await getTeamSecret(team);
    value = await encrypt(value, teamSecret);
    notes = await encrypt(notes, teamSecret);
    api.post('item', { name, target, value, notes, team });
  },
  async itemList(team) {
    const teamSecret = await getTeamSecret(team);
    const items = (await api.get('item', { params: { team } })).data.items;
    for (const i of items) {
      i.value = await decrypt(i.value, teamSecret);
      i.notes = await decrypt(i.notes, teamSecret);
    }
    return items;
  },
  async verify(username, team) {
    return (await api.post('verify', { username, team })).data.value;
  },
  async invite(username, team, verificationValue) {
    const resp = await api.get('public_key', { params: { username } });
    var inviteePublicKey = resp.data.publicKey;
    inviteePublicKey = await importKey(
      JSON.parse(inviteePublicKey),
      publicOps,
      pairAlg,
    );
    var teamSecret = await getTeamSecret(team);
    teamSecret = await wrapTeamSecret(teamSecret, inviteePublicKey);
    return api.post('invite', { username, team, verificationValue, teamSecret });
  },
};
