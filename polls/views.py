from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from .models import Question, Choice

# --- 質問リスト（トップページ） ---
class IndexView(generic.ListView):
    # 使用するテンプレートファイル名
    template_name = 'polls/index.html'
    # テンプレート内で使う変数名（オブジェクトリスト）
    context_object_name = 'latest_question_list'

    # 表示する質問リストの条件を定義（QuerySet）
    def get_queryset(self):
        # pub_dateが未来のものは除外し、最新5件を新しい順で返す
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

# --- 質問の詳細ページ ---
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    # 未来の質問は除外するため、カスタムQuerySetを上書き
    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

# --- 質問の集計（投票結果）ページ ---
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

# --- 投票処理（フォームPOST処理のみ関数ベースのまま） ---
def vote(request, question_id):
    # 該当する質問を取得。なければ404エラー
    question = get_object_or_404(Question, pk=question_id)
    try:
        # フォームで送信された選択肢（choice）を取得
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # 未選択や不正値の場合はエラーメッセージ付きで詳細ページ再表示
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "選択肢を選んでください。",
        })
    else:
        # 投票数をカウントアップして保存
        selected_choice.votes += 1
        selected_choice.save()
        # 投票後は結果ページにリダイレクト
        return HttpResponseRedirect(reverse('results', args=(question.id,)))