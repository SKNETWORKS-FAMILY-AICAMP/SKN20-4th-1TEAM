
# 청년 정책 AI 챗봇 서비스 (Youth Policy AI Chatbot)

AI 기반의 청년 정책 추천 및 검색 시스템으로, 사용자의 질문에 대해 실시간으로 맞춤형 청년 정책을 추천하고 검색할 수 있는 챗봇

---

## 팀명 : 청 바 지 (청춘은 바로 지금)

## 팀원 소개

| 나호성 | 강민지 | 이지은 | 조준상 | 홍혜원 |
|---|---|---|---|---|
| <img width="500" height="500" alt="Image" src="https://github.com/user-attachments/assets/aa1c4b5b-f271-44bc-8765-fb0717a255fb" /> | <img width="500" height="500" alt="Image" src="https://github.com/user-attachments/assets/93140ba3-81e2-4079-8084-8ebab3121a26" /> | <img width="500" height="500" alt="Image" src="https://github.com/user-attachments/assets/0ac142c1-01de-4130-bcdf-cf7bf026a371" /> | <img width="500" height="500" alt="Image" src="https://github.com/user-attachments/assets/4f23001a-38bb-41bb-ae6f-0ee01d97eebf" /> | <img width="500" height="500" alt="Image" src="https://github.com/user-attachments/assets/b133989b-a180-44cc-8fd6-d593e37aee8f" /> |


🏆 [SKN Family AI캠프] 4차 단위 프로젝트   
📅 개발 기간: 2025.01.09 ~ 2025.01.12


---

## 🎯 프로젝트 개요

본 프로젝트는 청년들이 자신에게 맞는 정부 지원 정책을 쉽게 찾을 수 있도록 돕는 **AI 기반 챗봇 서비스**

### 핵심 가치
- **사용자 친화적**: 직관적인 UI/UX로 누구나 쉽게 사용 가능
- **맞춤형 추천**: RAG(Retrieval-Augmented Generation) 기술을 통한 정확한 정책 추천
- **실시간 검색**: 고속의 정책 데이터 검색 및 필터링
- **데이터 기반**: 정부의 공식 청년 정책 데이터 기반

---

## ✨ 주요 기능

### 1. **AI 챗봇 기반 정책 추천**
- 자연어로 정책 관련 질문 입력
- RAG 기술을 활용한 정확한 정책 답변 제공
- 세션 기반 사용자 관리로 대화 이력 저장 ( NEW ) ⭐️

### 2. **정책 검색 시스템 ( NEW ) ⭐️**
- 정책명, 키워드, 분류별 검색
- 나이, 지원금액 범위 등 필터링 기능
- 빠른 검색 응답 속도

### 3. **정책 상세 정보 제공**
- 정책의 지원 내용, 신청 방법, 필요 서류 등 상세 정보
- 신청 기간 및 주관 기관 정보
- 연령 및 지원 금액 범위 명시

---

## 🛠️ 기술 스택

### 백엔드
| 분야 | 기술 |
|------|------|
| **Framework** | Django 5.0 |
| **Database** | SQLite3 |
| **Language** | Python 3.x |
| **API** | Django REST Framework |

### 프론트엔드
| 분야 | 기술 |
|------|------|
| **HTML/CSS/JS** | Vanilla JavaScript |
| **Styling** | CSS3 |
| **Communication** | Fetch API |

### AI/ML
| 분야 | 기술 |
|------|------|
| **RAG** | Retrieval-Augmented Generation |
| **Embeddings** | Vector-based Search |

### 데이터
| 분야 | 기술 |
|------|------|
| **Data Format** | JSON |
| **Source** | 공식 청년 정책 데이터 |

---

## 📊 데이터 소스

- **정책 데이터**: 대한민국 정부 공식 청년 정책 데이터 API
- **데이터 포맷**: JSON
- **포함 정보**: 정책명, 지원 내용, 신청 기간, 연령 제한, 지원금액 등

---

## 📁 프로젝트 구조

