# Generated by Django 2.0.6 on 2019-05-29 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAcore', '0008_user_avator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avator',
            field=models.CharField(default='author_avator/default.jpg', max_length=255),
        ),
    ]
