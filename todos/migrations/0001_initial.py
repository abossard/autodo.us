# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-03 19:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import todos.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_open', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(todos.models.CountMixin, todos.models.DurationMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Line',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('passed_on', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('duration', models.DurationField(blank=True, null=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='todos.Book')),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            bases=(todos.models.CountMixin, todos.models.DurationMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField()),
            ],
            options={
                'ordering': (),
            },
            bases=(todos.models.CountMixin, todos.models.DurationMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('finished', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='todos.Book')),
                ('current_line', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_task', to='todos.Line')),
            ],
            options={
                'ordering': ('-finished', 'created'),
            },
            bases=(todos.models.CountMixin, todos.models.DurationMixin, models.Model),
        ),
        migrations.AddField(
            model_name='tag',
            name='tagged',
            field=models.ManyToManyField(related_name='tag_set', to='todos.Task'),
        ),
        migrations.AddField(
            model_name='person',
            name='sitsin',
            field=models.ManyToManyField(to='todos.Task'),
        ),
        migrations.AddField(
            model_name='line',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='todos.Task'),
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together=set([('text', 'book')]),
        ),
        migrations.AlterUniqueTogether(
            name='book',
            unique_together=set([('name', 'owner')]),
        ),
    ]
