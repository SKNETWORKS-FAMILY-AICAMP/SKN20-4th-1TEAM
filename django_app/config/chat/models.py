import uuid
from django.db import models


class SessionUser(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.uuid)


class Question(models.Model):
    user = models.ForeignKey(SessionUser, on_delete=models.CASCADE)
    content = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:30]


class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name="answer")
    content = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:30]

class Policy(models.Model):
    policy_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)  # 고유 ID
    title = models.CharField(max_length=255)  # 정책명
    keywords = models.CharField(max_length=255, null=True, blank=True)  # 정책키워드
    description = models.TextField(null=True, blank=True)  # 정책설명
    category_major = models.CharField(max_length=100, null=True, blank=True)  # 대분류
    category_middle = models.CharField(max_length=100, null=True, blank=True)  # 중분류
    support_content = models.TextField(null=True, blank=True)  # 지원내용
    min_support_amount = models.CharField(max_length=100, null=True, blank=True)  # 최소지원금액 (문자열로 처리)
    max_support_amount = models.CharField(max_length=100, null=True, blank=True)  # 최대지원금액 (문자열로 처리)
    age_min = models.IntegerField(null=True, blank=True, default=0)  # 지원최소연령
    age_max = models.IntegerField(null=True, blank=True, default=0)  # 지원최대연령
    hosting_org = models.CharField(max_length=100, null=True, blank=True)  # 주관기관명
    registering_org = models.CharField(max_length=100, null=True, blank=True)  # 등록기관명
    parent_org = models.CharField(max_length=100, null=True, blank=True)  # 상위기관명
    parent_registering_org = models.CharField(max_length=100, null=True, blank=True)  # 상위등록기관명
    application_period = models.CharField(max_length=255, null=True, blank=True)  # 신청기간
    application_method = models.TextField(null=True, blank=True)  # 신청방법
    required_documents = models.TextField(null=True, blank=True)  # 제출서류
    start_date = models.CharField(max_length=100, null=True, blank=True)  # 사업시작일
    end_date = models.CharField(max_length=100, null=True, blank=True)  # 사업종료일
    selection_method = models.TextField(null=True, blank=True)  # 선정방법
    ref_url1 = models.URLField(max_length=500, null=True, blank=True)  # 참고URL1
    ref_url2 = models.URLField(max_length=500, null=True, blank=True)  # 참고URL2
    app_url = models.URLField(max_length=500, null=True, blank=True)  # 신청URL
    provider_group = models.CharField(max_length=100, null=True, blank=True)  # 재공기관그룹
    provision_method = models.CharField(max_length=100, null=True, blank=True)  # 정책제공방법
    approval_status = models.CharField(max_length=50, null=True, blank=True)  # 정책승인상태
    period_type = models.CharField(max_length=50, null=True, blank=True)  # 신청기간구분
    period_type_biz = models.CharField(max_length=50, null=True, blank=True)  # 사업기간구분
    marital_status = models.CharField(max_length=50, null=True, blank=True)  # 혼인상태
    income_condition = models.CharField(max_length=255, null=True, blank=True)  # 소득조건
    major_requirement = models.CharField(max_length=255, null=True, blank=True)  # 전공요건
    employment_status = models.CharField(max_length=255, null=True, blank=True)  # 취업상태
    education_requirement = models.CharField(max_length=255, null=True, blank=True)  # 학력요건
    specialization = models.CharField(max_length=255, null=True, blank=True)  # 특화분야
    region = models.TextField(null=True, blank=True)  # 지역 (데이터가 길어서 TextField)
    region_scope = models.CharField(max_length=50, null=True, blank=True)  # 지역범위
    additional_condition = models.TextField(null=True, blank=True)  # 추가자격조건
    exclusion_criteria = models.TextField(null=True, blank=True)  # 참여제외대상
    operating_org = models.CharField(max_length=100, null=True, blank=True)  # 운영기관명
    other_support_condition = models.TextField(null=True, blank=True)  # 기타지원조건

    def __str__(self):
        return self.title