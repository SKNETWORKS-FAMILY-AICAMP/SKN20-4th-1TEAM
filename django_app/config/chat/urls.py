from django.urls import path
from .views import ask_question, chat_page, serve_chat_css

urlpatterns = [
    path("", chat_page, name="chat"),  # 챗 페이지
    path("ask/", ask_question, name="ask"),
    path("chat.css", serve_chat_css, name="css"),  # CSS 파일
]
