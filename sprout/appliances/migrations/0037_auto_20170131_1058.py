# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-31 16:12


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appliances', '0036_template_ga_released'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appliance',
            options={'permissions': (('can_modify_hw', 'Can modify HW configuration'),)},
        ),
        migrations.AddField(
            model_name='appliance',
            name='cpu',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appliance',
            name='ram',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='provider',
            name='total_cpu',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='provider',
            name='total_memory',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='provider',
            name='used_cpu',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='provider',
            name='used_memory',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appliancepool',
            name='override_cpu',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appliancepool',
            name='override_memory',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='provider',
            name='memory_limit',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]