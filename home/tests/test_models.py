from django.test import TestCase
from model_bakery import baker

from home import models
from users.models import User


class TestQuestion(TestCase):
    def setUp(self):
        user = baker.make(User, username='username')
        self.question = baker.make(models.Question, owner=user, title='test title', body='test body')
        self.accepted_answer = self.question.answers.create(owner=user, question=self.question, accepted=True,
                                                            body='test', )

    def test_question_str(self):
        self.assertEqual(str(self.question), 'username - test title...')

    def test_question_save(self):
        self.assertEqual(self.question.slug, 'test-title')

    def test_question_has_accepted_answer(self):
        self.assertTrue(self.question.has_accepted_answer())

    def test_question_short_title(self):
        self.assertEqual(self.question.short_title, 'test title...')

    def test_question_short_body(self):
        self.assertEqual(self.question.short_body, 'test body...')


class TestAnswer(TestCase):
    def setUp(self):
        user = baker.make(User, username='username')
        question = baker.make(models.Question, title='test title')
        self.answer = baker.make(models.Answer, body='test', owner=user, question=question)

    def test_answer_str(self):
        self.assertEqual(str(self.answer), 'username - test... - test title...')

    def test_answer_short_body(self):
        self.assertEqual(self.answer.short_body, 'test...')


class AnswerCommentTest(TestCase):
    def setUp(self):
        user = baker.make(User, username='username')
        answer = baker.make(models.Answer, body='test')
        self.comment = baker.make(models.AnswerComment, owner=user, answer=answer)

    def test_comment_str(self):
        self.assertEqual(str(self.comment), 'username - test...')


class CommentReplyTest(TestCase):
    def setUp(self):
        user = baker.make(User, username='username')
        self.reply = baker.make(models.CommentReply, owner=user, body='test')

    def test_comment_str(self):
        self.assertEqual(str(self.reply), 'username - test...')


class TagTest(TestCase):
    def setUp(self):
        sub_tag = baker.make(models.Tag, is_sub=True)
        self.tag = baker.make(models.Tag, sub_tag=sub_tag, name='test name')

    def test_tag_str(self):
        self.assertEqual(str(self.tag), 'test name')

    def test_tag_save(self):
        self.assertEqual(self.tag.slug, 'test-name')


class VoteTest(TestCase):
    def setUp(self):
        user = baker.make(User, is_active=True)
        answer = baker.make(models.Answer)
        self.like = baker.make(models.Vote, is_like=True, owner=user, answer=answer)
        self.dislike = baker.make(models.Vote, is_dislike=True, owner=user, answer=answer)

    def test_vote_str(self):
        self.assertEqual(str(self.like), 'Like')
        self.assertEqual(str(self.dislike), 'Dislike')
