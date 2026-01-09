import json
import os
import warnings
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field 
from datetime import datetime

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        from langchain_community.retrievers import BM25Retriever, EnsembleRetriever
    RETRIEVERS_AVAILABLE = True
except ImportError:
    RETRIEVERS_AVAILABLE = False
    BM25Retriever = None
    EnsembleRetriever = None

# ============================================================================
# 1. 지역 정규화
class RegionNormalizer:
    def __init__(self, regions_data: List[Dict]):
        self.code_to_info = {}
        self.name_to_codes = {}
  
        self.sido_aliases = {
            "서울": "서울특별시", "부산": "부산광역시", "대구": "대구광역시",
            "인천": "인천광역시", "광주": "광주광역시", "대전": "대전광역시",
            "울산": "울산광역시", "세종": "세종특별자치시", "경기": "경기도",
            "충북": "충청북도", "충남": "충청남도", "전북": "전북특별자치도",
            "전남": "전라남도", "경북": "경상북도", "경남": "경상남도",
            "제주": "제주특별자치도", "강원": "강원특별자치도"
        }

        self.national_keywords = ["전국", "대한민국", "정부", "국가", "전체", "모든", "모두"]
        
        self._build_maps(regions_data)

    def _build_maps(self, regions_data: List[Dict]):
        """리스트 내의 모든 딕셔너리를 순회하며 마스터 사전 구축"""
        for region_group in regions_data:
            for code, info in region_group.items():
                self.code_to_info[code] = info
                sido = info.get('시도', '')
                sigungu = info.get('시군구', '')


                if sido:
                    self._add_to_map(sido, code)
                    for alias, full in self.sido_aliases.items():
                        if full == sido:
                            self._add_to_map(alias, code)
                
                if sigungu:
                    self._add_to_map(sigungu, code)
                    self._add_to_map(sigungu.replace(" ", ""), code) 

                    parts = sigungu.split(" ")
                    last_part = parts[-1] 
                    self._add_to_map(last_part, code)
                    
                    if len(last_part) > 1: 
                        self._add_to_map(last_part[:-1], code)

    def _add_to_map(self, name: str, code: str):
        if not name or len(name) < 1: return
        if name not in self.name_to_codes: self.name_to_codes[name] = []
        if code not in self.name_to_codes[name]: self.name_to_codes[name].append(code)

    def detect(self, query: str) -> Dict:
        """질문에서 전국 키워드 및 지역 코드 추출"""
        is_national = any(kw in query for kw in self.national_keywords)
        
        detected_sido_codes = []
        for alias in self.sido_aliases.keys():
            if alias in query:
                detected_sido_codes.extend(self.name_to_codes.get(alias, []))

        detected_code = None
        found_name = None
        sorted_names = sorted(self.name_to_codes.keys(), key=len, reverse=True)
        
        for name in sorted_names:
            if name in query:
                possible_codes = self.name_to_codes[name]
                # 중복 지명 처리
                if len(possible_codes) > 1 and detected_sido_codes:
                    for c in possible_codes:
                        if any(self.code_to_info[c]['시도'] == self.code_to_info[s]['시도'] for s in detected_sido_codes):
                            detected_code = c
                            break
                if not detected_code:
                    detected_code = possible_codes[0]
                found_name = name
                break

        res_sido = None
        res_sigungu = None
        if detected_code:
            info = self.code_to_info[detected_code]
            if info.get('시군구'):
                res_sigungu = detected_code
                for c, i in self.code_to_info.items():
                    if i['시도'] == info['시도'] and not i['시군구']:
                        res_sido = c
                        break
            else:
                res_sido = detected_code

        return {
            "has_region": bool(res_sido or res_sigungu or is_national),
            "sido_code": res_sido,
            "sigungu_code": res_sigungu,
            "is_national": is_national, # 전국 여부 반환
            "detected_name": found_name
        }

