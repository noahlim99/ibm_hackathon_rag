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
    "decoding_method": DecodingMethods.GREEDY.value,  # Greedy 방식 적용
    "max_new_tokens": 700,  # 생성 최대 토큰
    "min_new_tokens": 300,  # 생성 최소 토큰
    "repetition_penalty": 1,  # 반복 패널티
    "stop_sequences": ["<|endoftext|>"]  # 중지 시퀀스
}

# 📌 Watsonx.ai 모델 초기화 (ModelInference 방식)
watsonx_model = ModelInference(
    model_id="meta-llama/llama-3-3-70b-instruct",
    credentials=wml_credentials,
    project_id=project_id,
    params=parameters
)

# 📌 ChromaDB 설정
base_persist_directory = os.path.join(os.path.dirname(__file__), "vectorDB")
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en")

# 벡터DB 로드
vector_db = Chroma(
    persist_directory=base_persist_directory,
    embedding_function=embedding_model
)

# Retriever 생성 (상위5개 검색)
retriever = vector_db.as_retriever(search_kwargs={"k": 5})

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

    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
당신은 보호종료아동을 대상으로 답변하는 친절하고 정확한 AI 비서입니다.
답변할 때 다음의 규칙을 반드시 모두 지켜주세요.

-이해하기 쉬운 말로 설명하고, 핵심을 요약해서 설명해주세요.
-조언 시, 국가에서 운영하는 교육 프로그램, 지원제도를 우선적으로 알려주고, 그러한 제도들을 설명할 때는 신청 절차, 관련 연락망을 필수로 포함하세요.
-주거에 관한 조언을 구할 때 국가에서 주는 지원금을 우선적으로 알려주세요.
-같은 의미가 중복되는 단어와 문장의 반복은 절대 금지입니다. 토큰이 남았더라도, 준비한 말이 끝나면 멈추세요.
-상냥하고 친절한 말투로, "해요체"를 사용해주세요.
-답변은 다음의 검색된 정보에 기반하여 답변합니다.

### 검색된 정보:  
{knowledge_base}

**사용자 질문:**  
"{user_question}"

### 답변:
- **핵심 정보**: 
- **추가 설명**: 
- **관련 정보**: 


ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
    return prompt


@app.post("/ask/")
def process_question(request: QueryRequest):
    """질문에 대한 RAG 시스템 응답 생성 및 Watsonx.ai 호출"""
    full_prompt = f"{request.category} {request.prompt}"
    logger.info(f"✅ [DEBUG] 생성된 프롬프트: {full_prompt}")

    # 벡터DB 검색
    results = retriever.invoke(full_prompt)

    if not results:
        logger.warning("❌ 검색된 관련 정보가 없습니다.")
        return {
            "error": "검색된 관련 정보가 없습니다. 질문을 조금 더 구체적으로 작성해 주세요!"
        }

    # 프롬프트 생성
    prompt = generate_prompt(results, full_prompt)
    logger.info(f"\n🚀 [DEBUG] Watsonx.ai에 전달될 최종 프롬프트:\n{prompt}\n{'='*80}")

    # Watsonx.ai 호출 (ModelInference 방식)
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

    return {"answer": answer}
