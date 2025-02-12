import streamlit as st
import requests
from streamlit_lottie import st_lottie
import time





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
  text-align: left;
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
############################################







# 4) 페이지별 함수
############################################
def page_start():
    # 🌟 제목 및 설명 중앙 정렬 　.　
    st.markdown("<h2 style='text-align:center;'>IBM Mate Chat</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'><b>당신의 MATE가 되어드릴게요!<b></p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'><b>보호종료 아동을 위한 CHAT 도우미 서비스 입니다.<b></p>", unsafe_allow_html=True)
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
############################################


########################################
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
########################################


########################################
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
                font-size: 40px;
                margin-bottom: 10px;
                color: #7993c1;
            }
            .subtitle {
                text-align: center;
                font-size: 11px;
                color: #7993c1;
            }

            /* 안내 문구 (아래에 입력 후 Enter를 눌러주세요) 중앙 정렬 */
            .input-guide {
                text-align: center;
                font-size: 12px;
                font-weight: basic;
                color: #7993c1;
                margin-bottom: 5px;
            }
        </style>
    """, unsafe_allow_html=True)

    # 🏡 화면 중앙 정렬 텍스트 (타이핑 효과)
    typewriter_effect(" 만나서 반가워요!", key="title", delay=0.07)
    time.sleep(0.5)  # 첫 번째 문장 출력 후 살짝 대기
    typewriter_effect("이름을 알려주세요!", key="subtitle", delay=0.07)

    # 🌥️ 로딩 애니메이션 or 이미지
    if lottie_welcome:
        st_lottie(lottie_welcome, height=250, key="welcome_lottie")
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

    st.text_input("", key="name", on_change=on_name_submit, placeholder="이름을 입력해주세요")  # 입력창은 그대로 유지

    # 🔄 trigger_rerun 체크 후 페이지 리로드
    if st.session_state.trigger_rerun:
        st.session_state.trigger_rerun = False
        st.rerun()
########################################



########################################
def page_home():
    user_name = st.session_state.user_name or "사용자"

    # 🌟 환영 메시지 중앙 정렬
    st.markdown(f"""
    <h3 style="text-align: center;">　환영해요, <strong>{user_name}</strong>님.</h3>
    <p style="text-align: center;">무엇을 해볼까요?</p>
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
            height: 120px; /* 버튼 크기 증가 */
            padding: 10px;
            font-size: 40px;
            font-weight: bold;
            text-align: center;
            background: white;
            border: 3px solid #7993c1;
            border-radius: 25px;
            color: #2c3e50;
            cursor: pointer;
            transition: all 0.3s ease-in-out;
            box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
            white-space: pre-line; /* 줄바꿈 지원 */
        }
        
        .stButton > button:hover {
            background: #7993c1;
            color: white;
            box-shadow: 2px 2px 10px rgba(74, 111, 165, 0.5);
        }
        /* 버튼 클릭시(Active) 스타일 */
        .stButton > button:active {
            background: #7993c1;
            color: white;
            box-shadow: 2px 2px 10px rgba(74, 111, 165, 0.8);
        }
        </style>
    """, unsafe_allow_html=True)

    # ✅ 버튼 3개 배치
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⋆˚🤭✮⋆\n수다 떨기", key="chat_btn"):
            st.session_state.page = "chat"
            st.rerun()

    with col2:
        if st.button("🖐🤗🖐\n고민 상담", key="counseling_btn"):
            st.session_state.page = "counseling"
            st.rerun()

    with col3:
        if st.button("🥤🥗🥓\n맛집 탐방", key="food_btn"):
            st.session_state.page = "food"
            st.rerun()
########################################*



# def page_counseling():
########################################
def page_counseling():
    st.markdown("""
    <h3 style="text-align: center;">🥺 어떤 고민이 있으신가요?</h3>
    <p style="text-align: center;">카테고리를 선택해 주세요!</p>
    """, unsafe_allow_html=True)

    # ✅ CSS 스타일 (전체 화면 중앙 정렬)
    st.markdown("""
        <style>
        .block-container {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        .stButton > button {
            width: 140px;
            height: 140px;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            background: white;
            border: 2px solid #7993c1;
            border-radius: 7px;
            color: #7993c1;
            cursor: pointer;
            transition: all 0.3s ease-in-out;
            box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
            white-space: pre-line;
        }

        .stButton > button:hover {
            background: #7993c1;
            color: white;
            box-shadow: 2px 2px 10px rgba(44, 62, 80, 0.5);
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🏠\n주거"):
            st.session_state.selected_category = "주거"
            st.session_state.counseling_messages = []  # ✅ 기존 대화 초기화
            st.session_state.last_input = None  # ✅ 이전 입력도 초기화
            st.session_state.page = "chat_counseling"
            st.rerun()

    with col2:
        if st.button("💼\n일자리"):
            st.session_state.selected_category = "일자리"
            st.session_state.counseling_messages = []
            st.session_state.last_input = None
            st.session_state.page = "chat_counseling"
            st.rerun()

    with col3:
        if st.button("💰\n금융"):
            st.session_state.selected_category = "금융"
            st.session_state.counseling_messages = []
            st.session_state.last_input = None
            st.session_state.page = "chat_counseling"
            st.rerun()

    with col4:
        if st.button("🧑‍⚕\n건강 & 의료"):
            st.session_state.selected_category = "건강 & 의료"
            st.session_state.counseling_messages = []
            st.session_state.last_input = None
            st.session_state.page = "chat_counseling"
            st.rerun()

    # ✅ 간격 추가하여 균형 맞추기
    st.markdown("<br>", unsafe_allow_html=True)

    # ✅ 두 번째 줄 (보험 - 휴대폰 - 지원제도 - 교육)
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        if st.button("🛡️\n보험"):
            st.session_state.selected_category = "보험"
            st.session_state.counseling_messages = []
            st.session_state.last_input = None
            st.session_state.page = "chat_counseling"
            st.rerun()

    with col6:
        if st.button("📱\n휴대폰"):
            st.session_state.selected_category = "휴대폰"
            st.session_state.counseling_messages = []
            st.session_state.last_input = None
            st.session_state.page = "chat_counseling"
            st.rerun()

    with col7:
        if st.button("🆘\n지원 제도"):
            st.session_state.selected_category = "지원 제도"
            st.session_state.counseling_messages = []
            st.session_state.last_input = None
            st.session_state.page = "chat_counseling"
            st.rerun()

    with col8:
        if st.button("📚\n교육 & 학습"):
            st.session_state.selected_category = "교육 & 학습"
            st.session_state.counseling_messages = []
            st.session_state.last_input = None
            st.session_state.page = "chat_counseling"
            st.rerun()

    # ✅ "처음으로" 버튼을 네모 형태로 만들고 정확한 가운데 정렬
    st.write("")  # 간격 추가
    col_back = st.columns([1.5, 1, 1.5])  # ✅ 가운데 정렬을 위해 유지
    with col_back[1]:  # ✅ 중앙 컬럼에 배치
        if st.button("🏠︎ 처음으로"):  # ✅ 기본 Streamlit 버튼 그대로 사용 (네모 버튼 유지)
            st.session_state.page = "home"
            st.session_state.counseling_messages = []  # ✅ "처음으로" 눌러도 초기화
            st.session_state.last_input = None
            st.rerun()


    
    


    
########################################
########################################
########################################
########################################



########################################
# def page_chat_counseling():
#

def page_chat_counseling():
    cat = st.session_state.selected_category or "고민"


    # ✅ 상태 변수 설정
    if "last_input" not in st.session_state:
        st.session_state.last_input = None  
    if "waiting_for_response" not in st.session_state:
        st.session_state.waiting_for_response = False

    # ✅ **CSS 스타일 수정 (입력창을 채팅창 내부에 완전히 포함)**
    st.markdown("""
    <style>
    .chat-container {
      width: 90%;
      max-width: 600px;
      height: 75vh;
      display: flex;
      flex-direction: column-reverse;
      overflow-y: auto;
      padding: 15px;
      background: white;
      margin: auto;
      border-radius: 15px;
      box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
      position: relative;
    }

    .chat-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      background: #5a72c1;
      color: white;
      padding: 12px 16px;
      font-size: 18px;
      font-weight: bold;
      border-bottom: 2px solid #475b9b;
      border-radius: 8px 8px 0 0;
    }

    .chat-header h3 {
      flex-grow: 1;
      text-align: center;
      margin: 0;
    }

    .user-bubble {
      background: #d0f0ff;
      padding: 12px;
      border-radius: 20px;
      margin: 5px 0;
      max-width: 70%;
      margin-left: auto;
      text-align: left;
      box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
    }

    .assistant-bubble {
      background: #ffeaa7;
      padding: 12px;
      border-radius: 20px;
      margin: 5px 0;
      max-width: 70%;
      margin-right: auto;
      text-align: left;
      box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
    }

    .loading-bubble {
      background: #fff2c7;
      padding: 12px;
      border-radius: 20px;
      margin: 5px 0;
      max-width: 70%;
      margin-right: auto;
      text-align: left;
      box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
      font-weight: bold;
    }

    /* ✅ 입력창을 채팅창 내부 최하단에 고정 */
    .input-container {
      width: calc(100% - 30px);
      padding: 10px;
      background: white;
      border-top: 2px solid #ccc;
      display: flex;
      align-items: center;
      position: absolute;
      bottom: 0;
      left: 15px;
      border-radius: 0 0 15px 15px;
      box-shadow: 0px -2px 8px rgba(0, 0, 0, 0.1);
    }

    .input-container input {
      width: 100%;
      padding: 10px;
      border: none;
      outline: none;
      font-size: 16px;
      border-radius: 10px;
      background: #f1f3f4;
    }
    
    </style>
    """, unsafe_allow_html=True)

    # ✅ **상단 타이틀 바**
    col1, col2, col3 = st.columns([1, 5, 1])
    with col1:
        if st.button("◀", key="back_btn"):
            st.session_state.page = "counseling"
            st.rerun()

    with col2:
        st.markdown(f"<h3 style='text-align: center;'>🤓 {cat} 고민을 알려주세요</h3>", unsafe_allow_html=True)

    with col3:
        if st.button("🏠", key="home_btn"):
            st.session_state.page = "home"
            st.rerun()

    # ✅ **채팅 메시지 컨테이너 (입력창 포함)**
    messages_html = '<div class="chat-container" id="chat-messages">'

    # ✅ "🐝 답변 생성 중..."을 조건부로 표시
    if st.session_state.waiting_for_response:
        messages_html += '<div class="loading-bubble">🐝 답변 생성 중...</div>'

    # ✅ 기존 메시지 렌더링
    for msg in reversed(st.session_state.counseling_messages):
        if msg["role"] == "user":
            messages_html += f'<div class="user-bubble"><strong>Q:</strong> {msg["content"]}</div>'
        else:
            messages_html += f'<div class="assistant-bubble"><strong>A:</strong> {msg["content"]}</div>'

    messages_html += '</div>'
    st.markdown(messages_html, unsafe_allow_html=True)

    # ✅ **입력창을 채팅창 내부 최하단에 고정 (단일 입력창 유지)**
    user_q = st.text_input(
        "질문을 입력하세요!", 
        key="chat_input", 
        label_visibility="collapsed"
    )

    # ✅ **질문 입력 처리**
    if user_q and user_q != st.session_state.last_input:
        st.session_state.counseling_messages.append({"role": "user", "content": user_q})
        st.session_state.waiting_for_response = True
        st.session_state.last_input = user_q
        st.rerun()

    # ✅ **AI 응답 생성 (자동 호출)**
    if st.session_state.waiting_for_response:
        with st.spinner("🐝 답변 생성 중..."):
            try:
                cat_clean = cat.replace("🏠 ","").replace("💼 ","").replace("💰 ","").replace("🛡️ ","").replace("📱 ","").replace("🆘 ","")
                
                resp = requests.post(
                    RAG_API_URL,
                    json={"prompt": st.session_state.counseling_messages[-1]["content"], "category": cat_clean}
                )
                resp.raise_for_status()
                data = resp.json()
                answer = data.get("answer", "🚨 응답 없음.")
            except requests.exceptions.RequestException as e:
                answer = f"오류 발생: {str(e)}"

        # ✅ "답변 생성 중..." 제거 후 실제 응답 추가
        st.session_state.counseling_messages.append({"role": "assistant", "content": answer})
        st.session_state.waiting_for_response = False
        st.rerun()




#
########################################




########################################
def page_chat_talk():
    # ✅ 상태 변수 설정
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []  # 수다 대화 상태 변수 추가
    if "last_chat_input" not in st.session_state:
        st.session_state.last_chat_input = None  
    if "waiting_for_chat_response" not in st.session_state:
        st.session_state.waiting_for_chat_response = False

    # ✅ **CSS 스타일 수정 (입력창을 채팅창 내부에 완전히 포함)**
    st.markdown("""
    <style>
    .chat-container {
      width: 90%;
      max-width: 600px;
      height: 75vh;
      display: flex;
      flex-direction: column-reverse;
      overflow-y: auto;
      padding: 15px;
      background: white;
      margin: auto;
      border-radius: 15px;
      box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
      position: relative;
    }

    .chat-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      background: #ffcc66;
      color: white;
      padding: 12px 16px;
      font-size: 18px;
      font-weight: bold;
      border-bottom: 2px solid #ffb347;
      border-radius: 8px 8px 0 0;
    }

    .chat-header h3 {
      flex-grow: 1;
      text-align: center;
      margin: 0;
    }

    .user-bubble {
      background: #d0f0ff;
      padding: 12px;
      border-radius: 20px;
      margin: 5px 0;
      max-width: 70%;
      margin-left: auto;
      text-align: left;
      box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
    }

    .assistant-bubble {
      background: #ffeb99;
      padding: 12px;
      border-radius: 20px;
      margin: 5px 0;
      max-width: 70%;
      margin-right: auto;
      text-align: left;
      box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
    }

    .loading-bubble {
      background: #fff2c7;
      padding: 12px;
      border-radius: 20px;
      margin: 5px 0;
      max-width: 70%;
      margin-right: auto;
      text-align: left;
      box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
      font-weight: bold;
    }

    /* ✅ 입력창을 채팅창 내부 최하단에 고정 */
    .input-container {
      width: calc(100% - 30px);
      padding: 10px;
      background: white;
      border-top: 2px solid #ccc;
      display: flex;
      align-items: center;
      position: absolute;
      bottom: 0;
      left: 15px;
      border-radius: 0 0 15px 15px;
      box-shadow: 0px -2px 8px rgba(0, 0, 0, 0.1);
    }

    .input-container input {
      width: 100%;
      padding: 10px;
      border: none;
      outline: none;
      font-size: 16px;
      border-radius: 10px;
      background: #f1f3f4;
    }
    
    </style>
    """, unsafe_allow_html=True)

    # ✅ **상단 타이틀 바**
    col1, col2, col3 = st.columns([1, 5, 1])
    with col1:
        if st.button("◀", key="back_chat_btn"):
            st.session_state.page = "home"
            st.rerun()

    with col2:
        st.markdown(f"<h3 style='text-align: center;'>☕ 수다 떨기</h3>", unsafe_allow_html=True)

    with col3:
        if st.button("🏠", key="home_chat_btn"):
            st.session_state.page = "home"
            st.rerun()

    # ✅ **채팅 메시지 컨테이너 (입력창 포함)**
    messages_html = '<div class="chat-container" id="chat-messages">'

    # ✅ "🐝 답변 생성 중..."을 조건부로 표시
    if st.session_state.waiting_for_chat_response:
        messages_html += '<div class="loading-bubble">🐝 답변 생성 중...</div>'

    # ✅ 기존 메시지 렌더링
    for msg in reversed(st.session_state.chat_messages):
        if msg["role"] == "user":
            messages_html += f'<div class="user-bubble"><strong>Q:</strong> {msg["content"]}</div>'
        else:
            messages_html += f'<div class="assistant-bubble"><strong>A:</strong> {msg["content"]}</div>'

    messages_html += '</div>'
    st.markdown(messages_html, unsafe_allow_html=True)

    # ✅ **입력창을 채팅창 내부 최하단에 고정 (단일 입력창 유지)**
    user_q = st.text_input(
        "자유롭게 수다를 떨어보세요!", 
        key="chat_input", 
        label_visibility="collapsed"
    )

    # ✅ **질문 입력 처리**
    if user_q and user_q != st.session_state.last_chat_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_q})
        st.session_state.waiting_for_chat_response = True
        st.session_state.last_chat_input = user_q
        st.rerun()

    # ✅ **AI 응답 생성 (자동 호출)**
    if st.session_state.waiting_for_chat_response:
        with st.spinner("🐝 답변 생성 중..."):
            try:
                resp = requests.post(
                    RAG_API_URL,
                    json={"prompt": st.session_state.chat_messages[-1]["content"], "category": "general_chat"}
                )
                resp.raise_for_status()
                data = resp.json()
                answer = data.get("answer", "🚨 응답 없음.")
            except requests.exceptions.RequestException as e:
                answer = f"오류 발생: {str(e)}"

        # ✅ "답변 생성 중..." 제거 후 실제 응답 추가
        st.session_state.chat_messages.append({"role": "assistant", "content": answer})
        st.session_state.waiting_for_chat_response = False
        st.rerun()

