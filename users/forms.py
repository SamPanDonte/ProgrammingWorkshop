from django import forms


class LoginForm(forms.Form):
    """Form for users to logging in"""
    login = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Login'}))
    password = forms.CharField(max_length=64, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class RegisterForm(forms.Form):
    """Form for users to register"""
    login = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Login'}))
    password = forms.CharField(max_length=64, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    surname = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Surname'}))
    date_of_birth = forms.DateField(widget=forms.DateTimeInput(attrs={'type': 'date'}))


class ChangeUserForm(RegisterForm):
    """Form for users to change their user data"""
    # todo
