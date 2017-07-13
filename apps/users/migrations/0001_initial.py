# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.auth.models
import django.utils.timezone
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login', null=True, blank=True)),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('username', models.CharField(unique=True, max_length=60, error_messages={'unique': 'A user with that username already exists.'}, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w]+[ \\w.@+-]*$', 'Enter a valid username. This value may contain only letters, digits, spaces and @/./+/-/_ characters. It must start with a digit or a letter.', 'invalid')], help_text='Required. 60 characters or fewer. Letters, digits, spaces and @/./+/-/_ only.')),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='Email address', error_messages={'unique': 'A user with that email address already exists.'})),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('get_notifications', models.BooleanField(help_text='Designates whether you want to receive notifications. Unselect if you do not want to receive notifications.', default=True, verbose_name='Send me email notifications')),
                ('groups', models.ManyToManyField(related_name='user_set', blank=True, verbose_name='groups', related_query_name='user', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='auth.Group')),
                ('user_permissions', models.ManyToManyField(related_name='user_set', blank=True, verbose_name='user permissions', related_query_name='user', help_text='Specific permissions for this user.', to='auth.Permission')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
