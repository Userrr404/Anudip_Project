from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Job

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['company_name', 'role_required', 'address', 'description', 'salary', 'experience', 'skills_required', 'category']