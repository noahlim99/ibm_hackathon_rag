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

# 📌 로깅 설정 (로그를 보기 쉽게 설정)
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

# 📌 Watsonx.ai 모델 초기화 (FastAPI 시작 시 로드)
@app.on_event("startup")
def load_watsonx_model():
    global watsonx_model
    watsonx_model = ModelInference(
        model_id="meta-llama/llama-3-3-70b-instruct",
        credentials=wml_credentials,
        project_id=project_id,
        params=parameters
    )
    logger.info("✅ Watsonx.ai 모델이 성공적으로 로드되었습니다.")

# 📌 ChromaDB 설정
base_persist_directory = os.path.join(os.path.dirname(__file__), "vectorDB")
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en")


def get_category_vector_db(category):
    """카테고리에 맞는 벡터DB 로드"""
    category_db_path = os.path.join(base_persist_directory, category.strip())
    logger.info(f"📌 벡터DB 경로 확인: {category_db_path}")

    if not os.path.exists(category_db_path):
        logger.warning(f"❌ 벡터DB 없음: {category}")
        return None

    logger.info(f"✅ 벡터DB 로드 성공: {category}")
    return Chroma(
        persist_directory=category_db_path,
        embedding_function=embedding_model
    ).as_retriever(search_kwargs={"k": 5})  # 상위 5개 검색


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

- 최대한 쉬운 단어로 풀어서 설명하세요. 너에게 질문하는 사람들은 기초 지식이 매우 낮습니다. 단어들을 중학생도 이해하기 쉬운 말로 대체해서 의미를 풀어서 설명해주세요.
- 조언 시, 국가에서 운영하는 교육 프로그램, 지원제도를 우선적으로 알려주고, 신청 절차와 연락망을 포함하세요.
- 주거 관련 조언을 할 때 국가 지원금을 우선적으로 안내하세요.
- 일자리 관련 조언 시. 질문자가 이력, 능력, 인맥이 전혀 없다고 생각하세요. 교육 프로그램, 상담 프로그램 등 지원제도를 먼저 추천하세요.
- 같은 의미가 중복되는 문장의 반복은 금지합니다.
- 상냥하고 친절한 말투로, "해요체"를 사용해주세요.
- 한글 이외의 문자 표기는 절대금지입니다. 예를 들면 자세히를 仔細히라고 하면 절대로 안됩니다. 무조건 자세히라고 해야합니다.
- 답변은 다음의 검색된 정보에 기반하여 작성됩니다.
- 질문자들은 이력, 경력, 인맥이 전혀 없는 사람들입니다. 이력서와 인맥을 잘 쌓으라고 추천하지 마세요.
- 조언 시, 그냥 제도만 알려주기보다 방법을 더욱 자세히 설명해주세요. 예를 들어 아르바이트를 추천하기보다 아르바이트를 얻는 법을 자세하게 알려주세요.
- 질문자가 물어본 것에만 대답하세요. 관련없는 대답은 금지입니다.
- 일자리와 보험은 관련 없는것입니다. 보험과 주거는 관련 없는것입니다. 휴대폰과 일자리는 관련 없는것입니다.

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


@app.post("/ask/")
def process_question(request: QueryRequest):
    """질문에 대한 RAG 시스템 응답 생성 및 Watsonx.ai 호출"""

    # ✅ FastAPI에서 받은 데이터 확인
    cleaned_category = request.category.strip()
    logger.info(f"📌 FastAPI에서 받은 category: '{cleaned_category}' (길이: {len(cleaned_category)})")
    logger.info(f"📌 사용자 질문: {request.prompt}")

    # ✅ 벡터DB 로드
    retriever = get_category_vector_db(cleaned_category)
    if retriever is None:
        logger.error(f"❌ 벡터DB를 찾을 수 없음: {cleaned_category}")
        return {
            "category": cleaned_category,
            "retrieved_context": "해당 카테고리에 대한 데이터가 없습니다.",
            "answer": "현재 해당 카테고리에 대한 문서가 없습니다."
        }

    # ✅ 벡터DB에서 문서 검색
    results = retriever.invoke(request.prompt)
    logger.info(f"🔎 검색된 문서 개수: {len(results)}")

    if not results:
        logger.warning(f"❌ 검색된 문서 없음 (카테고리: {cleaned_category}, 질문: {request.prompt})")
        return {
            "category": cleaned_category,
            "retrieved_context": "검색된 문서 없음",
            "answer": "관련 정보를 찾을 수 없습니다."
        }

    # ✅ 검색된 문서 내용 로그 출력
    retrieved_context = "\n\n---\n\n".join([doc.page_content[:500] for doc in results])[:2000]
    logger.info(f"✅ 검색된 문서 내용 (첫 500자): {retrieved_context[:500]}")

    # ✅ AI 응답 생성
    prompt = generate_prompt(results, request.prompt)

    try:
        response_data = watsonx_model.generate(prompt=prompt)
        answer = response_data["results"][0]["generated_text"].strip()
        logger.info(f"🟡 AI 최종 응답: {answer}")
    except Exception as e:
        logger.error(f"❌ AI 생성 오류: {str(e)}")
        return {
            "category": cleaned_category,
            "retrieved_context": retrieved_context,
            "answer": "AI 응답을 생성하는 중 오류가 발생했습니다."
        }

    return {
        "category": cleaned_category,
        "retrieved_context": retrieved_context,
        "answer": answer
    }
