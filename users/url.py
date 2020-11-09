from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:page_num>', views.index, name='index'),
    path('login/', views.sign_in, name='login'),
    path('register/', views.sign_up, name='register'),
    path('logout/', views.sign_out, name='logout'),
    path('detail/', views.detail, name='detail'),
]
