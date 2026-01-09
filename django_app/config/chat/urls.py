from django.urls import path
from .views import ask_question, main_page, search_page, serve_search_css, search_policy, serve_main_css, serve_chat_css, chat_page, get_policy_detail

urlpatterns = [
    path("", main_page, name="main"),  # 메인 페이지
    path("search/", search_page, name="search"),  # 검색 페이지
    path("chat/", chat_page, name="chat"),  # 채팅 페이지
    path("ask/", ask_question, name="ask"),
    path("main.css", serve_main_css, name="css"),  # CSS 파일
    path("search.css", serve_search_css, name="search_css"),  # 검색 CSS 파일
    path("chat.css", serve_chat_css, name="chat_css"),  # 채팅 CSS 파일
    path("search-policy/", search_policy, name="search_policy"),  # 정책 검색 페이지
    path("policy-detail/<uuid:policy_id>/", get_policy_detail, name="policy_detail"),  # 정책 상세 정보
]
