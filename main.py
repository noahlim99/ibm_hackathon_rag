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
    "max_new_tokens": 900,  # 생성 최대 토큰
    "min_new_tokens": 0,  # 생성 최소 토큰
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

# Retriever 생성 (상위 3개 검색)
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
너는 청년들 중에서도 가난하고 능력이 없는 이들을 위한 한글 외에는 전혀 모르는 도우미야.
답변할 때 너가 지켜야 하는 사항을 알려줄게.

1. 최대한 쉬운 단어로 풀어서 설명해. 너에게 질문하는 사람들은 기초 지식이 매우 낮아. 단어들을 중학생도 이해하기 쉬운 말로 대체해서 의미를 풀어서 설명해줘.
2. 답변이 600자를 초과해선 안돼. 너의 글을 읽는 사람들은 긴 글을 못 읽어. 최대한 핵심만 요약해서 정리해.
3. 존댓말 형식을 유지하면서 친근감 있는 말투를 사용해줘.
4. 절대로 한글 이외의 문자를 사용해선 안돼. 예를 들면 자세히를 仔細히라고 하면 절대로 안돼. 무조건 자세히라고 해. 사람들은 한자, 일본어를 전혀 몰라.
5. 가난한 사람들을 대상으로 하기 때문에 답변을 할 때 어느 정도 자산이 있어야 도움이 되는 정보는 최대한 배제해.
6. 질문자들은 이력, 경력, 인맥이 전혀 없는 사람들이야. 일자리 관련 조언을 해줄 때 국가에서 운영하는 교육 프로그램, 지원제도를 우선적으로 알려줘.
7. 정부가 운영하는 제도들을 설명할 때는 신청 절차, 관련 연락망을 필수로 포함해.
8. 사회 초년생들을 대상으로 하기 때문에 답변을 할 때 최대한 경력, 능력이 전혀 없어도 도전할 만한 일들을 추천해줘.
9. 질문자들은 돈이 전혀 없기 때문에, 집을 구할 때 국가에서 주는 지원금을 우선적으로 알려줘.
10. 아르바이트를 추천하기보다 아르바이트를 얻는 법을 자세하게 알려줘.
11. 같은 문장이 중복되는 일은 절대로 없어야 해. 토큰이 남았더라도, 너가 준비한 말이 끝나면 그냥 멈춰. 했던 말 반복하지 말고.
12. 너에게 질문을 하는 사람들은 불쌍한 사람들이기 때문에, 용기를 북돋아줘야 하는 대상이야. 답변의 마지막에 가독성을 해치지 않는 선에서 격려하는 멘트를 적어주면 좋겠어.

**사용자 질문:**  
"{user_question}"

**참고 자료 (Knowledge Base):**  
{knowledge_base}
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
