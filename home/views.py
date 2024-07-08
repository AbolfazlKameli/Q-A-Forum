from django.utils.text import slugify
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from permissions import permissions
from utils import paginators
from . import serializers
from .models import Question


class QuestionListAPI(ListAPIView):
    """
    this view returns all questions.\n
    allowed methods: GET.
    """
    permission_classes = [AllowAny, ]
    queryset = Question.objects.all().order_by('-created')
    serializer_class = serializers.QuestionSerializer
    pagination_class = paginators.StandardPageNumberPagination
    lookup_field = 'slug'

    def options(self, request, *args, **kwargs):
        response = super().options(request, *args, **kwargs)
        response.headers['host'] = 'localhost'
        response.headers['user'] = request.user
        return response


class QuestionDetailUpdateDestroyAPI(RetrieveUpdateDestroyAPIView):
    """
    this view can retrieve, update and delete a question.\n
    allowed methods: GET, PUT, PATCH, DELETE.
    """
    permission_classes = [permissions.IsOwnerOrReadOnly, ]
    queryset = Question.objects.all()
    serializer_class = serializers.QuestionSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def retrieve(self, request, *args, **kwargs):
        question = self.get_object()
        srz_question = self.serializer_class(question)
        answers = question.answers.all()
        srz_answers = serializers.AnswerSerializer(answers, many=True)
        return Response({'question': srz_question.data, 'answers': srz_answers.data}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        srz_data = self.serializer_class(instance, data=self.request.data, partial=True)
        if srz_data.is_valid():
            vd = srz_data.validated_data
            vd['slug'] = slugify(srz_data.validated_data['title'][:30])
            srz_data.save()
            return Response(srz_data.data, status=status.HTTP_200_OK)
        return Response(srz_data.errors, status=status.HTTP_400_BAD_REQUEST)
