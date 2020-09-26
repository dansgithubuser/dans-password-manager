import axios from 'axios';
import { Jose } from 'jose-jwe-jws';

const crypto = window.crypto;
const subtle = crypto.subtle;

const pairAlg = { name: 'RSA-OAEP', hash: 'SHA-256' };
const publicOps = ['encrypt', 'wrapKey'];
const privateOps = ['decrypt', 'unwrapKey'];
const teamSecretOps = ['encrypt', 'decrypt'];
const symmetricKeyOps = ['wrapKey', 'unwrapKey'];

const api = axios.create({ baseURL: '/api/' });

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

// return: key object
function genTeamSecret() {
  return subtle.generateKey(
    { name: 'AES-GCM', length: 256 },
    true,
    teamSecretOps,
  );
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
  async signup(username, password) {
    const params = new URLSearchParams();
    params.append('username', username);
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

    //function ab2str(buf) {
    //  return String.fromCharCode.apply(null, new Uint8Array(buf));
    //}
    console.log('hello there 1');
    exported = await subtle.exportKey('pkcs8', pair.publicKey);
    console.log('hello there 2');
    //const exportedAsString = ab2str(exported);
    //const exportedAsBase64 = window.btoa(exportedAsString);
    //const pemExported = `-----BEGIN PRIVATE KEY-----\n${exportedAsBase64}\n-----END PRIVATE KEY-----`;
    //params.append('pem', pemExported);

    const response = await api.post('signup', params);
    if (response.status == 201)
      await storeUserInfo(username, symmetricKey, publicKey, pair.privateKey);
    return response;
  },
  async login(username, password) {

ct = [61, 87, 98, 137, 228, 162, 245, 255, 249, 134, 57, 250, 0, 93, 243, 191, 184, 228, 191, 142, 162, 88, 248, 65, 180, 97, 77, 35, 232, 110, 247, 59, 21, 155, 154, 18, 165, 20, 88, 248, 19, 61, 32, 85, 80, 246, 50, 33, 86, 22, 244, 156, 74, 152, 210, 132, 153, 151, 118, 232, 173, 11, 132, 44, 85, 116, 83, 166, 61, 110, 44, 55, 193, 26, 142, 45, 7, 25, 251, 223, 128, 10, 243, 124, 133, 124, 91, 91, 98, 98, 12, 72, 150, 223, 141, 182, 101, 145, 17, 94, 75, 76, 249, 223, 177, 153, 29, 213, 49, 180, 97, 44, 68, 198, 41, 33, 21, 171, 232, 7, 120, 157, 116, 176, 128, 61, 167, 100, 10, 167, 102, 46, 253, 224, 136, 77, 184, 49, 225, 46, 223, 141, 116, 227, 135, 173, 102, 157, 123, 223, 42, 203, 37, 89, 216, 16, 234, 195, 242, 122, 38, 98, 74, 255, 94, 115, 135, 35, 11, 180, 249, 123, 164, 207, 186, 24, 45, 63, 236, 116, 154, 22, 165, 66, 43, 31, 77, 238, 172, 13, 72, 11, 44, 32, 22, 117, 14, 252, 56, 173, 210, 238, 186, 98, 151, 97, 108, 198, 239, 67, 29, 245, 226, 3, 107, 3, 78, 205, 252, 19, 117, 208, 28, 58, 50, 218, 177, 225, 76, 116, 101, 81, 152, 209, 53, 113, 175, 2, 146, 254, 8, 87, 16, 104, 195, 219, 200, 90, 239, 84, 114, 98, 247, 88, 45, 248, 173, 249, 34, 228, 116, 107, 143, 93, 192, 136, 198, 204, 29, 171, 216, 140, 200, 63, 109, 252, 228, 64, 247, 133, 239, 6, 201, 129, 190, 72, 183, 249, 206, 65, 19, 154, 13, 73, 253, 19, 160, 106, 81, 166, 219, 42, 117, 161, 141, 70, 84, 182, 81, 84, 46, 226, 235, 132, 42, 132, 25, 126, 49, 238, 175, 215, 243, 131, 208, 228, 197, 26, 34, 182, 82, 66, 191, 111, 202, 30, 97, 127, 16, 155, 156, 70, 176, 139, 51, 239, 30, 105, 217, 87, 113, 106, 3, 132, 9, 189, 24, 195, 233, 139, 252, 87, 18, 84, 176, 255, 149, 237, 57, 161, 177, 127, 247, 141, 225, 175, 138, 222, 176, 245, 182, 214, 201, 38, 48, 176, 150, 172, 3, 165, 191, 88, 219, 70, 151, 150, 62, 240, 238, 251, 197, 213, 250, 17, 155, 24, 138, 140, 191, 180, 3, 188, 129, 39, 237, 92, 7, 20, 5, 204, 203, 127, 137, 224, 130, 223, 28, 100, 155, 231, 226, 192, 238, 137, 245, 69, 174, 48, 254, 43, 170, 3, 147, 78, 186, 100, 225, 122, 147, 113, 235, 168, 34, 173, 21, 231, 248, 161, 230, 180, 215, 101, 222, 22, 222, 82, 124, 56, 213, 29, 92, 223, 13, 249, 4, 28, 190, 211, 144, 209, 117, 47, 156, 252, 113, 127, 54, 5, 224, 153, 164, 174, 109, 112, 162, 46, 239, 41, 254, 160, 240, 174, 37, 89, 84, 29, 87, 70, 11, 76, 103, 62];


    const challenge = await api.post('login_challenge', { username });
    console.log('hello');
    if (challenge.status != 200) return challenge;
    console.log('hello2');
    const symmetricKey = await getUserSymmetricKey(password, new Uint8Array(challenge.data.salt));
    const privateKey = await unwrapPrivateKey(challenge.data.privateKey, symmetricKey);
    await storeUserInfo(username, symmetricKey, challenge.data.publicKey, privateKey);
    console.log('nonce enc:', challenge.data.nonce_encrypted)
    console.log('priv key:', privateKey);
    console.log('Jose', Jose);
    const cryptographer = new Jose.WebCryptographer();
    const decrypter = new Jose.JoseJWE.Decrypter(cryptographer, privateKey);
    const nonce = await decrypter.decrypt(challenge.data.nonce_encrypted);
    console.log('nonce:', nonce);
    const response = await api.post('login', { username, nonce });
    return response;
  },
  async teamCreate(name) {
    var teamSecret = await genTeamSecret();
    const publicKey = await getUserPublicKey();
    teamSecret = await wrapTeamSecret(teamSecret, publicKey);
    await api.post('team', { name, teamSecret });
  },
  async teamList() {
    const privateKey = await getUserPrivateKey();
    const teams = (await api.get('team')).data.teams;
    window.localStorage.teamSecretsUpdatedAt = JSON.stringify(teams.reduce(
      (teamSecretsUpdatedAt, team) => {
        teamSecretsUpdatedAt[team.id] = team.secretUpdatedAt;
        return teamSecretsUpdatedAt;
      },
      {},
    ));
    const teamSecrets = {};
    for (const team of teams) {
      teamSecrets[team.id] = await subtle.exportKey(
        'jwk',
        await unwrapTeamSecret(team.secret, privateKey)
      );
    }
    window.localStorage.teamSecrets = JSON.stringify(teamSecrets);
    return teams;
  },
  async itemCreate(name, target, user, value, notes, team) {
    const teamSecret = await getTeamSecret(team);
    user  = await encrypt(user , teamSecret);
    value = await encrypt(value, teamSecret);
    notes = await encrypt(notes, teamSecret);
    await api.post('item', {
      name, target, user, value, notes, team,
      teamSecretUpdatedAt: JSON.parse(window.localStorage.teamSecretsUpdatedAt)[team],
    });
  },
  async itemUpdate(id, name, target, user, value, notes, team) {
    const teamSecret = await getTeamSecret(team);
    user  = await encrypt(user , teamSecret);
    value = await encrypt(value, teamSecret);
    notes = await encrypt(notes, teamSecret);
    await api.post('item', {
      id, name, target, user, value, notes,
      teamSecretUpdatedAt: JSON.parse(window.localStorage.teamSecretsUpdatedAt)[team],
    });
  },
  async itemList(team) {
    const teamSecretUpdatedAt = JSON.parse(window.localStorage.teamSecretsUpdatedAt)[team];
    const items = (await api.get('item', { params: { team, teamSecretUpdatedAt } })).data.items;
    const teamSecret = await getTeamSecret(team);
    for (const i of items) {
      i.user  = await decrypt(i.user , teamSecret);
      i.value = await decrypt(i.value, teamSecret);
      i.notes = await decrypt(i.notes, teamSecret);
    }
    return items;
  },
  async verify(username, team) {
    return (await api.post('verify', { username, team })).data.value;
  },
  async verificationValues() {
    return (await api.get('verification_values')).data.values;
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
  async revoke(username, team) {
    await api.post('revoke', { username, team });
    const oldTeamSecret = await getTeamSecret(team);
    const newTeamSecret = await genTeamSecret();
    // team items
    const oldItems = (await api.get('item', { params: { team } })).data.items;
    const items = {};
    for (const item of oldItems) {
      items[item.id] = {
        user : await encrypt(await decrypt(item.user , oldTeamSecret), newTeamSecret),
        value: await encrypt(await decrypt(item.value, oldTeamSecret), newTeamSecret),
        notes: await encrypt(await decrypt(item.notes, oldTeamSecret), newTeamSecret),
      };
    }
    // teammates' team secrets
    const publicKeys = (await api.get('public_key', { params: { team } })).data.publicKeys;
    const teamSecrets = {};
    for (const publicKey of publicKeys) {
      teamSecrets[publicKey.userId] = await wrapTeamSecret(newTeamSecret, await importKey(
        JSON.parse(publicKey.publicKey),
        publicOps,
        pairAlg,
      ));
    }
    // post
    await api.post('rotate', { team, items, teamSecrets });
  },
};
