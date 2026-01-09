import uuid
import os
import json
import sys
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.db.models import Q
from .models import SessionUser, Question, Answer, Policy

# RAG 모듈 임포트
sys.path.append(os.path.join(settings.BASE_DIR.parent.parent, 'rag'))
from advanced_rag4_3 import (
    AdvancedRAGPipeline,
    RegionNormalizer,
    RegionFilter,
    QueryRouter,
    MultiQueryGenerator,
    EnsembleRetriever,
    ReciprocalRankFusion,
    ConversationMemory
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

# 프로젝트 루트의 .env 파일 로드
project_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # RAG 폴더의 .env 확인
    rag_env_path = os.path.join(project_root, 'rag', '.env')
    if os.path.exists(rag_env_path):
        load_dotenv(rag_env_path)

# 전역 RAG 파이프라인 인스턴스
_rag_pipeline = None

def initialize_rag_pipeline():
    """RAG 파이프라인 초기화 (첫 실행 시 한 번만)"""
    global _rag_pipeline
    
    if _rag_pipeline is not None:
        return _rag_pipeline
    
    try:
        # 프로젝트 루트 경로
        project_root = settings.BASE_DIR.parent.parent
        vectordb_path = os.path.join(project_root, 'data', 'vectordb2')
        regions_code_path = os.path.join(project_root, 'data', 'regions_code.json')
        
        # OpenAI API 키 확인
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        
        # 파일 존재 확인
        if not os.path.exists(vectordb_path):
            raise FileNotFoundError(f"VectorDB를 찾을 수 없습니다: {vectordb_path}")
        
        if not os.path.exists(regions_code_path):
            raise FileNotFoundError(f"regions_code.json을 찾을 수 없습니다: {regions_code_path}")
        
        # LLM 및 임베딩 설정
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)
        
        # VectorDB 로드
        vectorstore = Chroma(
            persist_directory=vectordb_path,
            embedding_function=embeddings,
            collection_name="youth_policies"
        )
        
        # regions_code.json 로드
        with open(regions_code_path, 'r', encoding='utf-8') as f:
            regions_data = json.load(f)
        
        # BM25용 전체 문서 추출
        all_docs_data = vectorstore.get()
        documents = [
            Document(page_content=text, metadata=meta) 
            for text, meta in zip(all_docs_data['documents'], all_docs_data['metadatas'])
            if text
        ]
        
        # 파이프라인 생성
        _rag_pipeline = AdvancedRAGPipeline(
            vectorstore=vectorstore,
            regions_data=regions_data,
            llm=llm,
            documents=documents
        )
        
        return _rag_pipeline
        
    except Exception as e:
        import traceback
        print(f"RAG 파이프라인 초기화 실패: {e}")
        print(f"상세 에러:\n{traceback.format_exc()}")
        return None

def run_rag(prompt):
    """
    RAG 파이프라인 호출
    """
    try:
        pipeline = initialize_rag_pipeline()
        if pipeline is None:
            return "죄송합니다. 시스템 초기화에 실패했습니다. 잠시 후 다시 시도해주세요."
        
        result = pipeline.query(prompt)
        return result['answer']
        
    except Exception as e:
        print(f"RAG 실행 에러: {e}")
        return "죄송합니다. 답변 생성 중 오류가 발생했습니다. 다시 시도해주세요."

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

def chat_page(request):
    """
    채팅 페이지 렌더링
    """
    return render(request, 'chat.html')
def serve_main_css(request):
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

