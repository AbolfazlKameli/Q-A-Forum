# Generated by Django 5.0.6 on 2024-07-08 12:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_alter_question_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='answer',
            old_name='user',
            new_name='owner',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='user',
            new_name='owner',
        ),
    ]
