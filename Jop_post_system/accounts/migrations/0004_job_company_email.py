# Generated by Django 5.2 on 2025-05-25 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_job_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='company_email',
            field=models.EmailField(default='company@example.com', max_length=254),
        ),
    ]
