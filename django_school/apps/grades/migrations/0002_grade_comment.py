# Generated by Django 3.2.6 on 2021-08-19 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grades', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]