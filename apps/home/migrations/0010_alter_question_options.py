# Generated by Django 5.0.6 on 2024-07-09 14:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_alter_answer_modified_alter_question_modified'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('-modified', '-created')},
        ),
    ]
