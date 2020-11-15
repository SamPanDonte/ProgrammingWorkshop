from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.forms import TextInput, PasswordInput, ModelForm, Form, DateInput, CharField

from users.models import User


class AdminUserForm(ModelForm):
    """Form for administrating users"""
    class Meta:
        model = User
        exclude = ('password', 'last_login')
        widgets = {
            'login': TextInput(attrs={'placeholder': 'Login'}),
            'password': PasswordInput(attrs={'placeholder': 'Password'}),
            'name': TextInput(attrs={'placeholder': 'Name'}),
            'surname': TextInput(attrs={'placeholder': 'Surname'}),
            'date_of_birth': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }


class UserForm(AdminUserForm):
    """Form for registering and editing user"""
    class Meta(AdminUserForm.Meta):
        exclude = ('role_id', 'id', 'is_deleted', 'last_login')


class LoginForm(Form):
    """Form for users to logging in"""
    login = CharField(max_length=30, widget=TextInput(attrs={'placeholder': 'Login'}))
    password = CharField(max_length=64, widget=PasswordInput(attrs={'placeholder': 'Password'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        login = cleaned_data.get('login')
        print(login, password)

        if password and login:
            user = authenticate(login=login, password=password)
            if not user:
                raise ValidationError('Login or password not correct.')
            if user.is_deleted:
                raise ValidationError('This account has been deleted.')
            cleaned_data['user'] = user
        return cleaned_data
