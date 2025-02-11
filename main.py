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
    "decoding_method": DecodingMethods.SAMPLE.value,
    "temperature": 0.5,
    "min_new_tokens": 1,
    "max_new_tokens": 1000,
    "stop_sequences": ["<|endoftext|>"]
}

# 📌 Watsonx.ai 모델 초기화 (최신 모델 사용)
watsonx_model = ModelInference(
    model_id="meta-llama/llama-3-3-70b-instruct",
    credentials=wml_credentials,
    project_id=project_id,
    params=parameters
)

# 📌 ChromaDB 디렉토리 기본 경로
base_persist_directory = os.path.join(os.path.dirname(__file__), "vectorDB")
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 📌 요청 데이터 모델
class QueryRequest(BaseModel):
    prompt: str  # 질문 텍스트를 저장하는 필드
    category: str  # 선택된 카테고리

# ================================ 새로운 Retriever 구현 ================================ #

def retrieve_documents(user_question, category, top_k=5):
    """
    사용자가 선택한 카테고리 내에서 유사한 문서를 검색하는 함수
    """
    category_directory = os.path.join(base_persist_directory, category)
    
    # 🔺 카테고리 디렉토리가 존재하지 않으면 오류 반환
    if not os.path.exists(category_directory):
        return {"error": f"카테고리 '{category}'에 해당하는 데이터가 없습니다."}
    
    # 🔹 벡터 DB 로드 (임베딩 모델 적용)
    vector_db = Chroma(
        persist_directory=category_directory,
        embedding_function=embedding_model  # 🔺 임베딩 적용
    )

    # 🔍 유사한 문서 검색 (최대 top_k개)
    results = vector_db.similarity_search(user_question, k=top_k)

    # 🔺 검색된 문서가 없으면 오류 반환
    if not results:
        return {"error": "검색된 관련 정보가 없습니다. 질문을 조금 더 구체적으로 작성해 주세요!"}

    return results  # 🔹 올바르게 유사 문서만 반환!


# ================================ Watsonx.ai 프롬프트 생성 ================================ #

def generate_prompt(results, user_question):
    """
    검색된 문서를 포함하여 Watsonx.ai에 전달할 최종 프롬프트 생성
    """

    # 📌 검색된 문서 내용을 문자열로 변환
    knowledge_base = "\n\n".join([doc.page_content for doc in results])

    prompt = f"""
당신은 보호종료아동을 돕는 **정직하고 친절한 AI 비서**입니다.  
청소년을 상대하는 만큼, **경쾌하고 신나는 말투**로 말하고, 불필요한 반복 없이 핵심만 전달하세요. 

🔹 **[응답 지침]**  
1. 반드시 아래 제공된 **knowledge base**의 정보만 활용하세요.  
2. **불필요한 반복 없이 핵심 정보만 요약하여 설명**하세요.  
3. **이해하기 쉬운 문장**으로 재구성하고, **사족을 추가하지 마세요.**  
4. 응답은 반드시 "**해요체**"로, 매우 친절하고 상냥한 말투로 작성하세요.  
5. **응답은 700자 이하**로, 중요한 핵심 정보만 담고, 마지막에 말이 중간에 끊기지 않도록 다듬으세요.
6. **불필요한 감탄사 반복 및 인사말은 절대 금지**합니다.  

---
🔍 **다음은 참고해야 할 knowledge base입니다.**  
{knowledge_base}  

💡 **[이제 사용자 질문에 대한 답변을 작성하세요]**  
**질문:** {user_question}  

**답변:**
"""
    return prompt

# ================================ FastAPI 엔드포인트 ================================ #

@app.post("/ask/")
def process_question(request: QueryRequest):
    """질문에 대한 RAG 시스템 응답 생성"""
    category = request.category
    user_question = request.prompt
    logger.info(f"📌 [DEBUG] 카테고리: {category}")
    logger.info(f"📌 [DEBUG] 사용자 질문: {user_question}")

    # 📌 새로운 Retriever를 사용하여 문서 검색 (이제 전체 문서가 아니라 유사 문서만 검색!)
    results = retrieve_documents(user_question, category, top_k=5)

    # 🔺 검색된 문서가 없을 경우 에러 반환
    if isinstance(results, dict) and "error" in results:
        return results

    # 📌 Watsonx.ai 프롬프트 생성
    prompt = generate_prompt(results, user_question)
    logger.info(f"\n🚀 [DEBUG] Watsonx.ai에 전달될 프롬프트:\n{prompt}\n{'='*80}")

    # 📌 Watsonx.ai 호출 및 결과 수집
    try:
        answer = watsonx_model.generate(prompt=prompt)["results"][0]["generated_text"].strip()
        logger.info(f"\n✅ [DEBUG] 최종 답변:\n{answer}\n{'='*80}")
    except Exception as e:
        logger.error(f"Watsonx.ai 요청 중 오류 발생: {str(e)}")
        return {"error": f"Watsonx.ai 요청 중 오류 발생: {str(e)}"}

    # 📌 최종 응답 반환
    return {"answer": answer}
