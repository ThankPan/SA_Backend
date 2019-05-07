# Generated by Django 2.2 on 2019-05-06 14:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SAcore', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='bind',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='author',
            name='domain',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
