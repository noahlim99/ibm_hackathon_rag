import streamlit as st
import requests

# 📌 FastAPI RAG 시스템 엔드포인트 설정
RAG_API_URL = "http://localhost:8030/ask/"  # FastAPI 서버 URL

# 📌 세션 상태 초기화
if "page" not in st.session_state:
    st.session_state.page = "start"
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None
if "messages" not in st.session_state:
    st.session_state.messages = []  # 대화 기록 저장

# 🌟 1. 시작 화면
if st.session_state.page == "start":
    st.title("I'll Be your Mate!")
    if st.button("시작!"):
        st.session_state.page = "name_input"
        st.rerun()

# 🌟 2. 사용자 이름 입력
elif st.session_state.page == "name_input":
    st.markdown("## 이름을 알려주세요!")

    def set_user_name():
        if st.session_state.name:
            st.session_state.user_name = st.session_state.name
            st.session_state.page = "home"

    st.text_input("이름을 입력하세요", key="name", on_change=set_user_name)

# 🌟 3. 홈 화면 (메인 메뉴)
elif st.session_state.page == "home":
    user_name = st.session_state.user_name or "사용자"
    st.markdown(f"## 환영해요, {user_name}님!😊\n\n무엇을 해볼까요?")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("☕️ 수다 떨기 ☕️"):
            st.session_state.page = "chat"
            st.rerun()

    with col2:
        if st.button("💕 고민 상담 💕"):
            st.session_state.page = "counseling"
            st.rerun()

    with col3:
        if st.button("🍔 맛집 탐방 🍔"):
            st.session_state.page = "food"
            st.rerun()

# 🌟 4. 고민 상담 카테고리 선택
elif st.session_state.page == "counseling":
    st.markdown("## 어떤 고민인가요 ?")
    
    categories = ["주거", "일자리", "금융", "보험", "휴대폰", "지원 제도", "심리 상담"]
    cols = st.columns(len(categories))

    for i, category in enumerate(categories):
        if cols[i].button(category):
            st.session_state.selected_category = category
            st.session_state.messages = []  # 새 카테고리 선택 시 대화 초기화
            st.session_state.page = "chat_counseling"
            st.rerun()

    if st.button("🏠 처음으로"):
        st.session_state.page = "home"
        st.rerun()

# 🌟 5. 고민 상담 채팅 (FastAPI RAG 시스템 연동)
elif st.session_state.page == "chat_counseling":
    category = st.session_state.selected_category or "고민"
    st.markdown(f"## 💬 {category} 고민을 해결해 드릴게요!")

    prompt = st.chat_input("질문을 입력하세요!")

    if prompt:
        # 사용자 질문 저장
        st.session_state.messages.append({"role": "user", "content": prompt})

        # FastAPI 호출 (RAG 시스템)
        with st.spinner("☁️ 답변을 생성 중입니다! ☁️"):
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

    # 대화 기록 렌더링
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

    if st.button("🏠 처음으로"):
        st.session_state.page = "home"
        st.session_state.messages = []
        st.rerun()

