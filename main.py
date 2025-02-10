from fastapi import FastAPI
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from dotenv import load_dotenv
import os
import logging

# 📌 환경 변수 로드
load_dotenv()

# 📌 FastAPI 앱 초기화
app = FastAPI()

# 📌 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 📌 Watsonx.ai 설정
project_id = os.getenv("PROJECT_ID", None)
wml_credentials = {
    "apikey": os.getenv("API_KEY", None),
    "url": "https://us-south.ml.cloud.ibm.com"
}

parameters = {
    "decoding_method": DecodingMethods.SAMPLE.value,  # Sampling 방식
    "temperature": 0.3,  # 온도
    "top_p": 0.3,  # 상위 P (핵심 샘플링)
    "top_k": 10,  # 상위 K
    "repetition_penalty": 1.5,  # 반복 페널티
    "min_new_tokens": 100,  # 최소 토큰
    "max_new_tokens": 700,  # 최대 토큰
    "stop_sequences": ["<|endoftext|>"]  # 중지 시퀀스
}

# 📌 Watsonx.ai 모델 초기화
watsonx_model = ModelInference(
    model_id="meta-llama/llama-3-3-70b-instruct",
    credentials=wml_credentials,
    project_id=project_id,
    params=parameters
)

# 📌 ChromaDB 설정
base_persist_directory = os.path.join(os.path.dirname(__file__), "vectorDB")
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 벡터DB 로드
vector_db = Chroma(
    persist_directory=base_persist_directory,
    embedding_function=embedding_model
)

# Retriever 생성 (상위 3개 검색)
retriever = vector_db.as_retriever(search_kwargs={"k": 3})

# 📌 요청 데이터 모델
class QueryRequest(BaseModel):
    prompt: str  # 사용자 질문
    category: str  # 선택된 카테고리


def trim_knowledge_base(results, max_tokens=800):
    """검색된 문서를 길이 제한에 맞게 다듬는 함수"""
    knowledge_base = ""
    total_tokens = 0

    for doc in results:
        doc_tokens = len(doc.page_content.split())  # 텍스트를 토큰으로 변환 (단순 단어 수 기준)
        if total_tokens + doc_tokens > max_tokens:
            break
        knowledge_base += doc.page_content + "\n"
        total_tokens += doc_tokens

    return knowledge_base.strip()


def generate_prompt(results, user_question):
    if not results:
        knowledge_base = "관련된 참고 자료를 찾을 수 없습니다. 아래 질문에 대해 최대한 명확히 답변해 주세요."
    else:
        # 중복 제거 및 길이 제한 적용
        knowledge_base = trim_knowledge_base(results, max_tokens=800)

    prompt = f"""
-당신은 보호종료아동을 돕는 **친절한 AI 비서**입니다.  
-**경쾌하고 신나고 상냥한 말투**로, "**해요체**"로 응답하세요.
-반드시 아래 제공된 **knowledge base**의 정보만을 참고하여 응답하세요.

**사용자 질문:**  
"{user_question}"

**당신이 참고해야 하는 문서 (Knowledge Base):**  
{knowledge_base}

**[이제 사용자 질문에 대한 답변을 작성하세요]**
"""
    return prompt

@app.post("/ask/")
def process_question(request: QueryRequest):
    """질문에 대한 RAG 시스템 응답 생성 및 디버깅"""
    # 카테고리와 사용자 질문 조합
    full_prompt = f"{request.category} {request.prompt}"
    logger.info(f"✅ [DEBUG] 생성된 프롬프트: {full_prompt}")

    # 벡터DB 검색
    results = retriever.invoke(full_prompt)

    if not results:
        logger.warning("❌ 검색된 관련 정보가 없습니다.")
        return {
            "error": "검색된 관련 정보가 없습니다. 질문을 조금 더 구체적으로 작성해 주세요!"
        }

    # 디버깅: 검색된 문서 로그 출력
    logger.info(f"✅ [DEBUG] 검색된 문서 (최대 3개):")
    for i, doc in enumerate(results):
        logger.info(f"  📄 문서 {i + 1}: {doc.page_content[:100]}...")  # 문서의 첫 100자 출력
        logger.info(f"  📄 문서 {i + 1} 소스: {doc.metadata.get('source', '출처 없음')}")

    # 프롬프트 생성
    prompt = generate_prompt(results, full_prompt)
    logger.info(f"\n🚀 [DEBUG] Watsonx.ai에 전달될 최종 프롬프트:\n{prompt}\n{'='*80}")

    # Watsonx.ai 호출 및 결과 수집
    try:
        response_data = watsonx_model.generate(prompt=prompt)
        answer = response_data["results"][0]["generated_text"].strip()
        logger.info(f"\n✅ [DEBUG] Watsonx.ai가 생성한 응답:\n{answer}\n{'='*80}")
    except Exception as e:
        logger.error(f"❌ [ERROR] Watsonx.ai 요청 중 오류 발생: {str(e)}")
        return {
            "error": "Watsonx.ai 요청 중 오류 발생",
            "details": str(e)
        }

    # 최종 응답 반환
    logger.info(f"✅ [DEBUG] 사용자에게 전달할 최종 응답:\n{answer}")
    return {"answer": answer}