```
SKN20-4th-1TEAM/
├── README.md                          # 프로젝트 설명서
├── data/
│   └── youth_policies_filtered_kr_revised.json  # 청년 정책 데이터
├── django_app/
│   └── config/
│       ├── manage.py                  # Django 관리 도구
│       ├── db.sqlite3                 # SQLite 데이터베이스
│       ├── chat/                      # 채팅 앱
│       │   ├── models.py              # 데이터모델 (SessionUser, Question, Answer, Policy)
│       │   ├── views.py               # 뷰 로직
│       │   ├── urls.py                # URL 라우팅
│       │   ├── admin.py               # Django Admin 설정
│       │   ├── apps.py                # 앱 설정
│       │   ├── tests.py               # 테스트 코드
│       │   ├── management/
│       │   │   └── commands/
│       │   │       └── load_policies.py  # 정책 데이터 로드 커맨드
│       │   └── migrations/            # 데이터베이스 마이그레이션
│       ├── config/                    # Django 설정
│       │   ├── settings.py            # 프로젝트 설정
│       │   ├── urls.py                # 메인 URL 라우터
│       │   ├── asgi.py                # ASGI 설정
│       │   └── wsgi.py                # WSGI 설정
│       ├── templates/                 # HTML 템플릿
│       │   ├── main.html              # 메인 페이지
│       │   ├── main.css               # 메인 스타일
│       │   ├── chat.html              # 채팅 페이지
│       │   ├── chat.css               # 채팅 스타일
│       │   ├── search.html            # 검색 페이지
│       │   └── search.css             # 검색 스타일
│       └── static/                    # 정적 파일
│           ├── js/
│           │   ├── main.js            # 메인 JavaScript
│           │   ├── chat.js            # 채팅 기능 JavaScript
│           │   └── search.js          # 검색 기능 JavaScript
│           └── assets/
│               └── images/            # 이미지 자산
├── docs/                              # 추가 문서
├── rag/                               # RAG 모듈 (예정)
└── 산출물/                             # 최종 산출물

```

---

## 🏙️ 시스템 아키텍처

 <img width="1105" height="608" alt="image" src="https://github.com/user-attachments/assets/f2e3eab2-2fd8-4948-b096-7c88f06bfacb" />



---


### 데이터 Pipeline

```
┌──────────────┐
│ 정책 데이터     │
│ (JSON 등)     │
└───────┬──────┘
        │
        ▼
┌──────────────────────┐
│ 데이터 전처리/벡터화      │
│ (build_vectordb2.py) │
└───────┬──────────────┘
        │
        ▼
┌────────────────────┐
│ 정책 DB 적재          │
│ (load_policies.py) │
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│ 서비스 연동           │
│ (Django/RAG)       │
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│ 사용자 인터페이스       │
│ (웹 프론트엔드)        │
└────────────────────┘
```

각 단계 설명:
- 정책 데이터: data/ 폴더 내 JSON 등 원본 정책 데이터 확보
- 데이터 전처리/벡터화: build_vectordb2.py로 벡터DB(vectordb2/) 생성
- 정책 DB 적재: load_policies.py로 Django DB에 정책 데이터 적재
- 서비스 연동: Django 앱에서 정책 DB 및 벡터DB(RAG) 활용, 검색/챗봇 서비스 제공
- 사용자 인터페이스: templates, static을 통한 결과 시각화 및 제공


---

## 데이터 흐름

```
┌────────────┐        ┌──────────────┐        ┌──────────────┐         ┌──────────────┐
│    사용자    │  ◀──▶  │    프론트엔드   │  ◀──▶  │ 백엔드(Django) │   ◀──▶  │   데이터/AI   │
└────────────┘        └──────────────┘        └──────────────┘         └──────────────┘
      │                       │                      │                        │
      ▼                       ▼                      ▼                        ▼
   웹 브라우저             HTML/CSS/JS           Django View/URL         정책 데이터, 벡터DB, RAG
      │                       │                      │                        │
      ▼                       ▼                      ▼                        ▼
[정책 검색/챗봇 요청]   →   [요청 데이터 전송]     →     [정책/챗봇 처리]     →     [정책/챗봇 응답 생성]
      │                       │                      │                        │
      ▼                       ▼                      ▼                        ▼
[결과 수신 및 렌더링]   ←   [응답 데이터 수신]    ←   [정책/챗봇 결과 반환]    ←       [DB/AI 결과 조회]
```

주요 흐름:
- 사용자는 웹 브라우저에서 정책 검색 또는 챗봇 질문을 입력
- 프론트엔드(HTML/JS)가 입력을 백엔드(Django)로 전달
- Django는 정책 DB 또는 RAG(벡터DB)와 연동하여 결과 생성
- 결과를 프론트엔드로 반환, 사용자는 결과를 확인
- 프론트엔드 → Django View → 정책 DB 쿼리 → 결과 반환

---


## 📡 API 명세

### 1. 메인 페이지 조회
```
GET /
```
- **설명**: 메인 페이지 렌더링
- **Request**: 없음
- **Response**: HTML (메인 화면)

---

### 2. 채팅 페이지 조회
```
GET /chat/
```
- **설명**: AI 챗봇 채팅 페이지 렌더링
- **Request**: 없음
- **Response**: HTML (챗봇 UI)

---

### 3. 검색 페이지 조회
```
GET /search/
```
- **설명**: 정책 검색 페이지 렌더링
- **Request**: 없음
- **Response**: HTML (검색 UI)

---

