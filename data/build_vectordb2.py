"""
ChromaDB 벡터 데이터베이스 구축
전처리된 JSON 데이터를 임베딩하여 벡터 DB에 저장
- vector 검색 정확도
- 시스템 필터링(region / age / status) 지원
"""

import json
import os
from dotenv import load_dotenv
import chromadb
from openai import OpenAI

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


def load_preprocessed_data(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------------
# 1️⃣ Vector Search 용 텍스트 생성
# -------------------------------
def create_policy_text(policy: dict) -> str:
    """
    벡터 검색을 위한 핵심 의미 정보만 포함
    - 행정 서류/신청방법/제출서류는 제외
    """
    parts = []

    if policy.get("정책명"):
        parts.append(f"정책명: {policy['정책명']}")

    if policy.get("대분류") or policy.get("중분류"):
        parts.append(f"분야: {policy.get('대분류','')} > {policy.get('중분류','')}")

    if policy.get("정책설명"):
        parts.append(f"정책설명: {policy['정책설명'][:600]}")

    if policy.get("지원내용"):
        parts.append(f"지원내용: {policy['지원내용'][:800]}")

    if policy.get("정책키워드"):
        parts.append(f"키워드: {policy['정책키워드']}")

    if policy.get("추가자격조건"):
        parts.append(f"자격요약: {policy['추가자격조건'][:300]}")

    # 연령 정보는 의미 검색 보조로만
    min_age = int(policy.get("지원최소연령") or 0)
    max_age = int(policy.get("지원최대연령") or 0)
    if min_age or max_age:
        parts.append(f"대상연령: {min_age}세 ~ {max_age}세")

    if not parts:
        return "청년 정책"

    text = "\n".join(parts)
    return " ".join(text.split())


# -------------------------------
# 2️⃣ Embedding
# -------------------------------
def get_embeddings_batch(texts, model="text-embedding-3-small"):
    cleaned = []
    for t in texts:
        t = t.replace("\n", " ").strip()
        if not t:
            t = "청년 정책"
        cleaned.append(t[:8000])

    response = client.embeddings.create(input=cleaned, model=model)
    return [item.embedding for item in response.data]


# -------------------------------
# 3️⃣ ChromaDB 구축
# -------------------------------
def build_chromadb(policies, db_path="./vectordb2"):
    os.makedirs(db_path, exist_ok=True)
    chroma = chromadb.PersistentClient(path=db_path)

    try:
        chroma.delete_collection("youth_policies")
    except:
        pass

    collection = chroma.create_collection(
        name="youth_policies",
        metadata={"description": "청년이음 정책 벡터 DB"}
    )

    texts = []
    metadatas = []
    ids = []

    for idx, policy in enumerate(policies):
        texts.append(create_policy_text(policy))
        ids.append(f"policy_{idx}")

        # -------------------------------
        # 🔑 System Filtering Metadata
        # -------------------------------
        region_codes = policy.get("region_codes") or {}
        sido_codes = region_codes.get("sido") or []
        sigungu_codes = region_codes.get("sigungu") or []

        metadatas.append({
            # 기본 식별
            "정책명": policy.get("정책명", ""),
            "대분류": policy.get("대분류", ""),
            "중분류": policy.get("중분류", ""),

            # 지역 필터
            "region_scope": policy.get("region_scope", ""),
            "region_sido_codes": json.dumps(sido_codes, ensure_ascii=False),
            "region_sigungu_codes": json.dumps(sigungu_codes, ensure_ascii=False),

            # 상태 필터
            "신청상태": policy.get("신청상태", ""),
            "사업상태": policy.get("사업상태", ""),

            # 연령 필터
            "지원최소연령": int(policy.get("지원최소연령") or 0),
            "지원최대연령": int(policy.get("지원최대연령") or 0),

            # 참고용
            "정책제공방법": policy.get("정책제공방법", ""),
            "재공기관그룹": policy.get("재공기관그룹", ""),
            "주관기관명": policy.get("주관기관명", ""),
            "신청URL": policy.get("신청URL", ""),
            "참고URL1": policy.get("참고URL1", ""),
        })

    # Embedding
    embeddings = []
    batch = 20
    for i in range(0, len(texts), batch):
        embeddings.extend(get_embeddings_batch(texts[i:i+batch]))

    collection.add(
        documents=texts,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings
    )

    return collection


# -------------------------------
# 4️⃣ 실행
# -------------------------------
def main():
    if not OPENAI_API_KEY:
        print("OPENAI_API_KEY not set")
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "youth_policies_filtered_kr_revised2.json")

    if not os.path.exists(data_path):
        print(f"파일을 찾을 수 없습니다: {data_path}")
        return

    policies = load_preprocessed_data(data_path)
    print(f"Loaded {len(policies)} policies")

    build_chromadb(policies)
    print("ChromaDB build completed")


if __name__ == "__main__":
    main()
