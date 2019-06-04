# Generated by Django 2.0.6 on 2019-05-26 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAcore', '0002_auto_20190520_1952'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='uid',
            field=models.CharField(default=0, max_length=255),
        ),
        migrations.AlterField(
            model_name='resource',
            name='files',
            field=models.FileField(blank=True, upload_to='SAcore/static/files'),
        ),
    ]
