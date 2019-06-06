# Generated by Django 2.2.1 on 2019-06-07 08:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('duties', '0002_auto_20190607_1636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='duty',
            name='behalf',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='delegated_duty', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='duty',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