### 4. 정책 검색 API
```
POST /api/policies/search/
Content-Type: application/json
{
    "keyword": "주거",
    "age": 25,
    "min_support_amount": 0,
    "max_support_amount": 1000000
}
```
- **설명**: 조건에 맞는 정책 리스트 반환
- **Request**:
    ```json
    {
        "keyword": "주거",
        "age": 25,
        "min_support_amount": 0,
        "max_support_amount": 1000000
    }
    ```
- **Response**:
    ```json
    [
        {
            "policy_id": "P001",
            "title": "청년 주거 지원 정책",
            "description": "청년을 위한 주거비 지원...",
            "age_min": 19,
            "age_max": 34,
            "min_support_amount": 0,
            "max_support_amount": 1000000
        },
        ...
    ]
    ```

---

### 5. 챗봇 질의 API
```
POST /api/chat/
Content-Type: application/json
{
    "question": "청년 주거 정책 알려줘"
}
```
- **설명**: 사용자의 질문에 대해 AI 챗봇이 답변 생성
- **Request**:
    ```json
    {
        "question": "청년 주거 정책 알려줘"
    }
    ```
- **Response**:
    ```json
    {
        "answer": "청년 주거 지원 정책은 ...",
        "related_policies": [
            { "policy_id": "P001", "title": "청년 주거 지원 정책" },
            ...
        ]
    }
    ```

---

### 6. 정책 상세 정보 API
```
GET /api/policies/{policy_id}/
```
- **설명**: 특정 정책의 상세 정보 반환
- **Request**: `/api/policies/P001/`
- **Response**:
    ```json
    {
        "policy_id": "P001",
        "title": "청년 주거 지원 정책",
        "description": "청년을 위한 주거비 지원...",
        "support_content": "월세 지원, 보증금 대출 등",
        "age_min": 19,
        "age_max": 34,
        "min_support_amount": 0,
        "max_support_amount": 1000000,
        "application_period": "2025-01-01 ~ 2025-12-31",
        "application_method": "온라인 신청",
        "required_documents": "신분증, 소득증명서 등"
    }
    ```
---

## 🗄️ 데이터베이스 스키마

### SessionUser 모델
```python
class SessionUser(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    createdAt = models.DateTimeField(auto_now_add=True)
```

### Question 모델
```python
class Question(models.Model):
    user = models.ForeignKey(SessionUser, on_delete=models.CASCADE)
    content = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)
```

### Answer 모델
```python
class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    content = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)
```

### Policy 모델
```python
class Policy(models.Model):
    policy_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    keywords = models.CharField(max_length=255)
    description = models.TextField()
    category_major = models.CharField(max_length=100)
    category_middle = models.CharField(max_length=100)
    support_content = models.TextField()
    min_support_amount = models.CharField(max_length=100)
    max_support_amount = models.CharField(max_length=100)
    age_min = models.IntegerField()
    age_max = models.IntegerField()
    hosting_org = models.CharField(max_length=100)
    application_period = models.CharField(max_length=255)
    application_method = models.TextField()
    required_documents = models.TextField()
    start_date = models.CharField(max_length=100)
    end_date = models.CharField(max_length=100)
```

---

## 📊 성능 지표

성능 결과 !!!

---


## 🌐 브라우저 실행 방법

1. Python 및 Django가 설치되어 있는지 확인합니다.
    - Python 3.x, pip, Django 5.0 이상이 필요합니다.
    - (필요시) 의존성 설치:
      ```bash
      pip install -r requirements.txt
      ```

2. 데이터베이스 및 정책 데이터를 준비합니다.
    - (최초 1회) 마이그레이션 적용:
      ```bash
      cd django_app/config
      python manage.py migrate
      ```
    - (정책 데이터 적재 필요시)
      ```bash
      python manage.py load_policies
      ```

3. Django 개발 서버를 실행합니다.
    ```bash
    python manage.py runserver
    ```

4. 웹 브라우저를 열고 아래 주소로 접속합니다.
    - 메인 페이지: http://127.0.0.1:8000/
    - 검색 페이지: http://127.0.0.1:8000/search/
    - 챗봇 페이지: http://127.0.0.1:8000/chat/



## 🚀 향후 계획

- **데이터베이스 확장**: 더 많은 정책 정보를 포함하도록 데이터베이스를 확장하여 서비스 범위를 확대
- **시스템 성능 최적화**: 응답 속도와 안정성을 개선하기 위해 시스템 성능을 지속적으로 최적화
- **사용자 피드백 반영**: 사용자 피드백을 적극적으로 반영하여 기능을 고도화할 계획
- **다양한 플랫폼 확대**: 여러 플랫폼으로 서비스를 확장하여 청년들에게 더 실질적인 도움을 제공
