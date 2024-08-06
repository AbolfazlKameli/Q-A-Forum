from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from permissions import permissions
from utils import paginators
from . import serializers
from .models import Question, Answer, AnswerComment, CommentReply, Tag, Vote


class HomeAPI(GenericAPIView):
    """Home page."""
    permission_classes = [AllowAny]
    pagination_class = paginators.StandardPageNumberPagination

    @extend_schema(parameters=[
        OpenApiParameter(name='tag', type=str, location=OpenApiParameter.QUERY, description='tag'),
        OpenApiParameter(name='search', type=str, location=OpenApiParameter.QUERY, description='search'),
    ])
    def get(self, request, *args, **kwargs):
        questions = Question.objects.all()
        if self.request.query_params.get('tag'):
            tag = get_object_or_404(Tag, slug=self.request.query_params['tag'])
            questions = tag.questions.all()
        if self.request.query_params.get('search'):
            questions = Question.objects.filter(body__icontains=self.request.query_params['search'])
            if not questions.exists():
                return Response(data={'error': 'question not found.'}, status=status.HTTP_404_NOT_FOUND)
        srz_data = serializers.QuestionSerializer(questions, many=True)
        return Response(data={'data': srz_data.data}, status=status.HTTP_200_OK)


class QuestionViewSet(ModelViewSet):
    """question CRUD operations ModelViewSet"""
    serializer_class = serializers.QuestionSerializer
    queryset = Question.objects.all()
    pagination_class = paginators.StandardPageNumberPagination

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return [AllowAny()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        return [permissions.IsOwnerOrReadOnly()]

    def create(self, request, *args, **kwargs):
        """creates a question object."""
        serializer = self.get_serializer(data=self.request.data)
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            return Response({'message': 'question created successfully!'})
        return Response({'error': serializer.errors})

    def retrieve(self, request, *args, **kwargs):
        """shows detail of one question object."""
        question = self.get_object()
        srz_question = self.get_serializer(question)
        answers = question.answers.all()
        srz_answers = serializers.AnswerSerializer(answers, many=True)
        return Response(data={'question': srz_question.data, 'answers': srz_answers.data}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """updates one question object."""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """deletes an answer object."""
        return super().destroy(request, *args, **kwargs)


class AnswerViewSet(ModelViewSet):
    serializer_class = serializers.AnswerSerializer
    queryset = Answer.objects.all()
    http_method_names = ['post', 'put', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [permissions.IsOwnerOrReadOnly()]

    @extend_schema(parameters=[
        OpenApiParameter(name='question_id', type=int, location=OpenApiParameter.QUERY, description='question id',
                         required=True)])
    def create(self, request, *args, **kwargs):
        """creates an answer object."""
        srz_data = self.get_serializer(data=self.request.POST)
        if srz_data.is_valid():
            question = get_object_or_404(Question, id=request.query_params.get('question_id'))
            srz_data.save(question=question, owner=self.request.user)
            return Response(data={'message': 'created successfully'}, status=status.HTTP_201_CREATED)
        return Response(data={'error': srz_data.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """updates an answer object."""
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """updates an answer object."""
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """deletes an answer object."""
        return super().destroy(request, *args, **kwargs)


class AnswerCommentViewSet(ModelViewSet):
    serializer_class = serializers.AnswerCommentSerializer
    queryset = AnswerComment.objects.all()
    http_method_names = ['post', 'put', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [permissions.IsOwnerOrReadOnly()]

    @extend_schema(parameters=[
        OpenApiParameter(name='answer_id', type=str, location=OpenApiParameter.QUERY, description='answer id'),
    ])
    def create(self, request, *args, **kwargs):
        """creates a comment object."""
        srz_data = self.get_serializer(data=self.request.data)
        if srz_data.is_valid():
            answer = get_object_or_404(Answer, id=self.request.query_params['answer_id'])
            srz_data.save(owner=self.request.user, answer=answer)
            return Response(
                data={'message': 'created successfully'},
                status=status.HTTP_201_CREATED
            )
        return Response(data={'error': srz_data.errors}, status=status.HTTP_400_BAD_REQUEST)


class ReplyViewSet(ModelViewSet):
    serializer_class = serializers.ReplyCommentSerializer
    queryset = CommentReply.objects.all()
    http_method_names = ['post', 'put', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [permissions.IsOwnerOrReadOnly()]

    @extend_schema(parameters=[
        OpenApiParameter(name='comment_id', type=int, location=OpenApiParameter.QUERY, description='comment_id',
                         required=True),
        OpenApiParameter(name='reply_id', type=int, location=OpenApiParameter.QUERY, description='reply_id')
    ])
    def create(self, request, *args, **kwargs):
        """created a reply object."""
        srz_data = self.get_serializer(data=self.request.data)
        if srz_data.is_valid():
            comment = get_object_or_404(AnswerComment, id=self.request.query_params.get('comment_id'))
            try:
                reply = CommentReply.objects.get(id=self.request.query_params.get('reply_id'))
            except CommentReply.DoesNotExist:
                reply = None
            srz_data.save(owner=self.request.user, comment=comment, reply=reply)
            return Response(data={'message': 'created successfully!'}, status=status.HTTP_201_CREATED)
        return Response(data={'error': srz_data.errors}, status=status.HTTP_400_BAD_REQUEST)


class LikeAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, answer_id):
        """add a like for each answer"""
        answer = get_object_or_404(Answer, id=answer_id)
        like = Vote.objects.filter(owner=self.request.user, answer=answer, is_like=True)
        dislike = Vote.objects.filter(owner=self.request.user, answer=answer, is_dislike=True)
        if like.exists():
            like.delete()
            return Response(data={'message': 'like removed'}, status=status.HTTP_200_OK)
        if dislike:
            dislike.delete()
        like.create(owner=self.request.user, answer=answer, is_like=True)
        return Response(data={'message': 'liked'}, status=status.HTTP_200_OK)


class DisLikeAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, answer_id):
        """add a dislike for each answer"""
        answer = get_object_or_404(Answer, id=answer_id)
        dislike = Vote.objects.filter(owner=self.request.user, answer=answer, is_dislike=True)
        like = Vote.objects.filter(owner=self.request.user, answer=answer, is_like=True)
        if dislike.exists():
            dislike.delete()
            return Response(data={'message': 'dislike removed'}, status=status.HTTP_200_OK)
        if like.exists():
            like.delete()
        dislike.create(owner=self.request.user, answer=answer, is_dislike=True)
        return Response(data={'message': 'disliked'}, status=status.HTTP_200_OK)


class AcceptAnswerAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, answer_id):
        """accept an answer object"""
        answer = get_object_or_404(Answer, id=answer_id)
        if request.user.id == answer.question.owner.id:
            if not answer.accepted and not answer.question.has_accepted_answer():
                answer.accepted = True
                answer.owner.score += 1
                answer.owner.save()
                answer.save()
                return Response(data={'message': 'accepted'}, status=status.HTTP_200_OK)
            return Response(data={'message': 'you can not accept an answer twice or accept two answers'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        return Response(data={'error': 'only question owner can perform this action'}, status=status.HTTP_403_FORBIDDEN)
