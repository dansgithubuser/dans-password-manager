# Generated by Django 2.2.7 on 2020-09-26 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dans_password_manager', '0005_item_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='salt2',
            field=models.TextField(default='null'),
            preserve_default=False,
        ),
    ]