# 2. RegionFilter: 코드 기반
class RegionFilter:
    def __init__(self, regions_data: List[Dict]):
        self.normalizer = RegionNormalizer(regions_data)

    def build_chroma_filter_from_codes(self, region_info: Dict) -> Optional[Dict]:
        filter_conditions = [{"region_scope": "national"}] 
        
        if region_info.get('sigungu_code'):
            filter_conditions.append({"regiona_code.sigungu": {"$array_contains": region_info['sigungu_code']}})
        
        if region_info.get('sido_code'):
            filter_conditions.append({"regions_code.sido": {"$array_contains": region_info['sido_code']}})
            
        return {"$or": filter_conditions}
    
    def build_chroma_filter_from_codes(self, region_info: Dict) -> Optional[Dict]:
        """지역 정보 딕셔너리로부터 ChromaDB 필터 생성"""
        if region_info.get('is_national'):
            return {"region_scope": "national"}
        
        if not region_info.get('sido_code') and not region_info.get('sigungu_code'):
            return None

        filter_conditions = [{"region_scope": "national"}]
        
        detected_code = region_info.get('sigungu_code') or region_info.get('sido_code')
        if detected_code:
            # JSON 문자열에 코드가 포함되어 있는지 확인
            # 예: "[\"11110\", \"11111\"]" contains "11110"
            filter_conditions.append({"regions_code.sido": {"$contains": detected_code}})
            filter_conditions.append({"regiona_code.sigungu": {"$contains": detected_code}})
        
        return {"$or": filter_conditions} if filter_conditions else None

    def post_filter(self, documents: List, detected_code: Optional[str]) -> List:
        if not detected_code: 
            return documents
        
        filtered = []
        for doc in documents:
            # 전국 정책 패스 (모든 지역에서 사용 가능)
            if doc.metadata.get('region_scope') == 'national':
                filtered.append(doc)
                continue
            
            # 지역 정책의 경우 - 정확한 코드 매칭만 허용
            sido_json = doc.metadata.get('regions_code.sido', '[]')
            sigungu_json = doc.metadata.get('regiona_code.sigungu', '[]')
            
            try:
                doc_sido = json.loads(sido_json) if isinstance(sido_json, str) else sido_json
                doc_sigungu = json.loads(sigungu_json) if isinstance(sigungu_json, str) else sigungu_json
            except:
                doc_sido = []
                doc_sigungu = []
            
            if not isinstance(doc_sido, list):
                doc_sido = [doc_sido] if doc_sido else []
            if not isinstance(doc_sigungu, list):
                doc_sigungu = [doc_sigungu] if doc_sigungu else []
            
            # 정확한 코드 매칭 확인
            if detected_code in doc_sido or detected_code in doc_sigungu:
                filtered.append(doc)
        
        # 필터링 후 문서가 없으면 전국 정책만 반환
        return filtered if filtered else [d for d in documents if d.metadata.get('region_scope') == 'national']
    
# 3. 라우터
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class QueryRouter:
    """사용자 질문의 유효성을 검증하고 검색용 핵심 키워드를 추출하는 라우터"""
    
    def __init__(self, llm):
        self.llm = llm
        self.router_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 청년 정책 챗봇의 '입력 분석가'입니다.
사용자의 질문을 분석하여 1) 유효성을 판단하고, 2) 검색에 방해되는 지역명을 제거한 '순수 주제 키워드'만 추출하세요.

[작업 1: 유효성 검증 (is_valid)]
- False 조건: 심한 욕설, 비속어, 무의미한 자모음 나열(예: 'ㅋㅋㅋ', 'ㄴㅇㄹ', 'asdf'), 정책과 전혀 무관한 혐오 표현
- True 조건: 인삿말(안녕), 단순 지역명(부산), 짧은 키워드(창업, 주거지원), 문장형 질문 등 정상적인 대화 시도

[작업 2: 키워드 정제 (refined_query)]
- 질문에서 **지역명(시도, 시군구)**과 **조사(은/는/이/가)**, **수식어(전국, 전체)**를 제거하세요.
- 오직 **'어떤 정책을 찾고 싶은지'**에 대한 핵심 명사(키워드)만 남기세요.
- 만약 지역명만 있고 키워드가 없다면(예: "부산"), "청년 정책"이라고 반환하세요.

[Few-shot 예시]
- 입력: "경기도 봉사" -> refined_query: "봉사" (지역명 '경기도' 제거)
- 입력: "부산 자격증 지원" -> refined_query: "자격증 지원" (지역명 '부산' 제거)
- 입력: "서울시 주거" -> refined_query: "주거"
- 입력: "전국 일자리 센터" -> refined_query: "일자리 센터"
- 입력: "개XX야 꺼져" -> is_valid: false, reason: "욕설 및 비속어 감지"
- 입력: "asdfasdf" -> is_valid: false, reason: "무의미한 문자열"

