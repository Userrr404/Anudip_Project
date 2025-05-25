from django.urls import path
from . import views
from .views import admin_profile_view

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'),
    path('post-job/', views.post_job_view, name='post_job'),
    path('job/<int:job_id>/', views.job_detail_view, name='job_detail'),
    path('admin_profile/', admin_profile_view, name='admin_profile'),
    path('profile/', views.user_profile, name='user_profile'),
]
