from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:page_num>', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('login/', views.login1, name='login'),
    path('register/', views.register_frontend, name='register'),
    path('login_backend/', views.login_backend, name='login_backend'),
    path('logout/', views.logout1, name='logout'),
]
