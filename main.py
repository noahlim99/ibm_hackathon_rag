from fastapi import FastAPI
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from dotenv import load_dotenv
import os

# 📌 환경 변수 로드
load_dotenv()

# 📌 FastAPI 앱 초기화
app = FastAPI()

# 📌 Watsonx.ai 설정
project_id = os.getenv("PROJECT_ID", None)
wml_credentials = {
    "apikey": os.getenv("API_KEY", None),
    "url": "https://us-south.ml.cloud.ibm.com"
}

parameters = {
    "decoding_method": DecodingMethods.GREEDY.value,
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

# ChromaDB 초기화 (벡터DB 설정)
persist_directory = "/home/ibmuser01/team5_beta/chromadb_sqlite"
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)
retriever = vector_db.as_retriever(search_kwargs={"k": 3}) 

# 요청 데이터 모델 정의
class QueryRequest(BaseModel):
    question: str
    user_system_prompt: str = ""  
    max_tokens: int = 1000  
    gender: str
    age: int
    category: str
    
# ================================ 시스템 프롬프트 ================================ #

def generate_prompt(results, user_question):
    """ 검색된 문서를 포함한 최종 Watsonx.ai 프롬프트 생성 """

    knowledge_base = "\n".join(doc.page_content for doc in results)  # 검색된 문서 추가

    prompt = f"""
당신은 정직한 AI 비서이자, 당신의 고객은 보육원에서 나온 보호종료아동이에요.
청소년들에게 설명하는 것인 만큼, **매우 친절하고 상냥하게**, 그리고 **구체적으로 답변**해주세요.

🔹 **지시사항**:
- 반드시 아래 **knowledge base**를 기반으로 답변하세요.
- **추가적인 가정이나 추측**을 하지 마세요.
- 문단 사이에는 **공백을 추가**하여 가독성을 높이세요.

🔍 **다음은 참고해야 할 knowledge base입니다.**:
{knowledge_base}

---
📌 **응답 형식**:
1. 사용자의 질문에 대해 **상냥하고 구체적이고 친절한 답변**을 제공하고, 해요체를 쓰세요.
2. **추가로 도움이 될 만한 관련 질문과 답변을 **3~5개** 생성하세요.
3. 같은 내용의 질문이 반복되지 않도록 **주의하세요**.
4. 다음 형식을 따르세요:
---
💬 **메인 답변**:
[사용자의 질문에 대한 구체적인 답변]

=========================================
❓ 질문: [관련 질문 1]
💬 답변: [관련 질문 1에 대한 답변]

❓ 질문: [관련 질문 2]
💬 답변: [관련 질문 2에 대한 답변]


---
❓ **사용자의 질문**: {user_question}
💬 **답변**:
"""
    return prompt


@app.post("/ask/")
def process_question(request: QueryRequest):
    """RAG 시스템을 통해 질문에 대한 응답을 생성"""

    print(f"\n📌 [DEBUG] 사용자 질문: {request.question}")

    retriever_input = (
        f"{request.age}세 {request.gender} "
        f"{request.category} : {request.question}"
    )

    print(f"\n🔍 [DEBUG] retriever에 입력된 최종 검색 키워드:\n{retriever_input}\n{'='*50}")

    results = retriever.get_relevant_documents(retriever_input)

    print("\n🔎 [DEBUG] 검색된 관련 문서 목록:")
    for idx, doc in enumerate(results, start=1):
        source = doc.metadata.get("source", "출처 없음")
        content_preview = doc.page_content[:300]  # 문서 내용 앞 300자 미리보기
        print(f"\n📄 문서 {idx}: {source}\n📜 내용 미리보기:\n{content_preview}\n{'-'*50}")

    retrieved_docs = [{"source": doc.metadata.get("source", "출처 없음"), "content": doc.page_content[:300]} for doc in results]

    # Watsonx.ai에 전달할 프롬프트 생성
    prompt = generate_prompt(results, request.question)

    print(f"\n🚀 [DEBUG] Watsonx.ai에 전달될 최종 프롬프트:\n{prompt}\n{'='*80}")

    try:
        response_data = watsonx_model.generate(prompt=prompt)
        answer = response_data["results"][0]["generated_text"].strip()
        
        # 디버깅용: Watsonx.ai 응답 출력
        print(f"\n✅ [DEBUG] LLM이 생성한 답변:\n{answer}\n{'='*80}")

    except Exception as e:
        answer = f"⚠️ Watsonx.ai 요청 중 오류 발생: {str(e)}"

    # 기본 안내 문구 추가
    answer += """
=========================================
📞 관련 기관 문의: 123-456-7890\n🌐 홈페이지: www.example.com"
💕 당신의 힘찬 내일을 응원합니다 💕
"""
    # 디버깅용: 최종 응답 출력
    print(f"\n✅ [DEBUG] Streamlit으로 전달될 최종 응답:\n{answer}\n{'='*80}")

    return {"question": request.question, "answer": answer, "retrieved_docs": retrieved_docs}