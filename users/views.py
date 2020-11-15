from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from users.forms import LoginForm, UserForm, AdminUserForm
from users.models import User, Role


class IndexView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View for user administration"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    change_form_set = modelformset_factory(User, form=AdminUserForm, extra=0)
    template = 'users/index.html'

    def get(self, request, page_num=1):
        """Render administration page"""
        user_pages = Paginator(User.objects.filter(is_deleted=False).order_by('id').all(), 15)
        page = user_pages.get_page(page_num)
        form_set = self.change_form_set(queryset=page.object_list)
        return render(request, self.template, {'user_list': page, 'title': 'Admin', 'form_set': form_set})

    def post(self, request, page_num=1):
        """Save changes"""
        form_set = self.change_form_set(request.POST)
        if form_set.is_valid():
            form_set.save()
        return self.get(request, page_num)

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
    register_form = UserForm
    template = 'users/register.html'

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
    """Class for viewing account detail"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    change_form = None
    template = 'users/detail.html'

    def get(self, request):
        return render(request, self.template, {'title': 'Account', 'form': self.change_form()})

    def post(self, request):
        pass  # TODO


def detail(request):  # TODO
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
