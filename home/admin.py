from django.contrib import admin

from . import models


class AnswerInline(admin.StackedInline):
    model = models.Answer
    raw_id_fields = ('owner', 'question')


class AnswerCommentsInline(admin.StackedInline):
    model = models.AnswerComment
    raw_id_fields = ('owner', 'answer')


class ReplyInline(admin.StackedInline):
    model = models.CommentReply
    raw_id_fields = ('owner', 'comment', 'reply')


class VoteInline(admin.StackedInline):
    model = models.Vote
    raw_id_fields = ('owner', 'answer')


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('short_title', 'short_body', 'owner', 'id', 'created')
    search_fields = ('owner__username', 'owner__email', 'title')
    raw_id_fields = ('owner',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = (AnswerInline,)


@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('owner', 'short_body', 'question', 'created')
    search_fields = ('owner__username', 'owner__email', 'body')
    raw_id_fields = ('question', 'owner')
    inlines = (AnswerCommentsInline, VoteInline)


@admin.register(models.AnswerComment)
class AnswerCommentAdmin(admin.ModelAdmin):
    list_display = ('owner', 'answer', 'created', 'id')
    raw_id_fields = ('owner', 'answer')
    search_fields = ('owner__username', 'owner__email', 'body', 'reply__body')
    inlines = (ReplyInline,)


admin.site.register(models.Tag)
