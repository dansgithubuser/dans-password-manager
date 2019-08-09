from . import models

from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
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
        public_key=request.POST['publicKey'],
    )
    auth.login(request, user)
    return HttpResponse(status=201)

def login(request):
    params = json.loads(request.body.decode())
    user = auth.authenticate(
        username=params['username'],
        password=params['password'],
    )
    if user:
        auth.login(request, user)
        return JsonResponse({'salt': user.userinfo.salt}, status=200)
    else:
        return HttpResponse(status=400)

def team(request):
    if request.method == 'POST':
        team = models.Team.objects.create(name=request.POST['name'])
        models.Membership.objects.create(
            user=request.user,
            team=team,
            team_secret=request.POST['teamSecret'],
            admin=True,
        )
        return HttpResponse(status=201)
    else:
        return JsonResponse([i for i in request.user.team_set.values()], safe=False)

def item(request):
    if request.method == 'POST':
        params = request.POST
    else:
        params = request.GET
    # check user is a member of team
    if 'id' in params:
        items = models.Item.objects.filter(id=request.POST['id'])
        if not items: return HttpResponse(status=404)
        team_id = items[0].team_id
    else:
        team_id = params['team']
    if models.Membership.objects.filter(user=request.user, team_id=team_id).count() != 1:
        return HttpResponse(status=404)
    # action
    if request.method == 'POST':
        if 'id' in request.POST:
            models.Item.objects.filter(id=request.POST['id']).update(value=request.POST['value'])
            return HttpResponse(status=204)
        else:
            item = models.Item.objects.create(value=request.POST['value'], team_id=team_id)
            return JsonResponse(item.id, status=201, safe=False)
    else:
        return JsonResponse([i for i in
            models.Item.objects.filter(team_id=team_id).values()
        ], safe=False)

def verify(request):
    membership = models.Membership.objects.filter(user=request.user, team_id=request.POST['team'])
    if membership.count() != 1:
        return HttpResponse(status=404)
    if not membership[0].admin:
        return HttpResponse(status=403)
    value = random.randint(100000, 999999)
    models.Verification.objects.create(
        value=value,
        user_id=request.POST['user'],
        team_id=request.POST['team'],
    )
    return JsonResponse(value, status=201, safe=False)

def public_key(request):
    info = models.UserInfo.objects.get(user_id=request.GET['user'])
    return JsonResponse(info.public_key, safe=False)

def invite(request):
    membership = models.Membership.objects.filter(user=request.user, team_id=request.POST['team'])
    if membership.count() != 1:
        return HttpResponse(status=404)
    if not membership[0].admin:
        return HttpResponse(status=403)
    verifications = models.Verification.objects.filter(user_id=request.POST['user'], team_id=request.POST['team'])
    if request.POST['verificationValue'] not in [i.value for i in verifications]:
        return HttpResponse('verification failure', status=409)
    verifications.delete()
    invitee = User.objects.get(id=request.POST['user'])
    models.Membership.objects.create(
        user=invitee,
        team_id=request.POST['team'],
        team_secret=request.POST['teamSecret'],
    )
    return HttpResponse(status=201)

def revoke(request):
    membership = models.Membership.objects.filter(user=request.user, team_id=request.POST['team'])
    if membership.count() != 1:
        return HttpResponse(status=404)
    if not membership[0].admin:
        return HttpResponse(status=403)
    models.Membership.objects.filter(
        user_id=request.POST['user'],
        team_id=request.POST['team'],
    ).delete()
    return HttpResponse(status=204)

def rotate(request):
    membership = models.Membership.objects.filter(user=request.user, team_id=request.POST['team'])
    if membership.count() != 1:
        return HttpResponse(status=404)
    if not membership[0].admin:
        return HttpResponse(status=403)
    models.Membership.objects.filter(
        user_id=request.POST['user'],
        team_id=request.POST['team'],
    ).update(team_secret=request.POST['teamSecret'])
    return HttpResponse(status=204)
