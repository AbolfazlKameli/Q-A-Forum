from django.urls import reverse, resolve
from rest_framework.test import APISimpleTestCase

from home import views


class TestUrls(APISimpleTestCase):
    def test_home_url(self):
        home_url = reverse('home:home')
        self.assertEqual(resolve(home_url).func.view_class, views.HomeAPI)

    def test_answer_like_url(self):
        answer_like_url = reverse('home:answer_like', args=(20,))
        self.assertEqual(resolve(answer_like_url).func.view_class, views.LikeAPI)

    def test_answer_dislike_url(self):
        answer_dislike_url = reverse('home:answer_dislike', args=(20,))
        self.assertEqual(resolve(answer_dislike_url).func.view_class, views.DisLikeAPI)

    def test_accept_answer_url(self):
        accept_answer_url = reverse('home:answer_accept', args=(20,))
        self.assertEqual(resolve(accept_answer_url).func.view_class, views.AcceptAnswerAPI)
