import datetime
from django.utils import timezone
from django.test import TestCase
from .models import Question, Choice
from django.urls import reverse

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        pub_dateが未来の日付の場合、was_published_recently()はFalseを返す
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        pub_dateが1日より前の場合、was_published_recently()はFalseを返す
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        pub_dateが24時間以内の場合、was_published_recently()はTrueを返す
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        質問が何もなければ適切なメッセージが表示されるか
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "質問がありません。")
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        pub_dateが過去の場合、質問リストに表示されるか
        """
        question = Question.objects.create(
            question_text="過去の質問です。",
            pub_date=timezone.now() - datetime.timedelta(days=1)
        )
        response = self.client.get(reverse('index'))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [question]
        )

    def test_future_question(self):
        """
        pub_dateが未来の場合、質問リストに表示されないか
        """
        Question.objects.create(
            question_text="未来の質問です。",
            pub_date=timezone.now() + datetime.timedelta(days=30)
        )
        response = self.client.get(reverse('index'))
        self.assertContains(response, "質問がありません。")
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        未来の質問の詳細ページにはアクセスできない（404を返す）
        """
        future_question = Question.objects.create(
            question_text='未来の質問です。',
            pub_date=timezone.now() + datetime.timedelta(days=5)
        )
        url = reverse('detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        過去の質問の詳細ページは表示される
        """
        past_question = Question.objects.create(
            question_text='過去の質問です。',
            pub_date=timezone.now() - datetime.timedelta(days=1)
        )
        url = reverse('detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class VoteViewTests(TestCase):
    def setUp(self):
        # テスト用のQuestionとChoiceを作成
        self.question = Question.objects.create(
            question_text="好きな色は？",
            pub_date=timezone.now()
        )
        self.choice1 = Choice.objects.create(question=self.question, choice_text="赤", votes=0)
        self.choice2 = Choice.objects.create(question=self.question, choice_text="青", votes=0)

    def test_vote_count_up(self):
        """
        選択肢を選んで投票したらカウントアップされるか
        """
        vote_url = reverse('vote', args=(self.question.id,))
        response = self.client.post(vote_url, {'choice': self.choice1.id})
        self.choice1.refresh_from_db()
        self.assertEqual(self.choice1.votes, 1)
        self.assertRedirects(response, reverse('results', args=(self.question.id,)))

    def test_vote_no_choice_selected(self):
        """
        選択肢を選ばずに送信した場合、エラーメッセージが出るか
        """
        vote_url = reverse('vote', args=(self.question.id,))
        response = self.client.post(vote_url, {})  # choice未選択
        self.assertContains(response, "選択肢を選んでください。")