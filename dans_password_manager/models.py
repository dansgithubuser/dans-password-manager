from django.db import models
from django.contrib.auth.models import User

class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    salt = models.TextField()
    salt2 = models.TextField()
    public_key = models.TextField()
    private_key = models.TextField()

class Team(models.Model):
    name = models.TextField()
    users = models.ManyToManyField(User, through='Membership')

class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    team_secret = models.TextField()
    admin = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

class Item(models.Model):
    name = models.TextField()
    target = models.TextField()
    user = models.TextField()
    value = models.TextField()
    notes = models.TextField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

class Verification(models.Model):
    value = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
