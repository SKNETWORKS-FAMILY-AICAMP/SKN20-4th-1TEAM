# 청년 정책 AI 챗봇 서비스 (Youth Policy AI Chatbot)

AI 기반의 청년 정책 추천 및 검색 시스템으로, 사용자의 질문에 대해 실시간으로 맞춤형 청년 정책을 추천하고 검색할 수 있는 챗봇

---

## 📋 팀명

## 📋 팀원소개


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
- 세션 기반 사용자 관리로 대화 이력 저장

### 2. **정책 검색 시스템**
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

## 📡 API 명세

### 1. 메인 페이지 조회
```
GET /
```
- **설명**: 메인 페이지 렌더링
- **응답**: HTML 페이지

### 2. 검색 페이지 조회
```
GET /search/
```
- **설명**: 검색 페이지 렌더링
- **응답**: HTML 페이지

### 3. 채팅 페이지 조회
```
GET /chat/
```
- **설명**: AI 챗봇 채팅 페이지 렌더링
- **응답**: HTML 페이지

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

## 📊 데이터 소스

- **정책 데이터**: 대한민국 정부 공식 청년 정책 데이터
- **데이터 포맷**: JSON
- **포함 정보**: 정책명, 지원 내용, 신청 기간, 연령 제한, 지원금액 등

---
