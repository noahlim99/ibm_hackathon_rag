import os
import logging
import requests
import streamlit as st
from dotenv import load_dotenv

# ================================ 데이터 처리 부분 ================================ #

# 📌 환경 변수 로드
load_dotenv()
RAG_API_URL = "http://localhost:8000/ask/"  # FastAPI RAG 엔드포인트

# 📌 로깅 설정
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=f"{LOG_DIR}/chatbot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 📌 FastAPI RAG 시스템 호출 함수
def call_rag_api(prompt, user_inputs):
    """FastAPI RAG 시스템을 호출하여 사용자 정보를 포함한 응답을 가져오는 함수"""
    if not prompt.strip():
        return "⚠️ 입력된 메시지가 없습니다. 내용을 입력해주세요."

    try:
        payload = {
            "question": prompt,
            "user_system_prompt": "",
            "max_tokens": 500,
            "gender": user_inputs["성별"],
            "age": user_inputs["나이"],
            "category": user_inputs["카테고리"],
        }

        response = requests.post(RAG_API_URL, json=payload)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        response_data = response.json()

        return response_data.get("answer", "🚨 RAG 시스템에서 응답을 받지 못했습니다.")

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ RAG 응답 오류: {str(e)}")
        return "🚨 RAG 시스템과 통신 중 오류가 발생했습니다."
    except Exception as e:
        logging.error(f"❌ 일반 오류: {str(e)}")
        return "🚨 RAG 시스템과 통신 중 오류가 발생했습니다."


# ================================ UI 관련 부분 ================================ #

# 📌 Streamlit 페이지 설정
st.set_page_config(page_title="I'll Be your Mommy", layout="wide")

# 📌 대화 메시지 관리 (session_state에 한 번만 저장)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 📌 사용자 입력값 저장 공간
if "user_inputs" not in st.session_state:
    st.session_state.user_inputs = {"성별": "남자", "나이": 15, "카테고리": "주거"}  # 기본값 설정

# 📌 카테고리 매핑 (UI에 표시되는 값 -> API로 전달되는 값)
CATEGORY_MAPPING = {
    "주거": "주거",
    "일자리": "일자리",
    "금융": "금융",
    "보험": "보험",
    "핸드폰": "통신",  # UI에는 "핸드폰"으로 표시되지만 API에는 "통신"으로 전달
    "지원 제도": "지원 제도"
}

# 📌 🎨 사용자 정보 입력 (사이드바 UI)
st.sidebar.markdown("## 🔹 사용자 정보 입력")
st.session_state.user_inputs["성별"] = st.sidebar.radio("성별을 선택하세요:", ["남자", "여자"], horizontal=True)
st.session_state.user_inputs["나이"] = st.sidebar.selectbox("나이를 선택하세요:", list(range(15, 40)))
selected_category = st.sidebar.selectbox(
    "관심 있는 정보를 선택하세요:", list(CATEGORY_MAPPING.keys())
)
st.session_state.user_inputs["카테고리"] = CATEGORY_MAPPING[selected_category]  # 실제 API로 전달될 값

if st.sidebar.button("🐝 설정 완료", use_container_width=True):
    st.sidebar.success(
        f"🐝 {st.session_state.user_inputs['나이']}세 {st.session_state.user_inputs['성별']}님의 {selected_category} 정보를 제공합니다!"
    )

# 📌 타이틀 및 소개
st.markdown(
    """
    <div style="text-align:center; margin-top:20px;">
        <h2 style="color:gold;">🐝 I'll Be your Mommy (IBM) 🐝</h2>
        <p>🤖 Watsonx.ai 기반 RAG 챗봇</p>
    </div>
    """,
    unsafe_allow_html=True
)

# 📌 사용자 입력창 (질문 입력)
prompt = st.chat_input("질문해주세요!")  # 입력창 표시

if prompt:
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})

    # RAG 시스템 호출
    with st.spinner("🐝 답변을 생성 중입니다..."):
        response = call_rag_api(prompt, st.session_state.user_inputs)

    # AI 응답 메시지를 저장
    st.session_state.messages.append({"role": "assistant", "content": response.strip()})

# 📌 대화 기록을 한 번만 렌더링
for message in st.session_state.messages:
    if message["role"] == "user":  # 사용자 프롬프트
        st.markdown(
            f"""
            <div style="text-align: right; background-color: #E3E3E3; padding: 10px; border-radius: 10px; margin-bottom: 10px; max-width: 70%; margin-left: auto;">
                <strong>Q:</strong> {message['content']}
            </div>
            """,
            unsafe_allow_html=True
        )
    elif message["role"] == "assistant":  # AI 응답
        # 응답을 문단 단위로 나누어 표시
        response_paragraphs = message["content"].split("\n")
        formatted_response = "".join(
            f"<p style='margin-bottom: 10px;'>{paragraph.strip()}</p>"
            for paragraph in response_paragraphs if paragraph.strip()
        )
        st.markdown(
            f"""
            <div style="text-align: left; background-color: #FFD700; padding: 10px; border-radius: 10px; margin-bottom: 10px; max-width: 70%; margin: 0 auto;">
                <strong>A:</strong> {formatted_response}
            </div>
            <hr style="border: 1px solid #ccc; margin: 10px 0;">
            """,
            unsafe_allow_html=True,
        )
