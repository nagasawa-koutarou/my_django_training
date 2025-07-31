from django.urls import path
from . import views

urlpatterns = [
    # トップページ（質問リスト）：IndexViewのas_view()を指定
    path('', views.IndexView.as_view(), name='index'),

    # 質問の詳細ページ：pk（プライマリキー）でアクセス
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),

    # 結果ページもpk指定
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),

    # 投票処理（POSTのみ）は従来の関数ベースビュー
    path('<int:question_id>/vote/', views.vote, name='vote'),
]