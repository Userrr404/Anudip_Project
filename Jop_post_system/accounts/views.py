from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import JobForm, SignUpForm
from .models import Job
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.conf import settings
import os

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

from django.core.mail import EmailMessage
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponse
import os

def job_detail_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        resume_file = request.FILES.get('resume')
        if not resume_file:
            return render(request, 'accounts/job_details.html', {'job': job, 'error': 'Resume is required.'})

        # Ensure it's a PDF
        if not resume_file.name.endswith('.pdf'):
            return render(request, 'accounts/job_details.html', {'job': job, 'error': 'Only PDF files are allowed.'})

        # Save resume temporarily
        file_path = default_storage.save(resume_file.name, resume_file)
        absolute_file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        try:
            # Construct email
            subject = f"Job Application from {request.user.username} for {job.role_required}"
            message = (
                f"Dear {job.company_name},\n\n"
                f"{request.user.username} is interested in the position of {job.role_required}.\n"
                f"Experience: {job.experience} years\n\n"
                f"Please find the attached resume.\n\n"
                f"Regards,\n"
                f"{request.user.username} ({request.user.email})"
            )

            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [job.company_email]
            )
            email.attach_file(absolute_file_path)
            email.send()

            # Delete file after sending
            default_storage.delete(file_path)

            return render(request, 'accounts/job_details.html', {'job': job, 'success': 'Application sent successfully.'})

        except Exception as e:
            return render(request, 'accounts/job_details.html', {'job': job, 'error': f'Error sending email: {str(e)}'})

    return render(request, 'accounts/job_details.html', {'job': job})
