import streamlit as st
import requests
from streamlit_lottie import st_lottie
import time

############################################
# 1) 전역 설정 & 세션 상태 초기화
############################################
st.set_page_config(page_title="IBM 챗봇", page_icon="☁️", layout="centered")

RAG_API_URL = "http://localhost:8030/ask/"

# --------------------------- 세션 기본값 ---------------------------
if "page" not in st.session_state:
    st.session_state.page = "start"

# 고민 상담용
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None
if "counseling_messages" not in st.session_state:
    st.session_state.counseling_messages = []  # 고민 상담 대화

# 수다 떨기용
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []  # 수다 떨기 대화

# 맛집 탐방용
if "food_messages" not in st.session_state:
    st.session_state.food_messages = []  # 맛집 탐방 대화

# ✅ 여기서 trigger_rerun을 반드시 초기화
if "trigger_rerun" not in st.session_state:
    st.session_state.trigger_rerun = False

############################################
# 2) CSS 스타일
############################################
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css?family=Poppins:300,400,600&display=swap');

* {
  font-family: 'Poppins', sans-serif;
}
body {
  background: linear-gradient(135deg, #dbeeff 25%, #ffffff 100%) no-repeat center center fixed;
  background-size: cover;
}
.block-container {
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.user-bubble {
  text-align: left;
  background-color: #cceeff;
  padding: 10px;
  border-radius: 10px;
  margin-bottom: 10px;
  max-width: 70%;
  margin-left: auto;
  box-shadow: 0 2px 4px rgba(0,0,0,0.15);
}
.assistant-bubble {
  text-align: right;
  background-color: #ffffff;
  padding: 10px;
  border-radius: 10px;
  margin-bottom: 10px;
  max-width: 70%;
  margin-right: auto;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)




############################################
# 4) 페이지별 함수
############################################
def page_start():
    # 🌟 제목 및 설명 중앙 정렬
    st.markdown("<h2 style='text-align:center;'>IBM Mate Chat</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>IBM AI 기반 챗봇에 오신 것을 환영합니다!</p>", unsafe_allow_html=True)

    st.write("")  # 간격 조정

    # ✅ 중앙 정렬된 로고 (Lottie 제거 후 로고 사용)
    col1, col2, col3 = st.columns([1,2,1])  
    with col2:
        st.image("logo_ibm.png", use_container_width=False, width=6000)  # 크기 변경 가능

    st.write("")  # 추가 간격

    # ✅ 버튼 중앙 정렬 및 스타일 추가
    col1, col2, col3 = st.columns([1,2,1])  
    with col2:
        st.markdown(
            """
            <style>
                .block-container {
                min-height: 100vh;  /* 전체 화면 높이 */
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
                .start-button {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background-color: f5f5f5;;
                    color: white;
                    padding: 15px 32px;
                    font-size: 18px;
                    font-weight: bold;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    width: 100%;
                    transition: background-color 0.3s;
                }
                .start-button:hover {
                    background-color: #ffffff;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        # ✅ 버튼 중복 방지 (고유 키 적용)
        if st.button("클릭하여 시작하기", use_container_width=True, key="start_btn"):  
            st.session_state.page = "userinfo"
            st.rerun()





########################################





# 3) Lottie 애니메이션 로딩(옵션)
############################################
def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

lottie_welcome_url = "https://assets10.lottiefiles.com/packages/lf20_5e7wgehs.json"
lottie_welcome = load_lottie_url(lottie_welcome_url)
if "trigger_rerun" not in st.session_state:
    st.session_state.trigger_rerun = False


# 📝 타이핑 효과 함수 (중앙 정렬 유지)
def typewriter_effect(text, key, delay=0.1):
    """한 글자씩 출력하는 효과 (중앙 정렬 유지)"""
    container = st.empty()
    displayed_text = ""

    for char in text:
        displayed_text += char
        container.markdown(
            f"<h3 style='text-align: center;'>{displayed_text}</h3>", unsafe_allow_html=True
        )
        time.sleep(delay)


def page_userinfo():
    # 🎈 페이지 진입 시 풍선 효과
    st.balloons()

    # 🎨 페이지 스타일 설정
    st.markdown("""
        <style>
            /* 전체 컨테이너 높이 조정 */
            .block-container {
                min-height: 100vh;  /* 전체 화면 높이 */
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }

            /* 제목과 부제목 스타일 */
            .title-container {
                text-align: center;
                font-weight: bold;
                font-size: 28px;
                margin-bottom: 10px;
            }
            .subtitle {
                text-align: center;
                font-size: 18px;
                color: #555;
            }

            /* 안내 문구 (아래에 입력 후 Enter를 눌러주세요) 중앙 정렬 */
            .input-guide {
                text-align: center;
                font-size: 12px;
                font-weight: basic;
                color: #444;
                margin-bottom: 5px;
            }
        </style>
    """, unsafe_allow_html=True)

    # 🏡 화면 중앙 정렬 텍스트 (타이핑 효과)
    typewriter_effect("여러분 만나서 반갑습니다!", key="title", delay=0.1)
    time.sleep(1.0)  # 첫 번째 문장 출력 후 살짝 대기
    typewriter_effect("당신의 이름은?", key="subtitle", delay=0.2)

    # 🌥️ 로딩 애니메이션 or 이미지
    if lottie_welcome:
        st_lottie(lottie_welcome, height=200, key="welcome_lottie")
    else:
        st.image("https://via.placeholder.com/200x100?text=Loading+Clouds", use_container_width=True)

    # 📝 안내 문구 중앙 정렬
    st.markdown("<p class='input-guide'>아래에 입력 후 <b>Enter</b>를 눌러주세요</p>", unsafe_allow_html=True)

    # 👤 이름 입력 필드
    def on_name_submit():
        if st.session_state.name:
            st.session_state.user_name = st.session_state.name
            st.session_state.page = "home"
            st.session_state.trigger_rerun = True

    st.text_input("", key="name", on_change=on_name_submit, placeholder="홍길동")  # 입력창은 그대로 유지

    # 🔄 trigger_rerun 체크 후 페이지 리로드
    if st.session_state.trigger_rerun:
        st.session_state.trigger_rerun = False
        st.rerun()









########################################
def page_home():
    user_name = st.session_state.user_name or "사용자"

    # 🌟 환영 메시지 중앙 정렬
    st.markdown(f"""
    <h3 style="text-align: center;">👋 환영해요, <strong>{user_name}</strong> 님!👋</h3>
    <p style="text-align: center;">무엇을 해볼까요? 아래 메뉴 중에서 골라보세요!</p>
    """, unsafe_allow_html=True)

    # ✅ CSS 스타일 (버튼 디자인 적용)
    st.markdown("""
        <style>
        .block-container {
                min-height: 100vh;  /* 전체 화면 높이 */
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
        /* 전체 st.button에 대한 스타일 오버라이드 */
        .stButton > button {
            display: flex;
            flex-direction: column; /* 수직 정렬 */
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 160px; /* 버튼 크기 증가 */
            padding: 10px;
            font-size: 25px;
            font-weight: bold;
            text-align: center;
            background: white;
            border: 3px solid #6b4f3f;
            border-radius: 25px;
            color: #6b4f3f;
            cursor: pointer;
            transition: all 0.3s ease-in-out;
            box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
            white-space: pre-line; /* 줄바꿈 지원 */
        }
        
        .stButton > button:hover {
            background: #6b4f3f;
            color: white;
            box-shadow: 2px 2px 10px rgba(74, 111, 165, 0.5);
        }
        /* 버튼 클릭시(Active) 스타일 */
        .stButton > button:active {
            background: #5b4336;
            color: white;
            box-shadow: 2px 2px 10px rgba(74, 111, 165, 0.8);
        }
        </style>
    """, unsafe_allow_html=True)

    # ✅ 버튼 3개 배치
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⋆.˚✮🤭✮˚.⋆\n수다 떨기", key="chat_btn"):
            st.session_state.page = "chat"
            st.rerun()

    with col2:
        if st.button("🖐🤗🖐\n고민 상담", key="counseling_btn"):
            st.session_state.page = "counseling"
            st.rerun()

    with col3:
        if st.button("🥤🥗🍔🍗\n맛집 탐방", key="food_btn"):
            st.session_state.page = "food"
            st.rerun()


########################################





########################################
def page_counseling():
    st.markdown("""
    <h3 style="text-align: center;">🥺 어떤 고민이 있으신가요?</h3>
    <p style="text-align: center;">카테고리를 선택해 주세요!</p>
    """, unsafe_allow_html=True)

    # ✅ CSS 스타일 (버튼 디자인 + 줄바꿈)
    st.markdown("""
        <style>
        .block-container {
            min-height: 110vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            overflow: auto; /* 스크롤 가능하도록 조정 */
        }

        .stButton > button {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            width: 120px;
            height: 120px; /* 버튼 크기 */
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            background: white;
            border: 2px solid #2c3e50;
            border-radius: 60px;
            color: #2c3e50;
            cursor: pointer;
            transition: all 0.3s ease-in-out;
            box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
            white-space: pre-line; /* 줄바꿈 적용 */
        }

        .stButton > button:hover {
            background: #2c3e50;
            color: white;
            box-shadow: 2px 2px 10px rgba(44, 62, 80, 0.5);
        }

        .stButton > button:active {
            background: #1c2833;
            color: white;
            box-shadow: 2px 2px 10px rgba(44, 62, 80, 0.8);
        }
        </style>
    """, unsafe_allow_html=True)

    # ✅ 버튼을 3개씩 배치하여 최적화
    categories = [
        ("🏠", "주거"), ("💼", "일자리"), ("💰", "금융"),
        ("🛡️", "보험"), ("📱", "휴대폰"), ("🆘", "지원제도")

    ]
    
    num_cols = 3
    rows = [categories[i:i+num_cols] for i in range(0, len(categories), num_cols)]

    for row in rows:
        cols = st.columns(num_cols)
        for i, (icon, text) in enumerate(row):
            with cols[i]:
                if st.button(f"{icon}\n{text}"):  # 줄바꿈 적용
                    st.session_state.counseling_messages = []
                    st.session_state.selected_category = text
                    st.session_state.page = "chat_counseling"
                    st.rerun()

    # ✅ "🏠 처음으로" 버튼 정렬 조정
    st.markdown("<div style='display: flex; justify-content: center; padding-top: 10px;'>", unsafe_allow_html=True)
    if st.button("🏠︎\n처음으로", key="home_btn"):  # 줄바꿈 적용
        st.session_state.page = "home"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    
    
    
    
    
########################################
########################################
########################################
########################################
########################################
########################################
########################################



def page_chat_counseling():
    cat = st.session_state.selected_category or "고민"
    st.markdown(f"## 🤓 {cat} 고민을 알려주세요 ☝️")

    user_q = st.chat_input("질문을 입력하세요!")
    if user_q:
        st.session_state.counseling_messages.append({"role":"user","content":user_q})

        with st.spinner("🐝 답변 생성 중..."):
            # ✅ 카테고리 변형 없이 그대로 FastAPI로 전달
            try:
                resp = requests.post(
                    RAG_API_URL,
                    json={"prompt": user_q, "category": cat}  # 변경 없음
                )
                resp.raise_for_status()
                data = resp.json()
                answer = data.get("answer", "🚨 응답 없음.")
            except requests.exceptions.RequestException as e:
                answer = f"오류 발생: {str(e)}"

        st.session_state.counseling_messages.append({"role":"assistant","content":answer})


    # 고민 상담 대화 렌더
    for msg in st.session_state.counseling_messages:
        if msg["role"]=="user":
            st.markdown(
                f"""
                <div class="user-bubble">
                    <strong>Q:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="assistant-bubble">
                    <strong>A:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True
            )

    if st.button("🏠 처음으로"):
        st.session_state.page = "home"
        st.rerun()


def page_chat():
    st.markdown("## ☕ 수다 떨기 페이지")
    st.write("가볍게 수다를 떨고 싶다면 여기에 질문을 입력하세요!")

    user_q = st.chat_input("메시지를 입력하세요!")
    if user_q:
        st.session_state.chat_messages.append({"role":"user","content":user_q})

        with st.spinner("🤖 응답 생성 중..."):
            try:
                resp = requests.post(
                    RAG_API_URL,
                    json={"prompt": user_q, "category": "general_chat"}
                )
                resp.raise_for_status()
                data = resp.json()

                # ✅ API 응답 디버깅
                answer = data.get("answer", "🤖 응답 없음.")
                st.write(f"🔍 [DEBUG] API 응답: {answer}")

            except requests.exceptions.RequestException as e:
                answer = f"오류 발생: {str(e)}"
                st.write(f"⚠ [DEBUG] API 호출 실패: {e}")

        st.session_state.chat_messages.append({"role":"assistant","content":answer})

    # 수다 대화 렌더
    for msg in st.session_state.chat_messages:
        if msg["role"]=="user":
            st.markdown(
                f"""
                <div class="user-bubble">
                    <strong>Q:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="assistant-bubble">
                    <strong>A:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True
            )

    if st.button("🏠 처음으로"):
        st.session_state.page = "home"
        st.rerun()



def page_food():
    st.markdown("## 🍔 맛집 탐방 페이지 (미구현)")
    st.write("맛집 정보를 공유하고 싶다면 여기서 구현할 수 있어요!")

    user_q = st.chat_input("어떤 맛집을 찾고 계신가요?")
    if user_q:
        st.session_state.food_messages.append({"role":"user","content":user_q})

        with st.spinner("🍽️ 추천 생성 중..."):
            try:
                resp = requests.post(
                    RAG_API_URL,
                    json={"prompt": user_q, "category": "food_recommendation"}
                )
                resp.raise_for_status()
                data = resp.json()
                answer = data.get("answer","🍽️ 추천 없음.")
            except requests.exceptions.RequestException as e:
                answer = f"오류 발생: {str(e)}"

        st.session_state.food_messages.append({"role":"assistant","content":answer})

    # 맛집 대화 렌더
    for msg in st.session_state.food_messages:
        if msg["role"]=="user":
            st.markdown(
                f"""
                <div class="user-bubble">
                    <strong>Q:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="assistant-bubble">
                    <strong>A:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True
            )

    if st.button("🏠 처음으로"):
        st.session_state.page = "home"
        st.rerun()

########################################
# 5) 라우팅
########################################
page = st.session_state.page
if page == "start":
    page_start()
elif page == "userinfo":
    page_userinfo()
elif page == "home":
    page_home()
elif page == "counseling":
    page_counseling()
elif page == "chat_counseling":
    page_chat_counseling()
elif page == "chat":
    page_chat()
elif page == "food":
    page_food()
