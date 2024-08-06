from rest_framework import serializers

from .models import Question, Answer, AnswerComment, CommentReply, Tag


class QuestionSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    tag = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Tag.objects.all(), required=False)

    class Meta:
        model = Question
        exclude = ('slug',)


class AnswerSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    question = serializers.StringRelatedField(read_only=True)
    comments = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = '__all__'

    def get_comments(self, obj):
        comments = obj.comments.all()
        return AnswerCommentSerializer(comments, many=True).data

    def get_likes(self, obj):
        likes = obj.votes.filter(is_like=True)
        return likes.count()

    def get_dislikes(self, obj):
        dislikes = obj.votes.filter(is_dislike=True)
        return dislikes.count()


class AnswerCommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField(read_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    answer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AnswerComment
        fields = '__all__'

    def get_replies(self, obj):
        replies = obj.replies.filter(reply=None)
        return ReplyCommentSerializer(instance=replies, many=True).data


class ReplyCommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField(read_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    comment = serializers.StringRelatedField(read_only=True)
    reply = serializers.StringRelatedField(read_only=True, required=False)

    class Meta:
        model = CommentReply
        fields = '__all__'

    def get_replies(self, obj):
        replies = obj.i_replies.all()
        return ReplyCommentSerializer(instance=replies, many=True).data
