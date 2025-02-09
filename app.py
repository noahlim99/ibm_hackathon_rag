import streamlit as st
import requests

# 📌 FastAPI RAG 시스템 엔드포인트 설정
RAG_API_URL = "http://localhost:8000/ask/"  # FastAPI 서버 URL

# 📌 세션 상태 초기화
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None  # 카테고리 선택 전 상태

if "messages" not in st.session_state:
    st.session_state.messages = []  # 대화 기록 저장

# 📌 제목 및 설명
st.markdown("## I'll Be Your Mommy")
st.markdown("#### 원하는 카테고리를 선택하고 질문을 입력하세요.")

# 📌 카테고리 버튼 UI
st.markdown("### 🏷️ 카테고리 선택")
categories = ["주거", "일자리", "금융", "보험", "휴대폰", "지원 제도", "심리 상담"]

# 버튼 표시
selected = st.columns(len(categories))
for i, category in enumerate(categories):
    if selected[i].button(category):
        if st.session_state.selected_category != category:
            st.session_state.selected_category = category
            st.session_state.messages = []  # 카테고리 변경 시 대화 초기화
        st.success(f"선택된 카테고리: {category}")

# 📌 질문 입력창 표시
if st.session_state.selected_category:
    prompt = st.chat_input("질문을 입력하세요!")

    if prompt:
        # 사용자 질문 저장
        st.session_state.messages.append({"role": "user", "content": prompt})

        # FastAPI 호출 (RAG 시스템)
        with st.spinner("🐝 답변을 생성 중입니다..."):
            try:
                response = requests.post(
                    RAG_API_URL,
                    json={
                        "prompt": prompt,
                        "category": st.session_state.selected_category
                    }
                )
                response.raise_for_status()
                response_data = response.json()
                answer = response_data.get("answer", "🚨 RAG 시스템에서 응답을 받지 못했습니다.")
            except requests.exceptions.RequestException as e:
                answer = f"🚨 오류 발생: {str(e)}"

        # RAG 응답 저장
        st.session_state.messages.append({"role": "assistant", "content": answer})

# 📌 대화 기록 렌더링
if st.session_state.messages:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f"""
                <div style='text-align: right; background-color: #E3E3E3; padding: 10px; border-radius: 10px; margin-bottom: 10px; max-width: 70%; margin-left: auto;'>
                    <strong>Q:</strong> {message['content']}
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif message["role"] == "assistant":
            st.markdown(
                f"""
                <div style='text-align: left; background-color: #FFD700; padding: 10px; border-radius: 10px; margin-bottom: 10px; max-width: 70%; margin: 0 auto;'>
                    <strong>A:</strong> {message['content']}
                </div>
                """,
                unsafe_allow_html=True,
            )
