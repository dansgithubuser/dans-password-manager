from . import views

from django.contrib.auth import views as auth_views
from django.urls import path

import inspect

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html')),
]

for name, value in inspect.getmembers(views):
    if getattr(value, '__module__', None) != 'dans_password_manager.views': continue
    if not inspect.isfunction(value): continue
    if name.startswith('_'): continue
    urlpatterns.append(path(name, value))
