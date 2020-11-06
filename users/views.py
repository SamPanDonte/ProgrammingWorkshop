from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from users.models import User


def index(request, page_num=1):
    page = None
    if request.user.is_authenticated:
        user_pages = Paginator(User.objects.filter(is_deleted=False).order_by('id').all(), 25)
        page = user_pages.get_page(page_num)
        if not page:
            raise Http404("Page does not exists")
    context = {'user_list': page, 'user': request.user}
    return render(request, 'users/index.html', context)


def add(request):
    try:
        user = User.objects.create_user(request.POST['login'], request.POST['name'], request.POST['surname'],
                                        request.POST['date_of_birth'], request.POST['password'])
        request.user = user
    except KeyError:
        return render(request, 'users/register.html')
    else:
        return HttpResponseRedirect(reverse('users:index'))


def login1(request):
    return render(request, 'users/login.html')


def register_frontend(request):
    return render(request, 'users/register.html')


def login_backend(request):
    try:
        user = authenticate(login=request.POST['login'], password=request.POST['password'])
        if user:
            login(request, user)
        else:
            raise KeyError
    except KeyError:
        return render(request, 'users/login.html')
    else:
        return HttpResponseRedirect(reverse('users:index'))


def logout1(request):
    logout(request)
    return HttpResponseRedirect(reverse('users:index'))