응답 형식 (JSON):
{{
    "is_valid": true/false,
    "refined_query": "정제된 키워드",
    "reason": "판단 근거"
}}"""),
            ("user", "{query}")
        ])
    
    def route(self, query: str) -> dict:
        """질문 검증 및 핵심 키워드 반환"""
        try:
            chain = self.router_prompt | self.llm | StrOutputParser()
            result_str = chain.invoke({"query": query})
  
            cleaned_str = result_str.strip().replace("```json", "").replace("```", "")

            result = json.loads(cleaned_str)
            return result
            
        except json.JSONDecodeError:
            logger.warning(f"[QueryRouter] JSON 파싱 에러. 원본: {result_str}")
            return {
                "is_valid": True,
                "refined_query": query, # 파싱 실패 시 원본 사용
                "reason": "파싱 에러로 인한 기본 처리"
            }
        except Exception as e:
            logger.exception(f"[QueryRouter] 에러 발생: {e}")
            return {
                "is_valid": True,
                "refined_query": query,
                "reason": "시스템 에러로 인한 기본 처리"
            }

# 4. 멀티쿼리        
class MultiQueryGenerator:
    """검색 재현율을 높이기 위해 질문을 다각도로 확장"""
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 청년 정책 검색 전문가입니다. 
사용자의 질문을 바탕으로 벡터 DB 검색에 최적화된 3개의 유사 질문을 생성하세요.
단, 원본의 핵심 의미(창업, 주거 등)를 유지하면서 다양한 키워드(플랫폼, 지원금, 센터 등)를 활용하세요.

응답 형식:
1. 확장 질문 1
2. 확장 질문 2
3. 확장 질문 3"""),
            ("user", "{query}")
        ])

    def generate(self, query: str) -> List[str]:
        chain = self.prompt | self.llm | StrOutputParser()
        response = chain.invoke({"query": query})
        # 줄바꿈으로 분리하여 리스트화
        queries = [q.strip() for q in response.split("\n") if q.strip()]
        return queries[:3]




# 5. 앙상블 리트리버
class EnsembleRetriever:
    """
    Dense(의미) 검색과 BM25(키워드) 검색을 결합한 통합 리트리버
    - QueryRouter가 뽑아준 '핵심 키워드'로 검색 수행
    - RegionFilter가 생성한 '행정 코드 필터' 적용
    """
    
    def __init__(
        self, 
        documents: List[any],
        vectorstore: Chroma,
        llm: ChatOpenAI = None,
        bm25_k: int = 15,       # 검색 재현율(Recall)을 위해 K값 상향 (기존 5)
        vector_k: int = 20,     # 전국 정책 확보를 위해 K값 상향 (기존 10)
        bm25_weight: float = 0.6,   # '중독' 등 핵심 키워드 보존을 위해 비중 상향 (기존 0.4)
        vector_weight: float = 0.4  # 의미적 왜곡(축제 등) 방지를 위해 비중 조정 (기존 0.6)
    ):
        self.documents = documents
        self.vectorstore = vectorstore
        self.llm = llm
        
        self.bm25_k = bm25_k
        self.vector_k = vector_k
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
        
        self._build_bm25()
        self._build_vector()
    
    def _build_bm25(self):
        """키워드 기반 BM25 리트리버 초기화"""
        if not RETRIEVERS_AVAILABLE or BM25Retriever is None or not self.documents:
            self.bm25_retriever = None
            return
        
        try:
            self.bm25_retriever = BM25Retriever.from_documents(
                documents=self.documents,
                k=self.bm25_k
            )
        except Exception:
            self.bm25_retriever = None
    
    def _build_vector(self):
        """임베딩 기반 Vector 리트리버 초기화"""
        try:
            # 기본 리트리버로 설정하되 검색 시 k값 적용
            self.vector_retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.vector_k}
            )
        except Exception:
            self.vector_retriever = None
    
    def dense_search(self, query: str, metadata_filter: Dict = None) -> List[Tuple[any, float]]:
        """
        행정 코드 필터가 적용된 Dense 검색
        - query: QueryRouter가 정제한 refined_query
        - metadata_filter: RegionFilter가 만든 코드 기반 필터 ($or 조건 등)
        """
        try:
            if self.vector_retriever:
                # 메타데이터 필터(시도/시군구 코드)를 적용하여 정밀 검색
                docs = self.vectorstore.similarity_search(
                    query, 
                    k=self.vector_k,
                    filter=metadata_filter
                )
                return [(doc, 1.0) for doc in docs]
            return []
        except Exception:
            return []
    
    def bm25_search(self, query: str) -> List[Tuple[any, float]]:
        """키워드(명사) 기반 검색 - 정책 고유명사 포착용"""
        try:
            if self.bm25_retriever:
                docs = self.bm25_retriever.invoke(query)
                return [(doc, 1.0) for doc in docs]
            return []
        except Exception:
            return []
    
    def retrieve(self, queries: List[str], metadata_filter: Dict = None) -> Dict[str, List[Tuple[any, float]]]:
        """
        멀티 쿼리 결과를 수집하여 RRF로 넘겨주기 위한 통합 검색 실행
        """
        all_results = {
            'dense': [],
            'bm25': []
        }
        
        for q in queries:
            # 각 쿼리당 Dense 검색(필터 포함)과 BM25 검색 수행
            all_results['dense'].extend(self.dense_search(q, metadata_filter))
            all_results['bm25'].extend(self.bm25_search(q))
        
        return all_results
    
