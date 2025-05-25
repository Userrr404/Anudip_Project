from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    CATEGORY_CHOICES = [
        ('IT', 'Information Technology'),
        ('HR', 'Human Resources'),
        ('Sales', 'Sales'),
        ('Finance', 'Finance'),
        ('Marketing', 'Marketing'),
    ]

    
    company_name = models.CharField(max_length=100, default="XYZ")
    role_required = models.CharField(max_length=100, default="Developer")
    address = models.TextField(default="Not specified")
    description = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=20000)
    experience = models.PositiveIntegerField(help_text="Years of experience required", default=1)
    skills_required = models.TextField(default="Node.js")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='IT')
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


# Create your models here.
