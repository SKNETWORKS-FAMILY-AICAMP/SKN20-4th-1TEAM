from django.urls import path
from .views import ask_question, main_page, serve_css, search_policy

urlpatterns = [
    path("", main_page, name="main"),  # 메인 페이지
    path("ask/", ask_question, name="ask"),
    path("search/", search_policy, name="search"),  # 통합 검색 API
    path("main.css", serve_css, name="css"),  # CSS 파일
]