# 6. RRF
class ReciprocalRankFusion:
    """
    여러 검색 전략(Dense, BM25)의 결과를 순위 기반으로 통합하고,
    전국 단위 정책에 가산점을 부여하여 상위권으로 유지하는 통합 엔진
    """
    
    def __init__(self, k: int = 60):
        self.k = k  
    
    def fuse(self, results_dict: Dict[str, List[Tuple[any, float]]], top_k: int = 20) -> List[any]:
        """
        검색 결과 통합 및 전국 정책 부스팅
        - results_dict: {'dense': [(doc, score), ...], 'bm25': [...]}
        - top_k: 최종적으로 LLM에게 전달할 문서 수 (충분한 후보 확보를 위해 상향 권장)
        """
        doc_scores = {}
        
        # 1. 각 검색 방식별 결과 순회
        for method, results in results_dict.items():
            for rank, (doc, _) in enumerate(results, 1):
                # 문서 식별자 추출 (정책명 또는 고유 ID 사용)
                # 우리 정규화 데이터의 '정책명' 또는 'policy_id'를 기준으로 함
                doc_id = doc.metadata.get('정책명', id(doc))
                
                # RRF 핵심 공식 적용: 1 / (k + rank)
                rrf_score = 1.0 / (self.k + rank)
                
                if doc_id not in doc_scores:
                    doc_scores[doc_id] = {'doc': doc, 'score': 0}
                
                # 점수 누적 (Dense와 BM25 모두에서 상위권인 문서가 높은 점수를 얻음)
                doc_scores[doc_id]['score'] += rrf_score
        
        # 2. 전국 단위 정책 부스팅
        # 특정 지역 검색 시 지역 정책에 밀려 사라지는 전국 단위 핵심 정책을 끌어올림
        for doc_id in doc_scores:
            doc = doc_scores[doc_id]['doc']
            # 데이터 정규화 때 설정한 'region_scope' 활용
            if doc.metadata.get('region_scope') == 'national':
                # 전국 정책에 약 20%의 가산점을 주어 지역 정책 사이사이에 섞이게 함
                doc_scores[doc_id]['score'] *= 1.2
        
        # 3. 최종 점수 기준 내림차순 정렬
        sorted_docs = sorted(
            doc_scores.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )
        
        # 4. 상위 top_k개 문서 반환
        final_docs = [item[1]['doc'] for item in sorted_docs[:top_k]]
        
        return final_docs

