# Generated by Django 3.2.7 on 2022-02-20 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("lessons", "0011_homeworkrealisation"),
    ]

    operations = [
        migrations.RenameField(
            model_name="homeworkrealisation",
            old_name="hand_over_date",
            new_name="submission_date",
        ),
    ]