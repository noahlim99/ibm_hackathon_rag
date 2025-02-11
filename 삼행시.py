import time
import sys

def typewriter_effect(text, delay=0.1):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def granite_13b_instruct_v2(word):
    print("\n\n[granite_13b_instruct_v2]")  # 한 번에 출력
    time.sleep(0.5)  # 잠시 멈춤
    
    output = ["I: I'll", "B: Be your", "M: Mate!😊\n\n"]
    
    for line in output:
        typewriter_effect(line, delay=0.1)
        time.sleep(0.5)  # 한 줄 출력 후 잠시 멈춤

# 사용자 입력 받기
user_word = input("\n\n\n\n\n\n\n\n\n\n\n[granite_13b_instruct_v2] 무엇을 도와드릴까요? \n\n\n").upper()
granite_13b_instruct_v2(user_word)