# 7. 메모리
@dataclass
class ConversationMemory:
    """대화 기록 및 사용자의 지역 맥락(Context) 관리"""
    messages: List[Dict] = field(default_factory=list)
    max_history: int = 10
    current_region: Dict = field(default_factory=lambda: {
        "sido_code": None, 
        "sigungu_code": None, 
        "is_national": False
    })
    
    def add_message(self, role: str, content: str, region_info: Optional[Dict] = None):
        """메시지를 추가할 때 감지된 지역 정보도 업데이트"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # [수정] 새로운 지역 정보가 들어오면 업데이트 (기억 유지)
        if region_info and region_info.get('has_region'):
            self.current_region = {
                "sido_code": region_info.get('sido_code'),
                "sigungu_code": region_info.get('sigungu_code'),
                "is_national": region_info.get('is_national', False)
            }
        
        if len(self.messages) > self.max_history * 2:
            self.messages = self.messages[-self.max_history * 2:]
    
    def get_context(self) -> str:
        """LLM 답변 생성을 위한 텍스트 맥락 생성"""
        if not self.messages:
            return "이전 대화 없음"
        
        context_parts = []
        for msg in self.messages[-6:]:  # 최근 3턴
            role = "사용자" if msg['role'] == 'user' else "AI"
            context_parts.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_parts)

    def get_region_context(self) -> Dict:
        """현재 기억하고 있는 지역 정보 반환"""
        return self.current_region
    
    def clear(self):
        """기록 및 지역 정보 초기화"""
        self.messages.clear()
        self.current_region = {"sido_code": None, "sigungu_code": None, "is_national": False}


# 8. 최종 파이프라인
class AdvancedRAGPipeline:

    def __init__(
        self,
        vectorstore,  # vectordb2
        regions_data: List[Dict],  # regions_code.json 데이터
        llm,
        documents: List[any]  # BM25용 전체 문서 리스트
    ):
        # 1. 컴포넌트 초기화
        self.router = QueryRouter(llm)
        self.multi_query = MultiQueryGenerator(llm) 
        self.region_filter = RegionFilter(regions_data)
        self.retriever = EnsembleRetriever(
            documents=documents,
            vectorstore=vectorstore,
            llm=llm
        )
        self.rrf = ReciprocalRankFusion()
        self.memory = ConversationMemory()
        self.llm = llm

        # 2. 답변 생성용 선배봇 프롬프트
        self.answer_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 '온통청년 청년정책 전담 챗봇 선배봇'입니다.

역할:
- 너는 청년 정책(특히 주거·월세·일자리·복지) 정보를, 사용자가 이해하기 쉽게 정리해 주는 선배야.
- 후배에게 알려주듯 친근하고 부드러운 말투로 답변해. (예: ~해줄게, ~해보자, ~이야)
- 반드시 '검색된 정책 정보(documents)' 안에 있는 내용만 사용해서 답변해.
- 추측하거나 지어내지 말고, 문서에 없는 정보는 "문서에 없는 내용이라 확답이 어렵다"고 말해.

출력 형식(꼭 지켜야 함):

1. 항상 아래 인사문구로 시작한다.
    안녕! 나는 청년들의 든든한 정책 선배, 청년이음 선배봇🌟이야.
    주거, 월세, 일자리, 복지 정책 등 궁금한 점이 있으면 언제든지 나에게 물어봐!😺
             
1-1. 두번째 부턴 답변부터는 인사문구 생략 가능.
             
2. 그 다음 줄에 질문을 그대로 보여준다.
             
   사용자 질문 : {query}

3. 그 다음에 '답변 :'을 쓰고, 정책을 번호를 매겨서 정리한다.
   - 최소 3개, 최대 5개의 정책을 선택해서 답변해.
   - 각 정책은 아래 구조를 따른다.

   예시 형식:

   답변 :
   1. 정책명
             
    🔸사업 개요
        - 사업 기간 : ...
        - 목적 : ...

    🔸신청 자격(핵심 요건)
        - 연령 : ...
        - 주거 : ...
        - 소득 : ...
        - 기타 조건 : ...

    🔸지원 금액·기간
        - 월 지원 금액 : ...
        - 지원 기간 : ...

    🔸신청 방법(절차)
        - 어디에 신청 : ...
        - 어떻게 신청 : ...
   2. 정책명
             
    🔸사업 개요
        - 사업 기간 : ...
        - 목적 : ...

    🔸신청 자격(핵심 요건)
        - 연령 : ...
        - 주거 : ...
        - 소득 : ...
        - 기타 조건 : ...

    🔸지원 금액·기간
        - 월 지원 금액 : ...
        - 지원 기간 : ...

    🔸신청 방법(절차)
        - 어디에 신청 : ...
        - 어떻게 신청 : ...
   3. ...
             
    4. 마지막에 '출처' 블록을 적는다.
    - 문서 메타데이터(파일명, 페이지 정보 등)가 있으면 최대한 활용해서 작성한다.
    - 예시:
    🔹 출처:
        - 온통청년 청년정책 포털 (https://youthcenter.go.kr)

작성 시 유의사항:
- 정책명이 같은 것을 중복해서 쓰지 말 것.
- 질문에서 언급한 지역(예: 경북, 대구 등)과 직접적으로 관련 있는 정책을 최우선으로 선택할 것.
- 질문에서 '월세', '보증금', '전세' 등 키워드가 나오면, 주거·월세 관련 정책 위주로 정리할 것.
- 숫자(지원 금액, 기간, 연령)는 가능한 한 구체적인 값으로 써 줄 것.
- 줄바꿈이나 문단 구분을 명확히 해서 가독성을 높일 것.

"""),
            ("user", """[대화 맥락]
{context}

[검색된 정책 정보]
{documents}

[현재 질문]
{query}""")
        ])

    def query(self, user_query: str) -> Dict:
        """전체 프로세스 실행 (멀티쿼리 확장 및 지역 필터링 적용)"""
        
        # [Step 1] 지역 감지 우선 수행
        current_region_info = self.region_filter.normalizer.detect(user_query)
        logger.debug(f"감지된 지역 정보: {current_region_info}")
        
        # 메모리 업데이트 및 현재 지역 맥락 유지
        self.memory.add_message("user", user_query, current_region_info)
        active_region_info = self.memory.get_region_context()

        # [Step 2] Router 검증
        route_result = self.router.route(user_query)
        logger.debug(f"Router 결과: {route_result}")
        
        if not route_result['is_valid']:
            return {
                "answer": "안녕! '서울, 자격증'이나 '서울 강남구 일자리'처럼 구체적으로 물어봐주면 내가 정책을 더 잘 찾아줄 수 있어!😊",
                "detected_region": active_region_info,
                "source_documents": []
            }
        
        refined_keyword = route_result['refined_query']
        logger.debug(f"정제된 키워드: {refined_keyword}")

        # [Step 2-1 추가] 멀티쿼리 확장
        # "창업 지원" -> ["청년 창업 플랫폼", "창업 지원금 신청", "스타트업 지원 센터"]
        expanded_queries = self.multi_query.generate(refined_keyword)
        all_queries = [refined_keyword] + expanded_queries
        logger.debug(f"생성된 멀티쿼리: {all_queries}")

        # [Step 3] 필터 생성
        db_filter = None
        detected_region_code = None
        
        if not active_region_info.get('is_national') and (active_region_info.get('sigungu_code') or active_region_info.get('sido_code')):
            detected_region_code = active_region_info.get('sigungu_code') or active_region_info.get('sido_code')
            db_filter = self.region_filter.build_chroma_filter_from_codes(active_region_info)
            logger.debug(f"지역 코드 감지됨: {detected_region_code}")
        
        logger.debug(f"생성된 필터: {db_filter}")

        # [Step 4 수정] Retrieval: 앙상블 검색 (멀티쿼리 리스트 전달)
        search_results = self.retriever.retrieve(all_queries, db_filter)
        logger.debug(f"검색 결과 (Dense): {len(search_results['dense'])}, BM25: {len(search_results['bm25'])}")

        # [Step 5] RRF & Boosting
        top_docs = self.rrf.fuse(search_results, top_k=20)
        logger.debug(f"RRF 후 문서 수: {len(top_docs)}")

        # [Step 6 수정] 문서가 없으면 필터 없이 멀티쿼리로 재검색
        if not top_docs:
            logger.debug("필터링된 문서 없음. 필터 제거 후 재검색...")
            search_results = self.retriever.retrieve(all_queries, None)
            logger.debug(f"필터 제거 후 검색 결과 (Dense): {len(search_results['dense'])}, BM25: {len(search_results['bm25'])}")
            top_docs = self.rrf.fuse(search_results, top_k=20)
            logger.debug(f"필터 제거 후 RRF 결과: {len(top_docs)}")

        # [Step 7] Post-Filtering: Python 레벨의 강화된 지역 필터링
        final_docs = self.region_filter.post_filter(top_docs, detected_region_code)
        logger.debug(f"Post-filter 후 최종 문서 수: {len(final_docs)}")
        
        # 특정 지역 검색 시 다른 지역의 정책이 섞여있는지 확인하는 강화된 검증 로직 (원본 유지)
        if detected_region_code and final_docs:
            region_validated_docs = []
            for doc in final_docs:
                if doc.metadata.get('region_scope') == 'national':
                    region_validated_docs.append(doc)
                    continue
                
                sido_json = doc.metadata.get('regions_code.sido', '[]')
                sigungu_json = doc.metadata.get('regions_code.sigungu', '[]')
                
                try:
                    doc_sido = json.loads(sido_json) if isinstance(sido_json, str) else sido_json
                    doc_sigungu = json.loads(sigungu_json) if isinstance(sigungu_json, str) else sigungu_json
                except:
                    doc_sido = []
                    doc_sigungu = []
                
                if not isinstance(doc_sido, list): doc_sido = [doc_sido] if doc_sido else []
                if not isinstance(doc_sigungu, list): doc_sigungu = [doc_sigungu] if doc_sigungu else []
                
                if detected_region_code in doc_sido or detected_region_code in doc_sigungu:
                    region_validated_docs.append(doc)
                else:
                    logger.debug(f"필터 제외됨 - 정책: {doc.metadata.get('정책명')}, 시도: {doc_sido}, 시군구: {doc_sigungu}")
            
            final_docs = region_validated_docs

        # [Step 8] Answer Generation
        context = self.memory.get_context()
        docs_text = "\n\n".join([f"[{d.metadata.get('정책명')}\n{d.page_content[:400]}]" for d in final_docs[:3]])
        
        response_chain = self.answer_prompt | self.llm | StrOutputParser()
        answer = response_chain.invoke({
            "context": context,
            "documents": docs_text,
            "query": user_query
        })

        # [Step 9] Memory Update
        self.memory.add_message("assistant", answer)

        return {
            "answer": answer,
            "detected_region": active_region_info,
            "source_documents": final_docs[:3]
        }




