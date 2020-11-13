from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('admin/', views.IndexView.as_view(), name='index'),
    path('admin/<int:page_num>', views.IndexView.as_view(), name='index'),
    path('login/', views.SignInView.as_view(), name='login'),
    path('register/', views.SignUpView.as_view(), name='register'),
    path('logout/', views.sign_out, name='logout'),
    path('detail/', views.detail, name='detail'),
]
