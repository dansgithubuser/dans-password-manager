from . import models

from django.contrib.auth.models import User
from django.test import Client, TestCase

class SecureClient(Client):
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs, secure=True)

    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs, secure=True)

    def signup(self, username, password, public_key, private_key):
        return self.post('/signup', {
            'username': username,
            'password1': password,
            'password2': password,
            'public_key': public_key,
            'private_key': private_key,
        })

class SmokeTestCase(TestCase):
    def test_functional(self):
        # client create
        client = SecureClient()
        # signup
        username = 'smoke_username'
        password = 'acjlimwsjldkfjsldkj'
        public_key = 'smoke_public_key'
        private_key = 'smoke_private_key'
        response = client.signup(username, password, public_key, private_key)
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username=username)
        self.assertEqual(user.userinfo.public_key, public_key)
        self.assertEqual(user.userinfo.private_key, private_key)
        # client login
        client.login(username=username, password=password)
        # team create
        team_name = 'smoke_team_name'
        admin_team_secret = 'smoke_team_secret'
        response = client.post('/team', {'name': team_name, 'teamSecret': admin_team_secret})
        self.assertEqual(response.status_code, 201)
        team = models.Team.objects.get(name=team_name)
        membership = models.Membership.objects.get(user=user, team=team)
        self.assertEqual(membership.admin, True)
        self.assertEqual(membership.team_secret, admin_team_secret)
        # teams view
        response = client.get('/team').json()
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['name'], team_name)
        # item create
        item_value = 'smoke_item_value'
        response = client.post('/item', {'value': item_value, 'team': team.id})
        self.assertEqual(response.status_code, 201)
        item = models.Item.objects.get(team=team.id)
        self.assertEqual(item.value, item_value)
        self.assertEqual(response.json(), item.id)
        # item update
        item_value = 'smoke_item_value_2'
        response = client.post('/item', {'id': item.id, 'value': item_value})
        self.assertEqual(response.status_code, 204)
        item = models.Item.objects.get(team=team.id)
        self.assertEqual(item.value, item_value)
        # items view
        response = client.get('/item', {'team': team.id}).json()
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['value'], item_value)
        # user outside team cannot create, update, or view items
        adversary = SecureClient()
        adversary_password = 'mauowcieawjelacsddpqq'
        adversary.signup('smoke_adversary', adversary_password, 'smoke_adversary_public_key', 'smoke_adversary_private_key')
        adversary.login(username='smoke_adversary', password=adversary_password)
        response = adversary.post('/item', {'value': item_value, 'team': team.id})
        self.assertEqual(response.status_code, 404)
        response = adversary.post('/item', {'id': item.id, 'team': team.id})
        self.assertEqual(response.status_code, 404)
        response = adversary.post('/item', {'id': 999, 'team': team.id})
        self.assertEqual(response.status_code, 404)
        response = adversary.get('/item', {'team': team.id})
        self.assertEqual(response.status_code, 404)
        # invite fails without verification
        invitee_team_secret = 'smoke_invitee_team_secret'
        invitee_client = SecureClient()
        response = invitee_client.signup('smoke_invitee', 'pmqxilassjkcwqvoo', 'smoke_invitee_public_key', 'smoke_invitee_private_key')
        invitee = User.objects.get(username='smoke_invitee')
        invite_args = lambda verification_value: {
            'user': invitee.id,
            'team': team.id,
            'verificationValue': verification_value,
            'teamSecret': invitee_team_secret,
        }
        response = client.post('/invite', invite_args('wrong'))
        self.assertEqual(response.status_code, 409)
        # verify
        response = client.post('/verify', {'user': invitee.id, 'team': team.id})
        self.assertEqual(response.status_code, 201)
        verification_value = response.json()
        # adversary cannot verify
        response = adversary.post('/verify', {'user': invitee.id, 'team': team.id})
        self.assertEqual(response.status_code, 404)
        # invite fails with wrong verification
        response = client.post('/invite', invite_args('wrong'))
        self.assertEqual(response.status_code, 409)
        # invite
        response = client.get('/public_key', {'user': invitee.id}).json()
        self.assertEqual(response, 'smoke_invitee_public_key')
        response = client.post('/invite', invite_args(verification_value))
        self.assertEqual(response.status_code, 201)
        membership = models.Membership.objects.get(user=invitee, team=team)
        self.assertEqual(membership.admin, False)
        self.assertEqual(membership.team_secret, invitee_team_secret)
        # adversary cannot invite
        response = adversary.post('/invite', invite_args(verification_value))
        self.assertEqual(response.status_code, 404)
        # regular cannot verify
        response = invitee_client.post('/verify', {'user': invitee.id, 'team': team.id})
        self.assertEqual(response.status_code, 403)
        # regular cannot invite
        response = invitee_client.post('/invite', invite_args(verification_value))
        self.assertEqual(response.status_code, 403)
        # regular cannot revoke
        response = invitee_client.post('/revoke', {'user': user.id, 'team': team.id})
        self.assertEqual(response.status_code, 403)
        # adversary cannot revoke
        response = adversary.post('/revoke', {'user': user.id, 'team': team.id})
        self.assertEqual(response.status_code, 404)
        # revoke
        response = client.post('/revoke', {'user': invitee.id, 'team': team.id})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(models.Membership.objects.filter(user=invitee, team=team).count(), 0)
