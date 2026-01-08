import uuid
import os
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import SessionUser, Question, Answer

def main_page(request):
    """
    메인 페이지 렌더링
    """
    return render(request, 'main.html')

def serve_main_css(request):
    """
    templates 폴더의 CSS 파일 서빙
    """
    css_path = os.path.join(settings.BASE_DIR, 'templates', 'main.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    return HttpResponse(css_content, content_type='text/css')

def run_rag(prompt):
    """
    RAG 파이프라인 호출 (임시 더미 함수)
    실제 RAG 모듈로 교체 필요
    """
    # TODO: 실제 RAG 모듈 연결
    return f"[RAG 응답] {prompt}에 대한 답변입니다."

def chat_page(request):
    """
    채팅 페이지 렌더링
    """
    return render(request, 'chat.html')

def serve_chat_css(request):
    """
    templates 폴더의 CSS 파일 서빙
    """
    css_path = os.path.join(settings.BASE_DIR, 'templates', 'chat.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    return HttpResponse(css_content, content_type='text/css')

def get_recent_conversations(user, limit=3):
    """
    최근 질문 + 답변 N개를 가져온다
    """
    questions = (
        Question.objects
        .filter(user=user)
        .order_by("-createdAt")[:limit]
    )

    conversations = []
    for q in reversed(questions):
        try:
            a = q.answer
            conversations.append({
                "question": q.content,
                "answer": a.content
            })
        except Answer.DoesNotExist:
            continue

    return conversations

def get_guest_user(request):
    """
    세션에 UUID 있으면 가져오고,
    없으면 새 GuestUser 생성
    """
    user_uuid = request.session.get("guest_uuid")

    if not user_uuid:
        guest = SessionUser.objects.create()
        request.session["guest_uuid"] = str(guest.uuid)
        return guest

    return SessionUser.objects.get(uuid=user_uuid)

@csrf_exempt
@require_POST
def ask_question(request):
    content = request.POST.get("question")

    if not content:
        return JsonResponse({"error": "질문이 없습니다."}, status=400)

    # 1️⃣ 세션 유저
    user = get_guest_user(request)

    # 2️⃣ 🔥 이전 대화 불러오기 (현재 질문 저장 전에!)
    previous_conversations = get_recent_conversations(user)

    # 3️⃣ 🔥 프롬프트 구성
    prompt = ""
    for conv in previous_conversations:
        prompt += f"Q: {conv['question']}\n"
        prompt += f"A: {conv['answer']}\n\n"

    prompt += f"Q: {content}\nA:"

    # 4️⃣ RAG / LLM 호출 (예시)
    answer_text = run_rag(prompt)  # ← 기존 RAG 함수

    # 5️⃣ 질문 저장 (답변 생성 후)
    question = Question.objects.create(
        user=user,
        content=content
    )

    # 6️⃣ 답변 저장
    Answer.objects.create(
        question=question,
        content=answer_text
    )

    return JsonResponse({
        "question": content,
        "answer": answer_text
    })
