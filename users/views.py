from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse

from users.models import User


def index(request, page_num=1):
    """User administration page"""
    user: User = request.user
    # User isn't logged in
    if not user.is_authenticated:
        return render(request, 'users/login.html')
    # User is an administrator
    if user.is_super_user():
        user_pages = Paginator(User.objects.filter(is_deleted=False).order_by('id').all(), 20)
        page = user_pages.get_page(page_num)
        if not page:
            raise Http404("Page does not exists")
        return render(request, 'users/index.html', {'user_list': page, 'user': user, 'title': 'Administration'})
    # User is regular user
    return HttpResponseRedirect(reverse('users:detail'))


def sign_in(request):
    """Handling user signing in"""
    user: User = request.user
    # User has sign in earlier
    if user.is_authenticated:
        return HttpResponseRedirect(reverse('users:index'))
    # User passed credentials
    if request.method == 'POST':
        try:
            signed_in_user = authenticate(request, login=request.POST['login'], password=request.POST['password'])
            if signed_in_user and signed_in_user.is_deleted:
                signed_in_user = None
        except KeyError:
            return render(request, 'users/login.html', {'error': 'Unknown error try again.', 'title': 'Sign in'})
        if signed_in_user:
            login(request, signed_in_user)
            return HttpResponseRedirect(reverse('users:index'))
        else:
            return render(request, 'users/login.html', {'error': 'Wrong login or password!', 'title': 'Sign in'})
    # User need to pass credentials
    return render(request, 'users/login.html', {'title': 'Sign in'})


def sign_up(request):
    """Handling user signing up"""""
    # User passed data
    if request.method == 'POST':
        try:
            new_user = User.objects.create_user(request.POST['login'], request.POST['name'], request.POST['surname'],
                                                request.POST['date_of_birth'], request.POST['password'])
        except KeyError:
            return render(request, 'users/register.html', {'error': 'Unknown error try again.', 'title': 'Sign up'})
        except IntegrityError:
            return render(request, 'users/register.html', {'error': 'Login occupied!', 'title': 'Sign up'})
        if not new_user:
            return render(request, 'users/register.html', {'error': 'Unknown error try again.', 'title': 'Sign up'})
        login(request, new_user)
        return HttpResponseRedirect(reverse('users:index'))
    # User need to pass data
    return render(request, 'users/register.html', {'title': 'Sign up'})


def sign_out(request):
    """Handling user signing out"""
    logout(request)
    return HttpResponseRedirect(reverse('users:index'))


def detail(request):
    """User account detail info and making changes"""
    user: User = request.user
    # If user not logged in send him login page
    if not user.is_authenticated:
        return render(request, 'users/login.html', {'title': 'Sign in'})
    # User send something to change or superuser is changing something
    if request.method == 'POST':
        # Check if valid request
        try:
            target_user = request.POST['account']
        except KeyError:
            return render(request, 'users/detail.html', {'user': user, 'title': 'Account'})
        target_user = User.objects.get(login=target_user)
        if not target_user:
            return HttpResponseRedirect(reverse('users:index'))
        # Check if user have privileges to see this page
        if not target_user.login == user.login and not user.is_super_user():
            return HttpResponseForbidden()
        # Delete account
        if 'delete' in request.POST.keys():
            target_user.is_deleted = True
            target_user.save()
            if target_user.login == user.login:
                logout(request)
            return HttpResponseRedirect(reverse('users:index'))
        # Change account data
        if 'save' in request.POST.keys():
            try:
                target_user.login = request.POST['login']
                target_user.set_password(request.POST['password'])
                target_user.name = request.POST['name']
                target_user.surname = request.POST['surname']
                target_user.date_of_birth = request.POST['date_of_birth']
                if user.is_super_user():
                    pass
                    # target_user.role_id = request.POST['date_of_birth']
                target_user.save()
            except KeyError:
                return render(request, 'users/detail.html', {'user': user, 'title': 'Account'})
        return render(request, 'users/detail.html',
                      {'user': target_user, 'title': 'Account', 'admin': user.is_super_user()})
    return render(request, 'users/detail.html', {'user': user, 'title': 'Account', 'admin': user.is_super_user()})
