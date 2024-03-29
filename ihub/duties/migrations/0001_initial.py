# Generated by Django 2.2.1 on 2019-06-07 08:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Duty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duty_start', models.DateTimeField(editable=False)),
                ('task1_start', models.DateTimeField(editable=False)),
                ('task2_start', models.DateTimeField(editable=False)),
                ('task3_start', models.DateTimeField(editable=False)),
                ('duty_end', models.DateTimeField(editable=False)),
                ('task1_end', models.DateTimeField(editable=False)),
                ('task2_end', models.DateTimeField(editable=False)),
                ('task3_end', models.DateTimeField(editable=False)),
                ('last_active', models.DateTimeField(blank=True, null=True)),
                ('behalf', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='behalf', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
