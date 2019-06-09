# Generated by Django 2.2.1 on 2019-06-07 16:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('duties', '0005_auto_20190607_2010'),
    ]

    operations = [
        migrations.CreateModel(
            name='DutyManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='duty',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='active_duties', to='duties.DutyManager'),
        ),
    ]