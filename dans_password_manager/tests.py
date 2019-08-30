from . import models

from django.contrib.auth.models import User
from django.test import Client, TestCase
import django.test.client

class SecureClient(Client):
    def get(self, *args, content_type='application/json', **kwargs):
        return super().get(*args, **kwargs, secure=True)

    def post(self, *args, content_type='application/json', **kwargs):
        return super().post(*args, **kwargs, secure=True, content_type=content_type)

    def signup(self, username, password, salt, public_key, private_key):
        return self.post('/api/signup', {
            'username': username,
            'password1': password,
            'password2': password,
            'salt': salt,
            'publicKey': public_key,
            'privateKey': private_key,
        }, content_type=django.test.client.MULTIPART_CONTENT)

class SmokeTestCase(TestCase):
    def test_functional(self):
        # client create
        client = SecureClient()
        # signup
        username = 'smoke_username'
        password = 'acjlimwsjldkfjsldkj'
        salt = '"smoke_salt"'
        public_key = 'smoke_public_key'
        private_key = '"smoke_private_key"'
        response = client.signup(username, password, salt, public_key, private_key)
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username=username)
        self.assertEqual(user.userinfo.public_key, public_key)
        self.assertEqual(user.userinfo.private_key, private_key)
        # login
        response = client.post('/api/login', {
            'username': username,
            'password': password,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'salt': 'smoke_salt',
            'publicKey': 'smoke_public_key',
            'privateKey': 'smoke_private_key',
        })
        # client login
        client.login(username=username, password=password)
        # team create
        team_name = 'smoke_team_name'
        admin_team_secret = '"smoke_team_secret"'
        response = client.post('/api/team', {'name': team_name, 'teamSecret': admin_team_secret})
        self.assertEqual(response.status_code, 201)
        team = models.Team.objects.get(name=team_name)
        membership = models.Membership.objects.get(user=user, team=team)
        self.assertEqual(membership.admin, True)
        self.assertEqual(membership.team_secret, admin_team_secret)
        # teams view
        response = client.get('/api/team').json()
        self.assertEqual(len(response), 1)
        team_id = response['teams'][0]['id']
        team_secret_updated_at = response['teams'][0]['secretUpdatedAt'];
        self.assertEqual(response, {'teams': [{
            'id': team_id,
            'name': team_name,
            'secret': eval(admin_team_secret),
            'secretUpdatedAt': team_secret_updated_at,
            'admin': True,
        }]})
        # item create fails when team secret is outdated
        item_params = {
            'name': 'smoke_item_name',
            'target': 'smoke_item_target',
            'value': 'smoke_item_value',
            'notes': 'smoke_item_notes',
            'team': team.id,
        }
        response = client.post('/api/item', dict(**item_params, teamSecretUpdatedAt=0))
        self.assertEqual(response.status_code, 409)
        # item create
        response = client.post('/api/item', dict(**item_params, teamSecretUpdatedAt=team_secret_updated_at))
        self.assertEqual(response.status_code, 201)
        item = models.Item.objects.get(team=team.id)
        self.assertEqual(item.value, item_params['value'])
        self.assertEqual(response.json(), {'item': item.id})
        # item update
        item_params['value'] = 'smoke_item_value_2'
        response = client.post('/api/item', {
            'id': item.id,
            'value': item_params['value'], 
            'teamSecretUpdatedAt': team_secret_updated_at,
        })
        self.assertEqual(response.status_code, 204)
        item = models.Item.objects.get(team=team.id)
        self.assertEqual(item.value, item_params['value'])
        self.assertEqual(item.notes, item_params['notes'])
        # items view
        response = client.get('/api/item', {
            'team': team.id,
            'teamSecretUpdatedAt': team_secret_updated_at,
        }).json()
        self.assertEqual(len(response), 1)
        self.assertEqual(response, {'items': [dict(**item_params, id=item.id)]})
        # user outside team cannot create, update, or view items
        adversary = SecureClient()
        adversary_password = 'mauowcieawjelacsddpqq'
        adversary.signup('smoke_adversary', adversary_password, 'smoke_adversary_salt', 'smoke_adversary_public_key', 'smoke_adversary_private_key')
        adversary.login(username='smoke_adversary', password=adversary_password)
        response = adversary.post('/item', {'value': item_params['value'], 'team': team.id})
        self.assertEqual(response.status_code, 404)
        response = adversary.post('/item', {'id': item.id, 'team': team.id})
        self.assertEqual(response.status_code, 404)
        response = adversary.post('/item', {'id': 999, 'team': team.id})
        self.assertEqual(response.status_code, 404)
        response = adversary.get('/item', {'team': team.id})
        self.assertEqual(response.status_code, 404)
        # invite fails without verification
        invitee_team_secret = '"smoke_invitee_team_secret"'
        invitee_client = SecureClient()
        response = invitee_client.signup('smoke_invitee', 'pmqxilassjkcwqvoo', 'smoke_invitee_salt', 'smoke_invitee_public_key', 'smoke_invitee_private_key')
        invitee = User.objects.get(username='smoke_invitee')
        invite_args = lambda verification_value: {
            'username': invitee.username,
            'team': team.id,
            'verificationValue': verification_value,
            'teamSecret': invitee_team_secret,
        }
        response = client.post('/api/invite', invite_args('wrong'))
        self.assertEqual(response.status_code, 409)
        # verify
        response = client.post('/api/verify', {'username': invitee.username, 'team': team.id})
        self.assertEqual(response.status_code, 201)
        verification_value = invitee_client.get('/api/verification_values').json()['values'][0]
        # adversary cannot verify
        response = adversary.post('/api/verify', {'username': invitee.username, 'team': team.id})
        self.assertEqual(response.status_code, 404)
        # invite fails with wrong verification
        response = client.post('/api/invite', invite_args('wrong'))
        self.assertEqual(response.status_code, 409)
        # invite
        response = client.get('/api/public_key', {'username': invitee.username}).json()
        self.assertEqual(response, {'publicKey': 'smoke_invitee_public_key'})
        response = client.post('/api/invite', invite_args(verification_value))
        self.assertEqual(response.status_code, 201)
        membership = models.Membership.objects.get(user=invitee, team=team)
        self.assertEqual(membership.admin, False)
        self.assertEqual(membership.team_secret, invitee_team_secret)
        # adversary cannot invite
        response = adversary.post('/api/invite', invite_args(verification_value))
        self.assertEqual(response.status_code, 404)
        # regular cannot verify
        response = invitee_client.post('/api/verify', {'username': invitee.username, 'team': team.id})
        self.assertEqual(response.status_code, 403)
        # regular cannot invite
        response = invitee_client.post('/api/invite', invite_args(verification_value))
        self.assertEqual(response.status_code, 403)
        # regular cannot rotate
        response = invitee_client.post('/api/rotate', {'team': team.id})
        self.assertEqual(response.status_code, 403)
        # adversary cannot rotate
        response = adversary.post('/api/rotate', {'team': team.id})
        self.assertEqual(response.status_code, 404)
        # regular cannot revoke
        response = invitee_client.post('/api/revoke', {'username': user.username, 'team': team.id})
        self.assertEqual(response.status_code, 403)
        # adversary cannot revoke
        response = adversary.post('/api/revoke', {'username': user.username, 'team': team.id})
        self.assertEqual(response.status_code, 404)
        # regular cannot get teammates' public keys
        response = invitee_client.get('/api/public_key', {'team': team.id})
        self.assertEqual(response.status_code, 403)
        # adversary cannot get teammates' public keys
        response = adversary.get('/api/public_key', {'team': team.id})
        self.assertEqual(response.status_code, 404)
        # revoke
        response = client.post('/api/revoke', {'username': invitee.username, 'team': team.id})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(models.Membership.objects.filter(user=invitee, team=team).count(), 0)
        # get teammates' public keys
        response = client.get('/api/public_key', { 'team': team.id })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'publicKeys': [{'userId': user.id, 'publicKey': public_key}]})
        # rotate
        admin_team_secret = '"smoke_team_secret_2"'
        response = client.post('/api/rotate', {
            'team': team.id,
            'teamSecrets': {user.id: admin_team_secret},
            'items': {item.id: {'value': 'rotated value', 'notes': 'rotated notes'}},
        })
        self.assertEqual(response.status_code, 204)
        self.assertEqual(models.Membership.objects.get(user=user, team=team).team_secret, admin_team_secret)
        item = models.Item.objects.get(id=item.id)
        self.assertEqual(item.value, 'rotated value')
        self.assertEqual(item.notes, 'rotated notes')
