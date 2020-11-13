from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from users.forms import LoginForm, RegisterForm, ChangeUserForm
from users.models import User


class IndexView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View for user administration"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    change_form = ChangeUserForm
    template = 'users/index.html'

    def get(self, request, page_num=1):
        """Render administration page"""
        user_pages = Paginator(User.objects.filter(is_deleted=False).order_by('id').all(), 20)
        page = user_pages.get_page(page_num)
        if not page:
            raise Http404("Page does not exists")
        return render(request, self.template, {'user_list': page, 'title': 'Administration'})

    def test_func(self):
        """Check if user is superuser"""
        return self.request.user.is_super_user()


class SignInView(View):
    """View for signing in"""
    login_form = LoginForm
    template = 'users/login.html'

    def get(self, request):
        """Render login view for user"""
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('users:index'))
        context = {'title': 'Sign in', 'form': self.login_form(), 'redirect': request.GET.get('redirect')}
        return render(request, self.template, context)

    def post(self, request):
        """Log user in or display errors"""
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('users:index'))
        form = self.login_form(request.POST)
        if form.is_valid():
            user = authenticate(request, login=form.cleaned_data['login'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return HttpResponseRedirect(request.POST.get('redirect', default=reverse('users:detail')))
            messages.error(request, 'username or password not correct')
        return render(request, self.template, {'title': 'Sign in', 'form': form})


class SignUpView(View):
    """View for registering user"""
    register_form = RegisterForm
    template = 'users/register.html'

    def get(self, request):
        """Render register view for user"""
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('users:index'))
        return render(request, self.template, {'title': 'Sign up', 'form': self.register_form()})

    def post(self, request):
        """Register user or display error"""
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('users:index'))
        form = self.register_form(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(form.cleaned_data['login'], form.cleaned_data['name'],
                                                form.cleaned_data['surname'], form.cleaned_data['date_of_birth'],
                                                form.cleaned_data['password'])
            except IntegrityError:
                messages.error(request, 'username occupied')
                user = None
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('users:index'))
        return render(request, self.template, {'title': 'Sign up', 'form': form})


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