########################################



########################################
########################################
# 🍽️ 맛집 탐방 챗봇
########################################
def page_food_chat():
    # ✅ 상태 변수 설정
    if "food_messages" not in st.session_state:
        st.session_state.food_messages = []  # 맛집 챗봇 대화 저장
    if "last_food_input" not in st.session_state:
        st.session_state.last_food_input = None  
    if "waiting_for_food_response" not in st.session_state:
        st.session_state.waiting_for_food_response = False

    # ✅ **CSS 스타일 수정 (입력창을 채팅창 내부에 완전히 포함)**
    st.markdown("""
    <style>
    .chat-container {
      width: 90%;
      max-width: 600px;
      height: 75vh;
      display: flex;
      flex-direction: column-reverse;
      overflow-y: auto;
      padding: 15px;
      background: white;
      margin: auto;
      border-radius: 15px;
      box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
      position: relative;
    }

    .chat-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      background: #ff9966;
      color: white;
      padding: 12px 16px;
      font-size: 18px;
      font-weight: bold;
      border-bottom: 2px solid #ff784f;
      border-radius: 8px 8px 0 0;
    }

    .chat-header h3 {
      flex-grow: 1;
      text-align: center;
      margin: 0;
    }

    .user-bubble {
      background: #d0f0ff;
      padding: 12px;
      border-radius: 20px;
      margin: 5px 0;
      max-width: 70%;
      margin-left: auto;
      text-align: left;
      box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
    }

    .assistant-bubble {
      background: #ffcc99;
      padding: 12px;
      border-radius: 20px;
      margin: 5px 0;
      max-width: 70%;
      margin-right: auto;
      text-align: left;
      box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
    }

    .loading-bubble {
      background: #fff2c7;
      padding: 12px;
      border-radius: 20px;
      margin: 5px 0;
      max-width: 70%;
      margin-right: auto;
      text-align: left;
      box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
      font-weight: bold;
    }

    /* ✅ 입력창을 채팅창 내부 최하단에 고정 */
    .input-container {
      width: calc(100% - 30px);
      padding: 10px;
      background: white;
      border-top: 2px solid #ccc;
      display: flex;
      align-items: center;
      position: absolute;
      bottom: 0;
      left: 15px;
      border-radius: 0 0 15px 15px;
      box-shadow: 0px -2px 8px rgba(0, 0, 0, 0.1);
    }

    .input-container input {
      width: 100%;
      padding: 10px;
      border: none;
      outline: none;
      font-size: 16px;
      border-radius: 10px;
      background: #f1f3f4;
    }
    
    </style>
    """, unsafe_allow_html=True)

    # ✅ **상단 타이틀 바**
    col1, col2, col3 = st.columns([1, 5, 1])
    with col1:
        if st.button("◀", key="back_food_btn"):
            st.session_state.page = "home"
            st.rerun()

    with col2:
        st.markdown(f"<h3 style='text-align: center;'>🍽️ 맛집 추천 챗봇</h3>", unsafe_allow_html=True)

    with col3:
        if st.button("🏠", key="home_food_btn"):
            st.session_state.page = "home"
            st.rerun()

    # ✅ **채팅 메시지 컨테이너 (입력창 포함)**
    messages_html = '<div class="chat-container" id="chat-messages">'

    # ✅ "🐝 답변 생성 중..."을 조건부로 표시
    if st.session_state.waiting_for_food_response:
        messages_html += '<div class="loading-bubble">🐝 맛집 추천 중...</div>'

    # ✅ 기존 메시지 렌더링
    for msg in reversed(st.session_state.food_messages):
        if msg["role"] == "user":
            messages_html += f'<div class="user-bubble"><strong>Q:</strong> {msg["content"]}</div>'
        else:
            messages_html += f'<div class="assistant-bubble"><strong>A:</strong> {msg["content"]}</div>'

    messages_html += '</div>'
    st.markdown(messages_html, unsafe_allow_html=True)

    # ✅ **입력창을 채팅창 내부 최하단에 고정 (단일 입력창 유지)**
    user_q = st.text_input(
        "어떤 음식이 먹고 싶나요?", 
        key="food_chat_input", 
        label_visibility="collapsed"
    )

    # ✅ **질문 입력 처리**
    if user_q and user_q != st.session_state.last_food_input:
        st.session_state.food_messages.append({"role": "user", "content": user_q})
        st.session_state.waiting_for_food_response = True
        st.session_state.last_food_input = user_q
        st.rerun()

    # ✅ **AI 응답 생성 (자동 호출)**
    if st.session_state.waiting_for_food_response:
        with st.spinner("🐝 맛집 추천 중..."):
            try:
                resp = requests.post(
                    RAG_API_URL,
                    json={"prompt": st.session_state.food_messages[-1]["content"], "category": "food_recommendation"}
                )
                resp.raise_for_status()
                data = resp.json()
                answer = data.get("answer", "🚨 추천 없음.")
            except requests.exceptions.RequestException as e:
                answer = f"오류 발생: {str(e)}"

        # ✅ "추천 생성 중..." 제거 후 실제 응답 추가
        st.session_state.food_messages.append({"role": "assistant", "content": answer})
        st.session_state.waiting_for_food_response = False
        st.rerun()
########################################

# 5) 라우팅 (맛집 챗봇 반영)
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
    page_chat_talk()
elif page == "food":  # ✅ 맛집 탐방 챗봇 적용
    page_food_chat()
########################################
