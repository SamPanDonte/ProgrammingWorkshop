from django.contrib.auth import login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.forms import modelform_factory
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
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
        user_pages = Paginator(User.objects.filter(is_deleted=False).order_by('id').all(), 15)
        page = user_pages.get_page(page_num)
        return render(request, self.template, {'user_list': page, 'title': 'Admin', 'page': page})

    def test_func(self):
        """Check if user is superuser"""
        return self.request.user.is_moderator()


class SignInView(View):
    """View for signing in"""
    login_form = LoginForm
    template = 'users/login.html'

    def get(self, request):
        """Render login view for user"""
        if request.user.is_authenticated:
            return HttpResponseRedirect(request.GET.get('redirect', default=reverse('users:detail')))
        context = {'title': 'Sign in', 'form': self.login_form(), 'redirect': request.GET.get('redirect')}
        return render(request, self.template, context)

    def post(self, request):
        """Log user in or display errors"""
        if request.user.is_authenticated:
            return HttpResponseRedirect(request.POST.get('redirect', default=reverse('users:detail')))
        form = self.login_form(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return HttpResponseRedirect(request.POST.get('redirect', default=reverse('users:detail')))
        return render(request, self.template, {'title': 'Sign in', 'form': form})


class SignUpView(View):
    """View for registering user"""
    register_form = modelform_factory(User, form=UserForm, exclude=('role_id', 'id', 'is_deleted'))
    template = 'users/form.html'

    def get(self, request):
        """Render register view for user"""
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('users:detail'))
        return render(request, self.template, {'title': 'Sign up', 'form': self.register_form()})

    def post(self, request):
        """Register user or display error"""
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('users:detail'))
        form = self.register_form(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role_id = Role.objects.get(pk=1)
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('users:detail'))
        return render(request, self.template, {'title': 'Sign up', 'form': form})


def sign_out(request):
    """Handling user signing out"""
    logout(request)
    return HttpResponseRedirect(reverse('users:index'))


class DetailView(LoginRequiredMixin, View):
    """View account detail and change it"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    change_form = modelform_factory(User, form=UserForm, exclude=('password', 'role_id', 'id', 'is_deleted'))
    admin_change_form = modelform_factory(User, form=UserForm, exclude=('password', 'id', 'is_deleted'))
    template = 'users/detail.html'

    def get(self, request, user_id=None):
        user = request.user
        if user_id:
            if not user.is_moderator():
                return HttpResponseForbidden()
            user = User.objects.get(pk=user_id)
            if request.user.is_super_user():
                return render(request, self.template, {'title': 'Account', 'form': self.admin_change_form(instance=user), 'user_id': user_id})
        return render(request, self.template, {'title': 'Account', 'form': self.change_form(instance=user), 'user_id': user_id})

    def post(self, request, user_id=None):
        user = request.user
        if user_id:
            if not user.is_moderator():
                return HttpResponseForbidden()
            user = User.objects.get(pk=user_id)
            form = self.admin_change_form(request.POST, instance=user) if request.user.is_super_user() else self.change_form(request.POST, instance=user)
        else:
            form = self.change_form(request.POST, instance=user)
        if form.is_valid():
            form.save()
        else:
            return render(request, self.template, {'title': 'Account', 'form': form, 'user_id': user_id})
        if user_id:
            return HttpResponseRedirect(reverse('users:index'))
        return self.get(request, user_id)

    def delete(self, request, user_id):
        user = User.objects.get(pk=user_id)
        user.is_deleted = True
        if request.user.is_super_user() or request.user == user or (request.user.is_moderator() and not user.is_moderator()):
            user.save()
            if request.user == user:
                logout(request)
            return HttpResponse(status=200)
        return HttpResponse(status=403)


class PasswordChangeView(LoginRequiredMixin, View):
    """View for password change"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    change_form = PasswordChangeForm
    template = 'users/form.html'

    def get(self, request):
        return render(request, self.template, {'form': self.change_form(request.user)})

    def post(self, request):
        form = self.change_form(data=request.POST, user=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            if request.user.is_moderator() or user == request.user:
                user.save()
                login(request, user)
            return HttpResponseRedirect(reverse('users:detail'))
        return render(request, self.template, {'form': form})
