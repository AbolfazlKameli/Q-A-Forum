# Generated by Django 5.0.6 on 2024-07-10 15:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_alter_question_slug'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('is_reply', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='home.answer')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answer_comments', to=settings.AUTH_USER_MODEL)),
                ('reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='home.answercomment')),
            ],
        ),
    ]
