# Generated by Django 2.1 on 2018-09-19 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_recipient'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='template',
            field=models.CharField(default='default.html', max_length=125),
        ),
    ]