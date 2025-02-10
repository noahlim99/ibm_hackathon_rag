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

# Watsonx.ai 모델 초기화 (최신 모델 사용)
watsonx_model = ModelInference(
    model_id="meta-llama/llama-3-3-70b-instruct",
    credentials=wml_credentials,
    project_id=project_id,
    params=parameters
)

# ChromaDB 디렉토리 기본 경로
base_persist_directory = os.path.join(os.path.dirname(__file__), "vectorDB")
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 📌 요청 데이터 모델
class QueryRequest(BaseModel):
    prompt: str  # 질문 텍스트를 저장하는 필드
    category: str  # 선택된 카테고리

# ================================ 시스템 프롬프트 ================================ #

def trim_knowledge_base(results, max_tokens=700):
    """검색된 문서를 길이 제한에 맞게 다듬는 함수"""
    knowledge_base = ""
    total_tokens = 0

    for doc in results:
        doc_tokens = len(doc.page_content.split())  # 텍스트를 단어 기준으로 토큰화
        if total_tokens + doc_tokens > max_tokens:
            # 초과되는 경우, 필요한 만큼만 잘라서 추가
            remaining_tokens = max_tokens - total_tokens
            knowledge_base += " ".join(doc.page_content.split()[:remaining_tokens]) + "\n"
            break
        knowledge_base += doc.page_content + "\n"
        total_tokens += doc_tokens

    return knowledge_base.strip()

def generate_prompt(results, user_question):
    """검색된 문서를 포함한 최종 Watsonx.ai 프롬프트 생성"""

    if not results:
        knowledge_base = "관련된 참고 자료를 찾을 수 없습니다. 아래 질문에 대해 최대한 명확히 답변해 주세요."
    else:
        # 700토큰 제한 적용
        knowledge_base = trim_knowledge_base(results, max_tokens=700)

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
📌 **[반드시 지켜야 할 응답 형식]**  
💡 **아래의 형식 그대로 답변해야 합니다.**  

✅ **[응답 예시]**  
**질문:** "보호종료아동이 지원받을 수 있는 혜택이 뭐야?"  

**답변:**  
보호종료아동이 받을 수 있는 지원 혜택에 대해 알려드릴게요!!

📌 **1. 자립정착금**  
- 일정 금액을 지급받아 안정적으로 생활을 시작할 수 있어요!  

📌 **2. 주거 지원**  
- LH 공공임대주택 우선 입주, 월세 지원 등이 가능해요!  

📌 **3. 취업 및 학업 지원**  
- 직업훈련, 대학 등록금 지원 등 다양한 혜택이 제공돼요!

더 궁금한 점이 있다면 물어봐주세요 😊 
---
🔍 **다음은 참고해야 할 knowledge base입니다.**  
{knowledge_base}  

💡 **[이제 사용자 질문에 대한 답변을 작성하세요]**  
**질문:** {user_question}  

**답변:**
"""
    return prompt


# ================================ 후처리 함수 ================================ #

def remove_redundant_phrases(answer):
    """중복된 문구 및 의미적으로 유사한 표현 제거"""
    lines = answer.split("\n")
    unique_lines = []
    seen_phrases = set()

    for line in lines:
        cleaned_line = line.strip()

        # 의미적으로 유사한 문장이 반복될 경우 제거
        if any(cleaned_line in seen for seen in seen_phrases) or cleaned_line in unique_lines:
            continue

        unique_lines.append(cleaned_line)
        seen_phrases.add(cleaned_line[:20])  # 문장의 앞 20자만 저장하여 중복 감지 강화

    return "\n".join(unique_lines)


def fetch_full_answer(prompt):
    """Watsonx.ai로부터 응답을 받아 중복 제거 후 최적화된 답변 생성"""
    full_answer = ""
    max_iterations = 4  # 반복 횟수를 늘려 더 긴 응답을 생성
    iteration = 0
    seen_sentences = set()  # 중복 감지용 집합
    last_answer = ""

    while iteration < max_iterations:
        response_data = watsonx_model.generate(prompt=prompt)
        partial_answer = response_data["results"][0]["generated_text"].strip()

        # 응답이 없거나, 너무 짧을 경우 추가 호출
        if not partial_answer or len(partial_answer) < 50:
            iteration += 1
            continue

        # 동일한 응답 반복 방지
        if partial_answer == last_answer:
            iteration += 1
            continue
        last_answer = partial_answer

        # 중복 제거
        sentences = partial_answer.split("\n")
        filtered_sentences = [s for s in sentences if s.strip() and s.strip() not in seen_sentences]
        seen_sentences.update(filtered_sentences)

        full_answer += "\n".join(filtered_sentences) + "\n"

        # 응답 길이 제한 & 종료 조건 확인
        if len(full_answer) > 700 or any(s.endswith(("😊", ".", "!", "?")) for s in filtered_sentences):
            break

        iteration += 1

    return remove_redundant_phrases(full_answer)


# ================================ FastAPI 엔드포인트 ================================ #

@app.post("/ask/")
def process_question(request: QueryRequest):
    """질문에 대한 RAG 시스템 응답 생성"""
    category = request.category
    user_question = request.prompt
    logger.info(f"📌 [DEBUG] 카테고리: {category}")
    logger.info(f"📌 [DEBUG] 사용자 질문: {user_question}")

    # 카테고리 디렉토리 확인
    category_directory = os.path.join(base_persist_directory, category)
    if not os.path.exists(category_directory):
        return {"error": f"카테고리 '{category}'에 해당하는 데이터가 없습니다."}

    # 벡터DB 로드 및 검색
    vector_db = Chroma(persist_directory=category_directory, embedding_function=embedding_model)
    results = vector_db.similarity_search(user_question, k=5)
    if not results:
        return {"error": "검색된 관련 정보가 없습니다. 질문을 조금 더 구체적으로 작성해 주세요!"}

    # 프롬프트 생성
    prompt = generate_prompt(results, user_question)
    logger.info(f"\n🚀 [DEBUG] Watsonx.ai에 전달될 프롬프트:\n{prompt}\n{'='*80}")

    # Watsonx.ai 호출 및 결과 수집
    try:
        answer = fetch_full_answer(prompt)  # 완전한 응답 수집
        logger.info(f"\n✅ [DEBUG] 최종 답변:\n{answer}\n{'='*80}")
    except Exception as e:
        logger.error(f"Watsonx.ai 요청 중 오류 발생: {str(e)}")
        return {"error": f"Watsonx.ai 요청 중 오류 발생: {str(e)}"}

    # 최종 응답 반환
    return {"answer": answer} 