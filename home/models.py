from django.db import models
from django.utils.text import slugify

from users.models import User


class Question(models.Model):
    tag = models.ManyToManyField('Tag', related_name='questions', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=500)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=50)

    class Meta:
        ordering = ('-modified', '-created')

    def __str__(self):
        return f'{self.owner.username} - {self.title[:30]}...'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title[:30])
        return super().save(*args, **kwargs)

    def has_accepted_answer(self):
        accepted = self.answers.filter(accepted=True)
        if accepted.exists():
            return True
        return False

    @property
    def short_title(self):
        return f'{self.title[:30]}...'

    @property
    def short_body(self):
        return f'{self.body[:30]}...'


class Answer(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    accepted = models.BooleanField(default=False)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-modified', '-created')

    def __str__(self):
        return f'{self.owner.username} - {self.body[:20]}... - {self.question.title[:30]}...'

    @property
    def short_body(self):
        return f'{self.body[:30]}...'


class AnswerComment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_comments')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-modified', '-created')

    def __str__(self):
        return f'{self.owner.username} - {self.answer.body[:20]}...'


class CommentReply(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='replies')
    comment = models.ForeignKey(AnswerComment, on_delete=models.CASCADE, related_name='replies')
    reply = models.ForeignKey('self', on_delete=models.CASCADE, related_name='i_replies', blank=True, null=True)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-modified', '-created')
        verbose_name_plural = 'replies'

    def __str__(self):
        return f'{self.owner.username} - {self.body[:10]}...'


class Tag(models.Model):
    sub_tag = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='s_tag')
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Vote(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='votes')
    is_like = models.BooleanField(default=False)
    is_dislike = models.BooleanField(default=False)

    def __str__(self):
        return 'Like' if self.is_like else 'Dislike'
