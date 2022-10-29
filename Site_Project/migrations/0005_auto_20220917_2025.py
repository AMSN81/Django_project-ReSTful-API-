# Generated by Django 3.2.9 on 2022-09-17 15:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Site_Project', '0004_projects_checked_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='checked_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='report',
            name='title',
            field=models.CharField(max_length=40),
        ),
    ]