from . import models

from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
import random

@csrf_exempt
def signup(request):
    form = UserCreationForm(request.POST)
    if not form.is_valid():
        return JsonResponse(form.errors, status=400)
    form.save()
    username = form.cleaned_data.get('username')
    raw_password = form.cleaned_data.get('password1')
    user = auth.authenticate(username=username, password=raw_password)
    user.userinfo = models.UserInfo.objects.create(
        user=user,
        salt=request.POST['salt'],
        salt2=request.POST['salt2'],
        public_key=request.POST['publicKey'],
        private_key=request.POST['privateKey'],
    )
    auth.login(request, user)
    return HttpResponse(status=201)

def salts(request):
    user = User.objects.get(username=request.GET['username'])
    return JsonResponse({
        'salt': json.loads(user.userinfo.salt),
        'salt2': json.loads(user.userinfo.salt2),
    }, status=200)

@csrf_exempt
def login(request):
    params = json.loads(request.body.decode())
    user = auth.authenticate(
        username=params['username'],
        password=params['password'],
    )
    if user:
        auth.login(request, user)
        return JsonResponse({
            'publicKey': user.userinfo.public_key,
            'privateKey': json.loads(user.userinfo.private_key),
        }, status=200)
    else:
        return HttpResponse(status=400)

def team(request):
    if request.method == 'POST':
        params = json.loads(request.body.decode())
        team = models.Team.objects.create(name=params['name'])
        models.Membership.objects.create(
            user=request.user,
            team=team,
            team_secret=params['teamSecret'],
            admin=True,
        )
        return HttpResponse(status=201)
    else:
        return JsonResponse({'teams': [
            {
                'id': i.team.id,
                'name': i.team.name,
                'secret': json.loads(i.team_secret),
                'secretUpdatedAt': i.updated_at.timestamp(),
                'admin': i.admin,
            }
            for i in request.user.membership_set.select_related('team')
        ]})

def item(request):
    if request.method == 'POST':
        params = json.loads(request.body.decode())
    else:
        params = {
            k: (v if k != 'teamSecretUpdatedAt' else float(v))
            for k, v in request.GET.items()
        }
    # check user is a member of team
    if 'id' in params:
        items = models.Item.objects.filter(id=params['id'])
        if not items: return HttpResponse(status=404)
        team_id = items[0].team_id
    else:
        team_id = params['team']
    membership = models.Membership.objects.filter(user=request.user, team_id=team_id)
    if not membership: return HttpResponse(status=404)
    # check if user's team secret is up-to-date
    if 'teamSecretUpdatedAt' in params:
        if params['teamSecretUpdatedAt'] < membership[0].updated_at.timestamp():
            return HttpResponse(status=409)
    # action
    if request.method == 'POST':
        if 'id' in params:
            models.Item.objects.filter(id=params['id']).update(
                **{i: params[i] for i in ['name', 'target', 'user', 'value', 'notes'] if i in params}
            )
            return HttpResponse(status=204)
        else:
            item = models.Item.objects.create(
                **{i: params[i] for i in ['name', 'target', 'user', 'value', 'notes']},
                team_id=team_id,
            )
            return JsonResponse({'item': item.id}, status=201)
    else:
        return JsonResponse({'items': [
            {
                'id': i.id,
                'name': i.name,
                'target': i.target,
                'user': i.user,
                'value': i.value,
                'notes': i.notes,
                'team': i.team_id,
            }
            for i in models.Item.objects.filter(team_id=team_id).order_by('id')
        ]})

def verify(request):
    params = json.loads(request.body.decode())
    membership = models.Membership.objects.filter(user=request.user, team_id=params['team'])
    if membership.count() != 1:
        return HttpResponse(status=404)
    if not membership[0].admin:
        return HttpResponse(status=403)
    invitee = User.objects.get(username=params['username'])
    value = str(random.randint(100000, 999999))
    models.Verification.objects.create(
        value=value,
        user=invitee,
        team_id=params['team'],
    )
    return HttpResponse(status=201)

def verification_values(request):
    return JsonResponse(
        {'values': [i.value for i in models.Verification.objects.filter(user=request.user)]},
        status=200,
    )

def public_key(request):
    if 'username' in request.GET:
        user = User.objects.get(username=request.GET['username'])
        info = models.UserInfo.objects.get(user=user)
        return JsonResponse({'publicKey': info.public_key})
    membership = models.Membership.objects.filter(user=request.user, team_id=request.GET['team'])
    if membership.count() != 1:
        return HttpResponse(status=404)
    if not membership[0].admin:
        return HttpResponse(status=403)
    team = models.Team.objects.get(id=request.GET['team'])
    teammates = team.users.select_related('userinfo').all()
    return JsonResponse({'publicKeys': [
        {
            'userId': i.id,
            'publicKey': i.userinfo.public_key,
        }
        for i in teammates
    ]})

def invite(request):
    params = json.loads(request.body.decode())
    membership = models.Membership.objects.filter(user=request.user, team_id=params['team'])
    if membership.count() != 1:
        return HttpResponse(status=404)
    if not membership[0].admin:
        return HttpResponse(status=403)
    invitee = User.objects.get(username=params['username'])
    verifications = models.Verification.objects.filter(user=invitee, team_id=params['team'])
    if params['verificationValue'] not in [i.value for i in verifications]:
        return HttpResponse('verification failure', status=409)
    verifications.delete()
    models.Membership.objects.create(
        user=invitee,
        team_id=params['team'],
        team_secret=params['teamSecret'],
    )
    return HttpResponse(status=201)

def revoke(request):
    params = json.loads(request.body.decode())
    membership = models.Membership.objects.filter(user=request.user, team_id=params['team'])
    if membership.count() != 1:
        return HttpResponse(status=404)
    if not membership[0].admin:
        return HttpResponse(status=403)
    revokee = User.objects.get(username=params['username'])
    models.Membership.objects.filter(
        user=revokee,
        team_id=params['team'],
    ).delete()
    return HttpResponse(status=204)

def rotate(request):
    params = json.loads(request.body.decode())
    membership = models.Membership.objects.filter(user=request.user, team_id=params['team'])
    if membership.count() != 1:
        return HttpResponse(status=404)
    if not membership[0].admin:
        return HttpResponse(status=403)
    team = models.Team.objects.get(id=params['team'])
    with transaction.atomic():
        for user in team.users.all():
            models.Membership.objects.filter(user=user, team=team).update(
                team_secret=params['teamSecrets'][str(user.id)]
            )
        for item in team.item_set.all():
            item_params = params['items'][str(item.id)]
            models.Item.objects.filter(id=item.id).update(
                user =item_params['user' ],
                value=item_params['value'],
                notes=item_params['notes'],
            )
    return HttpResponse(status=204)
