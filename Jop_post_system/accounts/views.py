from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import JobForm, SignUpForm
from .models import Job

from django.contrib.admin.views.decorators import staff_member_required

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # hash password
            user.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def home_view(request):
    jobs = Job.objects.all()
    return render(request, 'accounts/home.html', {'jobs': jobs})

@login_required(login_url='login')  # Redirects unauthenticated users to login
def post_job_view(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            return redirect('home')
    else:
        form = JobForm()
    return render(request, 'accounts/post_job.html', {'form': form})

def job_detail_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'accounts/job_details.html', {'job': job})

@staff_member_required
def admin_profile_view(request):
    return render(request, 'accounts/admin_profile.html')

@login_required
def user_profile(request):
    return render(request, 'accounts/user_profile.html')

# Create your views here.
