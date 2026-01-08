import uuid
import os
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.db.models import Q
from .models import SessionUser, Question, Answer, Policy

def run_rag(prompt):
    """
    RAG 파이프라인 호출 (임시 더미 함수)
    실제 RAG 모듈로 교체 필요
    """
    # TODO: 실제 RAG 모듈 연결
    return f"[RAG 응답] {prompt}에 대한 답변입니다."

def main_page(request):
    """
    메인 페이지 렌더링
    """
    return render(request, 'main.html')

def search_page(request):
    """
    검색 페이지 렌더링
    """
    return render(request, 'search.html')

def serve_css(request):
    """
    templates 폴더의 CSS 파일 서빙
    """
    css_path = os.path.join(settings.BASE_DIR, 'templates', 'main.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    return HttpResponse(css_content, content_type='text/css')

def serve_search_css(request):
    """
    templates 폴더의 search.css 파일 서빙
    """
    css_path = os.path.join(settings.BASE_DIR, 'templates', 'search.css')
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

@csrf_exempt
@require_POST
def search_policy(request):
    """
    청년 정책 통합 검색 API
    """
    try:
        # JSON 데이터 수신 시도
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # Fallback to POST (FormData)
            data = request.POST

        # 1. 필터 변수 추출
        region = data.get('region', '')
        marital_status = data.get('marital_status', '') # single, married
        age_str = data.get('age', '')
        income_min = data.get('income_min', '')
        income_max = data.get('income_max', '')
        
        # 리스트 형태의 태그들
        education = data.get('education', []) 
        major = data.get('major', [])
        employment_status = data.get('employment_status', [])
        specialization = data.get('specialization', [])
        
        # 검색어
        search_query = data.get('query', '')
        exclude_closed = data.get('exclude_closed', False)

        # 2. 쿼리셋 초기화
        policies = Policy.objects.all()

        # 3. 필터링 로직
        
        # (1) 검색어 (제목, 내용, 키워드)
        if search_query:
            policies = policies.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(keywords__icontains=search_query)
            )

        # (2) 지역 (region 필드에 포함 여부)
        # DB에 '서울', '부산' 등으로 저장되어 있다고 가정
        if region:
            # 매핑: seoul -> 서울
            region_map = {
                'seoul': '서울', 'busan': '부산', 'daegu': '대구', 
                'incheon': '인천', 'gwangju': '광주', 'daejeon': '대전', 
                'ulsan': '울산', 'sejong': '세종', 'gyeonggi': '경기'
            }
            kr_region = region_map.get(region, region)
            policies = policies.filter(region__icontains=kr_region)

        # (3) 혼인상태
        if marital_status:
            # DB: '미혼', '기혼', '제한없음' 등
            if marital_status == 'single':
                policies = policies.filter(Q(marital_status__icontains='미혼') | Q(marital_status__icontains='제한없음'))
            elif marital_status == 'married':
                policies = policies.filter(Q(marital_status__icontains='기혼') | Q(marital_status__icontains='제한없음'))

        # (4) 연령
        if age_str:
            try:
                age = int(age_str)
                # age_min <= age <= age_max (0이면 제한없음으로 간주할 수도 있으나, 데이터에 따라 다름)
                policies = policies.filter(
                    (Q(age_min__lte=age) | Q(age_min__isnull=True) | Q(age_min=0)) &
                    (Q(age_max__gte=age) | Q(age_max__isnull=True) | Q(age_max=0))
                )
            except ValueError:
                pass

        # (5) 학력 (education_requirement)
        if education and isinstance(education, list) and '제한없음' not in education:
            q_edu = Q()
            for edu in education:
                q_edu |= Q(education_requirement__icontains=edu)
            policies = policies.filter(q_edu)

        # (6) 전공 (major_requirement)
        if major and isinstance(major, list) and '제한없음' not in major:
            q_major = Q()
            for m in major:
                q_major |= Q(major_requirement__icontains=m)
            policies = policies.filter(q_major)

        # (7) 취업상태 (employment_status)
        if employment_status and isinstance(employment_status, list) and '제한없음' not in employment_status:
            q_emp = Q()
            for emp in employment_status:
                q_emp |= Q(employment_status__icontains=emp)
            policies = policies.filter(q_emp)
            
        # (8) 특화분야 (specialization)
        if specialization and isinstance(specialization, list) and '제한없음' not in specialization:
            q_spec = Q()
            for spec in specialization:
                q_spec |= Q(specialization__icontains=spec)
            policies = policies.filter(q_spec)

        # 4. 결과 반환
        results = []
        for p in policies[:50]:
            results.append({
                "id": p.policy_id,
                "title": p.title,
                "description": p.description[:100] + "..." if p.description else "",
                "region": p.region,
                "period": p.application_period,
                "url": p.app_url
            })

        return JsonResponse({
            "count": len(results),
            "results": results
        })

    except Exception as e:
        print(f"Search Error: {e}")
        return JsonResponse({"error": str(e)}, status=500)