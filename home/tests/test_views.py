from urllib.parse import urlencode

from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from home import models
from home.views import *
from users.models import User


class TestHomeAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        tag = baker.make(models.Tag, name='test_tag')
        baker.make(models.Question, body='test body')
        baker.make(models.Question, body='test body test_search')
        baker.make(models.Question, body='test_tag body', tag=[tag])

    def test_home_GET(self):
        response = self.client.get(reverse('home:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 3)
        self.assertEqual(response.data['data'][2]['id'], 1)
        self.assertEqual(response.data['data'][2]['body'], 'test body')

    def test_home_filter_tag_GET(self):
        url = f"{reverse('home:home')}?{urlencode({'tag': 'test_tag'})}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['tag'], ['test_tag'])

    def test_home_filter_invalid_tag_GET(self):
        url = f"{reverse('home:home')}?{urlencode({'tag': ['invalid_tag']})}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(response.data), 1)

    def test_home_search_GET(self):
        url = f"{reverse('home:home')}?{urlencode({'search': 'search'})}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['body'], 'test body test_search')

    def test_home_search_GET_404(self):
        url = f"{reverse('home:home')}?{urlencode({'search': 'username'})}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data['error'], 'question not found.')


class TestQuestionViewSet(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = baker.make(User, is_active=True)
        self.tag = baker.make(models.Tag, name='test_tag')
        baker.make(models.Question, 33, owner=self.user)
        self.token = self.get_JWT_token()

    def get_JWT_token(self):
        token = AccessToken.for_user(self.user)
        return str(token)

    def test_permissions_allowed(self):
        data = {
            'title': 'test title',
            'body': 'test body',
        }
        request = self.factory.post(reverse('home:question-detail', args=[2]), data=data,
                                    HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = QuestionViewSet.as_view({'post': 'create'})(request, pk=2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_permissions_denied(self):
        request = self.factory.post(reverse('home:question-list'))
        request.user = AnonymousUser()
        response = QuestionViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 401)

    def test_question_list(self):
        request = self.factory.get(reverse('home:question-list'))
        request.user = AnonymousUser()
        response = QuestionViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 20)

    def test_question_list_pagination(self):
        url = f"{reverse('home:question-list')}?{urlencode({'page': 2})}"
        request = self.factory.get(url)
        request.user = AnonymousUser()
        response = QuestionViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 13)

    def test_question_create(self):
        data = {
            'tag': self.tag,
            'owner': self.user,
            'title': 'test_title',
            'body': 'test_body',
        }
        request = self.factory.post(reverse('home:question-list'), data=data, HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = QuestionViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'question created successfully!')

    def test_question_partial_update(self):
        data = {
            'title': 'update test',
        }
        request = self.factory.patch(reverse('home:question-detail', args=[2]), data=data,
                                     HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = QuestionViewSet.as_view({'patch': 'partial_update'})(request, pk=2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'update test')

    def test_question_full_update(self):
        data = {
            'title': 'update test',
            'body': 'update testing body'
        }
        request = self.factory.put(reverse('home:question-detail', args=[2]), data=data,
                                   HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = QuestionViewSet.as_view({'put': 'update'})(request, pk=2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'update test')
        self.assertEqual(response.data['body'], 'update testing body')

    def test_question_delete(self):
        request = self.factory.delete(reverse('home:question-detail', args=[2]),
                                      HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = QuestionViewSet.as_view({'delete': 'destroy'})(request, pk=2)
        self.assertEqual(response.status_code, 204)


class TestAnswerViewSet(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = baker.make(User, is_active=True)
        self.question = baker.make(models.Question, owner=self.user)
        baker.make(Answer, question=self.question, owner=self.user)
        self.token = self.get_JWT_token()

    def get_JWT_token(self):
        token = AccessToken.for_user(self.user)
        return str(token)

    def test_permissions_denied(self):
        request = self.factory.put(reverse('home:answer-viewset-detail', args=[1]))
        request.user = AnonymousUser()
        response = AnswerViewSet.as_view({'put': 'update'})(request, pk=1)
        self.assertEqual(response.status_code, 401)

    def test_answer_create(self):
        data = {
            'owner': self.user,
            'body': 'test_body',
        }
        url = f"{reverse('home:answer-viewset-list')}?{urlencode({'question_id': 1})}"
        request = self.factory.post(url, data=data,
                                    HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = AnswerViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'created successfully')

    def test_answer_partial_update(self):
        data = {
            'body': 'update test',
        }
        request = self.factory.patch(reverse('home:answer-viewset-detail', args=[1]), data=data,
                                     HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = AnswerViewSet.as_view({'patch': 'partial_update'})(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['body'], 'update test')

    def test_answer_full_update(self):
        data = {
            'body': 'update testing body'
        }
        request = self.factory.put(reverse('home:answer-viewset-detail', args=[1]), data=data,
                                   HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = AnswerViewSet.as_view({'put': 'update'})(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['body'], 'update testing body')

    def test_answer_delete(self):
        request = self.factory.delete(reverse('home:answer-viewset-detail', args=[1]),
                                      HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = AnswerViewSet.as_view({'delete': 'destroy'})(request, pk=1)
        self.assertEqual(response.status_code, 204)


class TestAnswerCommentViewSet(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = baker.make(User, is_active=True)
        self.answer = baker.make(Answer)
        baker.make(AnswerComment, answer=self.answer, owner=self.user)
        self.token = self.get_JWT_token()

    def get_JWT_token(self):
        token = AccessToken.for_user(self.user)
        return str(token)

    def test_permissions_denied(self):
        request = self.factory.put(reverse('home:answer_comments-detail', args=[1]))
        request.user = AnonymousUser()
        response = AnswerCommentViewSet.as_view({'put': 'update'})(request, pk=1)
        self.assertEqual(response.status_code, 401)

    def test_comment_create(self):
        data = {
            'owner': self.user,
            'body': 'test_body',
        }
        url = f"{reverse('home:answer_comments-list')}?{urlencode({'answer_id': 1})}"
        request = self.factory.post(url, data=data, HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = AnswerCommentViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'created successfully')

    def test_comment_partial_update(self):
        data = {
            'body': 'update test',
        }
        request = self.factory.patch(reverse('home:answer_comments-detail', args=[1]), data=data,
                                     HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = AnswerCommentViewSet.as_view({'patch': 'partial_update'})(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['body'], 'update test')

    def test_comment_full_update(self):
        data = {
            'body': 'update testing body'
        }
        request = self.factory.put(reverse('home:answer_comments-detail', args=[1]), data=data,
                                   HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = AnswerCommentViewSet.as_view({'put': 'update'})(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['body'], 'update testing body')

    def test_comment_delete(self):
        request = self.factory.delete(reverse('home:answer_comments-detail', args=[1]),
                                      HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = AnswerCommentViewSet.as_view({'delete': 'destroy'})(request, pk=1)
        self.assertEqual(response.status_code, 204)


class TestReplyViewSet(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = baker.make(User, is_active=True)
        self.comment = baker.make(AnswerComment)
        baker.make(CommentReply, comment=self.comment, owner=self.user, reply=None)
        self.token = self.get_JWT_token()

    def get_JWT_token(self):
        token = AccessToken.for_user(self.user)
        return str(token)

    def test_permissions_denied(self):
        request = self.factory.put(reverse('home:reply-detail', args=[1]))
        request.user = AnonymousUser()
        response = ReplyViewSet.as_view({'put': 'update'})(request, pk=1)
        self.assertEqual(response.status_code, 401)

    def test_reply_create(self):
        data = {
            'owner': self.user,
            'body': 'test_body',
        }
        url = f"{reverse('home:reply-list')}?{urlencode({'comment_id': 1})}"
        request = self.factory.post(url, data=data, HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = ReplyViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'created successfully!')

    def test_reply_partial_update(self):
        data = {
            'body': 'update test',
        }
        request = self.factory.patch(reverse('home:reply-detail', args=[1]), data=data,
                                     HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = ReplyViewSet.as_view({'patch': 'partial_update'})(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['body'], 'update test')

    def test_comment_full_update(self):
        data = {
            'body': 'update testing body'
        }
        request = self.factory.put(reverse('home:reply-detail', args=[1]), data=data,
                                   HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = ReplyViewSet.as_view({'put': 'update'})(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['body'], 'update testing body')

    def test_comment_delete(self):
        request = self.factory.delete(reverse('home:reply-detail', args=[1]),
                                      HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = ReplyViewSet.as_view({'delete': 'destroy'})(request, pk=1)
        self.assertEqual(response.status_code, 204)


class TestLikeAPI(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = baker.make(User, is_active=True)
        self.answer = baker.make(Answer)
        baker.make(models.Vote, is_like=True)
        baker.make(models.Vote, is_dislike=True)
        self.token = self.get_JWT_token()

    def get_JWT_token(self):
        token = AccessToken.for_user(self.user)
        return str(token)

    def test_permissions_denied(self):
        request = self.factory.post(reverse('home:answer_like', args=[1]))
        request.user = AnonymousUser()
        response = LikeAPI.as_view()(request, pk=1)
        self.assertEqual(response.status_code, 401)

    def test_like_create(self):
        request = self.factory.post(reverse('home:answer_like', args=[1]),
                                    HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = LikeAPI.as_view()(request, answer_id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'liked')

    def test_remove_like(self):
        baker.make(models.Vote, is_like=True, owner=self.user, answer=self.answer)
        request = self.factory.post(reverse('home:answer_like', args=[1]),
                                    HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = LikeAPI.as_view()(request, answer_id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'like removed')

    def test_like_on_dislike(self):
        baker.make(models.Vote, is_dislike=True, owner=self.user, answer=self.answer)
        request = self.factory.post(reverse('home:answer_like', args=[1]),
                                    HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = LikeAPI.as_view()(request, answer_id=1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Vote.objects.filter(is_dislike=True).count(), 0)
        self.assertEqual(response.data['message'], 'liked')


class TestDisLikeAPI(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = baker.make(User, is_active=True)
        self.answer = baker.make(Answer)
        baker.make(models.Vote, is_like=True)
        baker.make(models.Vote, is_dislike=True)
        self.token = self.get_JWT_token()

    def get_JWT_token(self):
        token = AccessToken.for_user(self.user)
        return str(token)

    def test_permissions_denied(self):
        request = self.factory.post(reverse('home:answer_like', args=[1]))
        request.user = AnonymousUser()
        response = LikeAPI.as_view()(request, pk=1)
        self.assertEqual(response.status_code, 401)

    def test_dislike_create(self):
        request = self.factory.post(reverse('home:answer_dislike', args=[1]),
                                    HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = DisLikeAPI.as_view()(request, answer_id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'disliked')

    def test_remove_dislike(self):
        baker.make(models.Vote, is_dislike=True, owner=self.user, answer=self.answer)
        request = self.factory.post(reverse('home:answer_dislike', args=[1]),
                                    HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = DisLikeAPI.as_view()(request, answer_id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'dislike removed')

    def test_dislike_on_like(self):
        baker.make(models.Vote, is_like=True, owner=self.user, answer=self.answer)
        request = self.factory.post(reverse('home:answer_dislike', args=[1]),
                                    HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = DisLikeAPI.as_view()(request, answer_id=1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Vote.objects.filter(is_like=True).count(), 0)
        self.assertEqual(response.data['message'], 'disliked')