def serve_chat_css(request):
    """
    templates 폴더의 chat.css 파일 서빙
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

        # (9) 마감제외 (exclude_closed) - 현재 날짜 기준
        if exclude_closed:
            import re
            today = datetime.now().strftime('%Y%m%d')  # YYYYMMDD 형식 (예: 20260109)
            
            # 마감되지 않은 정책 필터링
            # 1단계: 기본 필터 - 상시/연중이거나 마감이 아닌 것들
            policies = policies.exclude(
                period_type__icontains='마감'  # '마감'으로 명시된 것 제외
            )
            
            # 2단계: 신청기간의 종료일 확인
            filtered_ids = []
            for policy in policies:
                # 상시/연중은 항상 포함
                if policy.period_type and ('상시' in policy.period_type or '연중' in policy.period_type):
                    filtered_ids.append(policy.policy_id)
                    continue
                
                if policy.application_period and ('상시' in policy.application_period or '연중' in policy.application_period):
                    filtered_ids.append(policy.policy_id)
                    continue
                
                # 신청기간이 없으면 신청기간구분 확인
                if not policy.application_period or policy.application_period.strip() == '':
                    # 신청기간구분이 '특정기간'이 아니거나 없으면 포함
                    if not policy.period_type or '특정기간' not in policy.period_type:
                        filtered_ids.append(policy.policy_id)
                    continue
                
                # 신청기간에서 모든 종료일 추출
                # 형식: "20250801 ~ 20250828" 또는 "20260101 ~ 20261231\N20270101 ~ 20271231"
                # \N, \n, 줄바꿈 등으로 구분된 여러 기간 처리
                periods_text = policy.application_period.replace('\\N', '\n').replace('\\n', '\n')
                
                # 모든 "~ YYYYMMDD" 패턴 찾기
                end_dates = re.findall(r'~\s*(\d{8})', periods_text)
                
                if end_dates:
                    # 가장 마지막(최신) 종료일 확인
                    latest_end_date = max(end_dates)
                    if latest_end_date >= today:  # 종료일이 오늘 이후이면 포함
                        filtered_ids.append(policy.policy_id)
                else:
                    # 날짜 형식이 아니면 포함 (안전하게)
                    filtered_ids.append(policy.policy_id)
            
            # 필터링된 ID로 쿼리셋 재구성
            policies = policies.filter(policy_id__in=filtered_ids)

        # 4. 결과 반환
        results = []
        for p in policies:
            results.append({
                "id": str(p.policy_id),
                "title": p.title,
                "description": p.description[:150] + "..." if p.description and len(p.description) > 150 else p.description or "",
                "category": p.category_major or "기타",
                "region": p.region,
                "period": p.application_period,
                "period_type": p.period_type or "",
                "keywords": p.keywords or "",
                "url": p.app_url
            })

        return JsonResponse({
            "count": len(results),
            "results": results
        })

    except Exception as e:
        print(f"Search Error: {e}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def get_policy_detail(request, policy_id):
    """
    정책 상세 정보 조회 API
    """
    try:
        policy = Policy.objects.get(policy_id=policy_id)
        
        data = {
            "policy_id": str(policy.policy_id),
            "title": policy.title,
            "keywords": policy.keywords,
            "description": policy.description,
            "category_major": policy.category_major,
            "category_middle": policy.category_middle,
            "support_content": policy.support_content,
            "min_support_amount": policy.min_support_amount,
            "max_support_amount": policy.max_support_amount,
            "age_min": policy.age_min,
            "age_max": policy.age_max,
            "application_period": policy.application_period,
            "period_type": policy.period_type,
            "application_method": policy.application_method,
            "required_documents": policy.required_documents,
            "selection_method": policy.selection_method,
            "ref_url1": policy.ref_url1,
            "ref_url2": policy.ref_url2,
            "marital_status": policy.marital_status,
            "income_condition": policy.income_condition,
            "major_requirement": policy.major_requirement,
            "employment_status": policy.employment_status,
            "education_requirement": policy.education_requirement,
            "specialization": policy.specialization,
            "region": policy.region,
            "hosting_org": policy.hosting_org,
            "registering_org": policy.registering_org,
            "parent_org": policy.parent_org,
            "parent_registering_org": policy.parent_registering_org
        }
        
        return JsonResponse(data)
        
    except Policy.DoesNotExist:
        return JsonResponse({"error": "정책을 찾을 수 없습니다."}, status=404)
    except Exception as e:
        print(f"Policy Detail Error: {e}")
        return JsonResponse({"error": str(e)}, status=500)