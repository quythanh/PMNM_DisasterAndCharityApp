# Generated by Django 5.1.3 on 2024-12-05 08:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CharityApp', '0003_donationposthistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockapply',
            name='location',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='CharityApp.location'),
        ),
    ]
