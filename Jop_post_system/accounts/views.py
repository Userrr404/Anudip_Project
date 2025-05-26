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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Important: keep user logged in
            return redirect('user_profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


from django.db.models import Q
from django.utils.dateparse import parse_date

def home_view(request):
    # Get filter parameters from GET request
    selected_category = request.GET.get('category', '')
    search_query = request.GET.get('search', '').strip()

    # New filters
    company_name = request.GET.get('company_name', '').strip()
    role = request.GET.get('role', '').strip()
    posted_before = request.GET.get('posted_before', '').strip()
    # skill = request.GET.get('skill', '').strip()
    experience = request.GET.get('experience', '').strip()
    min_salary = request.GET.get('min_salary', '').strip()
    max_salary = request.GET.get('max_salary', '').strip()

    jobs = Job.objects.all().order_by('-posted_at')

    # Filter by category if provided
    if selected_category:
        jobs = jobs.filter(category=selected_category)

    # Search by general search bar (company or role)
    if search_query:
        jobs = jobs.filter(
            Q(company_name__icontains=search_query) |
            Q(role_required__icontains=search_query)
        )

    # Filter by company_name
    if company_name:
        jobs = jobs.filter(company_name__icontains=company_name)

    # Filter by role
    if role:
        jobs = jobs.filter(role_required__icontains=role)

    # Filter by posted_before date
    if posted_before:
        date_obj = parse_date(posted_before)
        if date_obj:
            jobs = jobs.filter(posted_at__lte=date_obj)

    # # Filter by skill (assuming 'skills' is a CharField or TextField)
    # if skill:
    #     jobs = jobs.filter(skills__icontains=skill)

    # Filter by experience (assuming experience is numeric field in years)
    if experience.isdigit():
        jobs = jobs.filter(experience__gte=int(experience))

    # Filter by salary (assuming salary is numeric field)
    if min_salary.isdigit():
        jobs = jobs.filter(salary__gte=int(min_salary))
    if max_salary.isdigit():
        jobs = jobs.filter(salary__lte=int(max_salary))

    # Featured job - pick the latest posted job as featured (or any logic you want)
    featured_job = Job.objects.order_by('-posted_at').first()

    category_choices = Job.CATEGORY_CHOICES

    context = {
        'jobs': jobs,
        'featured_job': featured_job,
        'category_choices': category_choices,
        'selected_category': selected_category,
        'search_query': search_query,
        # New filters to persist form values
        'company_name': company_name,
        'role': role,
        'posted_before': posted_before,
        # 'skill': skill,
        'experience': experience,
        'min_salary': min_salary,
        'max_salary': max_salary,
    }
    return render(request, 'accounts/home.html', context)


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
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        return redirect('user_profile')  # ✅ fixed

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
