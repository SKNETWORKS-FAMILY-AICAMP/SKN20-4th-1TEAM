from django.urls import path
from .views import ask_question, main_page, search_page, serve_css, serve_search_css, search_policy

urlpatterns = [
    path("", main_page, name="main"),  # 메인 페이지
    path("search/", search_page, name="search"),  # 검색 페이지
    path("ask/", ask_question, name="ask"),
    path("main.css", serve_css, name="css"),  # CSS 파일
    path("search.css", serve_search_css, name="search_css"),  # 검색 CSS 파일
    path("search-policy/", search_policy, name="search_policy"),  # 정책 검색 페이지
]
