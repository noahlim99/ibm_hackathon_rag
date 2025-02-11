import os
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods

# 📌 환경 변수 로드
load_dotenv()

# 📌 FastAPI 앱 초기화
app = FastAPI()

# 📌 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 📌 Watsonx.ai 설정
project_id = os.getenv("PROJECT_ID", None)
wml_credentials = {
    "apikey": os.getenv("API_KEY", None),
    "url": "https://us-south.ml.cloud.ibm.com"
}

parameters = {
    "decoding_method": DecodingMethods.GREEDY.value,
    "max_new_tokens": 700,
    "min_new_tokens": 300,
    "repetition_penalty": 1,
    "stop_sequences": ["<|endoftext|>"]
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


def get_category_vector_db(category):
    """
    카테고리에 맞는 벡터DB를 로드하는 함수
    """
    category_db_path = os.path.join(base_persist_directory, category)
    
    if not os.path.exists(category_db_path):
        logger.warning(f"❌ 벡터DB 없음: {category}")
        return None
    
    return Chroma(
        persist_directory=category_db_path,
        embedding_function=embedding_model
    ).as_retriever(search_kwargs={"k": 5})  # 상위 5개 검색


# 📌 요청 데이터 모델
class QueryRequest(BaseModel):
    prompt: str  # 사용자 질문
    category: str  # 선택된 카테고리


def trim_knowledge_base(results, max_tokens=800):
    """검색된 문서를 길이 제한에 맞게 다듬는 함수"""
    knowledge_base = ""
    total_tokens = 0

    for doc in results:
        doc_tokens = len(doc.page_content.split())
        if total_tokens + doc_tokens > max_tokens:
            break
        knowledge_base += doc.page_content + "\n"
        total_tokens += doc_tokens

    return knowledge_base.strip()


def generate_prompt(results, user_question):
    """검색된 문서를 기반으로 AI 프롬프트 생성"""
    if not results:
        knowledge_base = "관련된 참고 자료를 찾을 수 없습니다. 아래 질문에 대해 최대한 명확히 답변해 주세요."
    else:
        knowledge_base = trim_knowledge_base(results, max_tokens=800)

    return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
당신은 보호종료아동을 대상으로 답변하는 친절하고 정확한 AI 비서입니다.
답변할 때 다음의 규칙을 반드시 모두 지켜주세요.

- 이해하기 쉬운 말로 설명하고, 핵심을 요약해서 설명해주세요.
- 조언 시, 국가에서 운영하는 교육 프로그램, 지원제도를 우선적으로 알려주고, 신청 절차와 연락망을 포함하세요.
- 주거 관련 조언을 할 때 국가 지원금을 우선적으로 안내하세요.
- 같은 의미가 중복되는 문장의 반복은 금지합니다.
- 상냥하고 친절한 말투로, "해요체"를 사용해주세요.
- 답변은 다음의 검색된 정보에 기반하여 작성됩니다.

### 검색된 정보:  
{knowledge_base}

**사용자 질문:**  
"{user_question}"

### 답변:
- **핵심 정보**: 
- **추가 설명**: 
- **관련 정보**: 
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""


def clean_category(category):
    """
    카테고리 이름에서 이모지 및 공백 제거 (벡터DB 폴더명과 일치하도록 수정)
    """
    category_mapping = {
        "주거": "주거",
        "일자리": "일자리",
        "금융": "금융",
        "보험": "보험",
        "휴대폰": "휴대폰",
        "지원제도": "지원제도"
    }
    
    cleaned_category = category.translate(str.maketrans('', '', "🏠💼💰🛡️📱🆘")).strip()
    return category_mapping.get(cleaned_category, cleaned_category)


@app.post("/ask/")
def process_question(request: QueryRequest):
    """질문에 대한 RAG 시스템 응답 생성 및 Watsonx.ai 호출"""
    
    # ✅ 1. 선택된 카테고리 로그
    cleaned_category = clean_category(request.category)
    logger.info(f"🟡 선택된 카테고리: {cleaned_category}")

    # ✅ 2. 사용자 질문 로그
    logger.info(f"🟡 사용자 질문: {request.prompt}")

    # ✅ 3. 벡터DB 로드
    retriever = get_category_vector_db(cleaned_category)
    if retriever is None:
        return {"error": f"❌ 해당 카테고리({cleaned_category})에 대한 데이터가 없습니다!"}

    # ✅ 4. 검색된 문서 확인
    results = retriever.invoke(request.prompt)
    if not results:
        logger.warning("❌ 검색된 문서 없음")
        return {"error": "검색된 관련 정보가 없습니다. 질문을 조금 더 구체적으로 작성해 주세요!"}

    logger.info(f"🟡 검색된 문서 개수: {len(results)}")
    logger.info(f"🟡 검색된 문서: {results}")

    # ✅ 5. AI 응답 생성
    prompt = generate_prompt(results, request.prompt)
    try:
        response_data = watsonx_model.generate(prompt=prompt)
        answer = response_data["results"][0]["generated_text"].strip()
        logger.info(f"🟡 AI 최종 응답: {answer}")
    except Exception as e:
        logger.error(f"❌ AI 생성 오류: {str(e)}")
        return {"error": "Watsonx.ai 요청 중 오류 발생", "details": str(e)}

    return {"category": cleaned_category, "answer": answer}