# 테스트
from dotenv import load_dotenv
load_dotenv()


def initialize_test_system():
    """테스트를 위한 시스템 초기화"""
    logger.info("--- [시스템 초기화 중] ---")
    
    # 1. 환경 설정
    api_key = os.getenv("OPENAI_API_KEY")
    vectordb_path = "./data/vectordb2"  # 실제 저장된 경로로 수정 필요
    regions_code_path = "./data/regions_code.json" # 파일 경로

    # 2. LLM 및 임베딩 설정
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # 3. VectorDB 로드
    vectorstore = Chroma(
        persist_directory=vectordb_path,
        embedding_function=embeddings,
        collection_name="youth_policies"
    )

    # 4. regions_code.json 데이터 로드 (리스트 형태)
    with open(regions_code_path, 'r', encoding='utf-8') as f:
        regions_data = json.load(f)

    # 5. BM25용 전체 문서 추출 (VectorDB에서 긁어옴)
    logger.info("문서 로드 중...")
    all_docs_data = vectorstore.get()
    
    if not all_docs_data or not all_docs_data.get('documents'):
        logger.error("VectorDB에 문서가 없습니다!")
        logger.debug(f"VectorDB 경로: {vectordb_path}")
        logger.debug(f"Metadata: {all_docs_data}")
        raise ValueError("VectorDB에서 문서를 찾을 수 없습니다.")
    
    logger.info(f"로드된 문서 수: {len(all_docs_data['documents'])}")
    
    from langchain_core.documents import Document
    documents = [
        Document(page_content=text, metadata=meta) 
        for text, meta in zip(all_docs_data['documents'], all_docs_data['metadatas'])
        if text
    ]

    logger.info(f"처리된 문서 수: {len(documents)}")

    pipeline = AdvancedRAGPipeline(
        vectorstore=vectorstore,
        regions_data=regions_data,
        llm=llm,
        documents=documents
    )
    
    return pipeline


def main():
    # 시스템 초기화
    pipeline = initialize_test_system()

    print("청년이음 선배봇 CLI 테스트 모드")

    while True:
        user_input = input("질문: ").strip()
        
        if user_input in ["종료", "exit", "quit"]:
            print("선배봇: 다음에 또 궁금한 게 있으면 언제든 물어봐! 안녕~👋")
            break
        
        if not user_input:
            continue

        try:
            # 파이프라인 실행
            result = pipeline.query(user_input)
            
            # 결과 출력 (사용자 응답만 출력)
            print(f"\n{result['answer']}\n")
            
        except Exception as e:
            logger.exception(e)

if __name__ == "__main__":
    main()
