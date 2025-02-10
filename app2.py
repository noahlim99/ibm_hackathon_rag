import streamlit as st
import streamlit.components.v1 as components

# 🌥️ 세션 상태 초기화
if "page" not in st.session_state:
    st.session_state.page = "start"
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None
if "trigger_rerun" not in st.session_state:
    st.session_state.trigger_rerun = False  # 리렌더링 플래그

# 🌤️ 웹 페이지 설정
st.set_page_config(page_title="IBM 챗봇", page_icon="☁️", layout="centered")

# 🌥️ 1. 로고 화면
if st.session_state.page == "start":
    st.image("https://via.placeholder.com/300x150?text=IBM+Chatbot", use_container_width=True)
    if st.button("클릭하여 시작하기 ☁️"):
        st.session_state.page = "userinfo"

# 🌤️ 2. 사용자 정보 입력 (Enter 입력 가능)
elif st.session_state.page == "userinfo":
    st.markdown("## IBM에 오신 것을 환영합니다!😊")

    def update_name():
        """사용자가 이름을 입력하면 자동으로 페이지를 변경"""
        if st.session_state.name:
            st.session_state.user_name = st.session_state.name
            st.session_state.page = "home"
            st.session_state.trigger_rerun = True  # 트리거 설정

    # 이름 입력 후 Enter를 누르면 자동으로 다음 화면으로 이동
    st.text_input("이름이 무엇인가요?", key="name", on_change=update_name)

    # 리렌더링 필요하면 rerun
    if st.session_state.trigger_rerun:
        st.session_state.trigger_rerun = False  # 플래그 초기화
        st.rerun()

# ☀️ 3. 메인 메뉴 (구름 버튼)
elif st.session_state.page == "home":
    user_name = st.session_state.user_name or "사용자"
    st.markdown(f"## 🌟 환영해요, {user_name}님!")
    st.write("무엇을 해볼까요?")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("☁️ 수다 떨기"):
            st.session_state.page = "chat"
            st.rerun()

    with col2:
        if st.button("☁️ 고민 상담"):
            st.session_state.page = "counseling"
            st.rerun()

    with col3:
        if st.button("☁️ 맛집 탐방"):
            st.session_state.page = "food"
            st.rerun()


# 🌥️ 4. 고민 상담 카테고리 선택
elif st.session_state.page == "counseling":
    st.markdown("## 🧐 어떤 고민이 있으신가요?")
    
    categories = ["🏠 주거", "💼 일자리", "💰 금융", "🛡️ 보험", "📱 휴대폰", "🆘 지원 제도", "🧠 심리 상담"]
    
    for category in categories:
        if st.button(category, key=category):
            st.session_state.selected_category = category
            st.session_state.page = "chat_counseling"
            st.rerun()

    if st.button("🏠 처음으로"):
        st.session_state.page = "home"
        st.rerun()

# 🌤️ 5. 고민 상담 채팅창 (RAG 연결)
elif st.session_state.page == "chat_counseling":
    category = st.session_state.selected_category or "고민"
    st.markdown(f"## 💬 {category} 고민을 알려주세요.")
    user_input = st.text_area("무엇이 고민이신가요?", key="counseling_input")

    if st.button("질문하기"):
        if user_input:
            # RAG 시스템과 연결하여 답변 받기 (임시 예제)
            response = f"🤖 {category} 관련 정보를 검색 중입니다..."
            st.write(response)
        else:
            st.warning("고민을 입력해주세요!")

    if st.button("🏠 처음으로"):
        st.session_state.page = "home"
        st.rerun()

