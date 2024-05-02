import os

from django.urls import path

from myproject.settings import BASE_DIR
from . import views

urlpatterns = [
    path('Login', views.Login, name='Login'),
    path('Auth/Registration', views.Registration, name='Registration'),
    path('Auth/Logout', views.Logout, name='Logout'),

    path('Main', views.Main, name='Main'),
    path('About', views.About, name='About'),
    path('Library', views.Library, name='Library'),
    path('Search', views.FindWork, name='Search'),
    path('Edit', views.EditWork, name='Edit'),

    path('Plan', views.Plan, name='Plan'),
    path('PlanRegister', views.PlanRegister, name='PlanRegister'),
    path('PlanProject', views.Project, name='PlanProject'),

    path('stream/', views.sse_stream, name='sse_stream'),
    path('TEST', views.SSE, name='TEST'),
    path('WS', views.WS, name='WS'),
    #path('api/create_project', api.create_project, name="create_project_api")
]
