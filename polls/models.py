from django.db import models
import datetime
from django.utils import timezone

class Question(models.Model):
    question_text = models.CharField(max_length=200)  # 質問内容
    pub_date = models.DateTimeField('date published') # 公開日

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)  # 質問への外部キー
    choice_text = models.CharField(max_length=200)  # 選択肢内容
    votes = models.IntegerField(default=0)           # 投票数