from django.contrib.auth import login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.forms import modelform_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from users.forms import LoginForm, UserForm
from users.models import User, Role


class IndexView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View for user administration"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    template = 'users/index.html'

    def get(self, request, page_num=1):
        """Render administration page"""
        user_pages = Paginator(User.objects.filter(is_deleted=False).order_by('id'), 20)
        user_list = user_pages.get_page(page_num)
        return render(request, self.template, {'user_list': user_list})

    def test_func(self):
        """Check if user is moderator"""
        return self.request.user.moderator


class SignInView(UserPassesTestMixin, View):
    """View for signing in"""
    login_form = LoginForm
    template = 'users/login.html'

    def get(self, request):
        """Render login view for user"""
        return render(request, self.template, {'form': self.login_form(), 'redirect': request.GET.get('redirect')})

    def post(self, request):
        """Log user in or display errors"""
        form = self.login_form(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return HttpResponseRedirect(request.POST.get('redirect', default=reverse('CRM:index')))
        return render(request, self.template, {'title': 'Sign in', 'form': form})

    def test_func(self):
        """Check if user is logged in"""
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('users:detail'))


class SignUpView(UserPassesTestMixin, View):
    """View for registering user"""
    register_form = modelform_factory(User, form=UserForm, exclude=('role_id', 'id', 'is_deleted'))
    template = 'form.html'

    def get(self, request):
        """Render register view for user"""
        return render(request, self.template, {'title': 'Sign up', 'form': self.register_form()})

    def post(self, request):
        """Register user or display error"""
        form = self.register_form(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role_id = Role.objects.get(pk=1)
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('CRM:index'))
        return render(request, self.template, {'title': 'Sign up', 'form': form})

    def test_func(self):
        """Check if user is logged in"""
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('users:detail'))


def sign_out(request):
    """Handling user signing out"""
    logout(request)
    return HttpResponseRedirect(reverse('users:login'))


class DetailView(LoginRequiredMixin, View):
    """View account detail and change it"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    change_form = modelform_factory(User, form=UserForm, exclude=('password', 'role_id', 'id', 'is_deleted'))
    admin_change_form = modelform_factory(User, form=UserForm, exclude=('password', 'id', 'is_deleted'))
    template = 'users/detail.html'

    def get(self, request, user_id=None):
        user = request.user
        form = self.change_form
        if user_id and user.moderator:
            user = User.objects.get(pk=user_id)
            if request.user.admin:
                form = self.admin_change_form
        return render(request, self.template, {'form': form(instance=user), 'admin': user_id})

    def post(self, request, user_id=None):
        user = request.user
        form = self.change_form
        if user_id and user.moderator:
            user = User.objects.get(pk=user_id)
            if request.user.admin:
                form = self.admin_change_form
        form = form(request.POST, instance=user)
        if form.is_valid():
            form.save()
            if user_id and request.user.moderator:
                return HttpResponseRedirect(reverse('users:index'))
        return render(request, self.template, {'form': form, 'user_id': user_id})

    @staticmethod
    def delete(request, user_id):
        user = User.objects.get(pk=user_id)
        if request.user.admin or request.user == user or (request.user.moderator and not user.moderator):
            user.is_deleted = True
            user.save()
            if request.user == user:
                logout(request)
            return HttpResponse('{"status": "Success"}', status=200)
        return HttpResponseForbidden('{"status": "Forbidden"}')


class PasswordChangeView(LoginRequiredMixin, View):
    """View for password change"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    change_form = PasswordChangeForm
    template = 'form.html'

    def get(self, request):
        return render(request, self.template, {'title': 'Password', 'form': self.change_form(request.user)})

    def post(self, request):
        form = self.change_form(data=request.POST, user=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            if user == request.user:
                user.save()
                login(request, user)
            return HttpResponseRedirect(reverse('users:detail'))
        return render(request, self.template, {'title': 'Password', 'form': form})
