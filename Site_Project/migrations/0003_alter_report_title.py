# Generated by Django 3.2.9 on 2022-09-11 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Site_Project', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='title',
            field=models.CharField(max_length=10),
        ),
    ]
