import json
import requests
import pandas as pd
import time

# ✅ FastAPI RAG 모델 엔드포인트
api_url = "http://127.0.0.1:8030/ask/"

# ✅ JSON 질문 리스트 불러오기
input_file = "generated_questions.json"
with open(input_file, "r", encoding="utf-8") as f:
    category_questions = json.load(f)  # 리스트 형태로 로드됨

# ✅ 평가 데이터 저장 리스트
data = []

print("\n🔹 FastAPI로 질문 전송 중...")

for entry in category_questions:
    category = entry["category"].strip()  # ✅ 공백 제거
    question = entry["prompt"]  # ✅ 질문 가져오기

    payload = {"prompt": question, "category": category}  # ✅ FastAPI 요청 JSON 형식 유지
    response = requests.post(api_url, json=payload)

    if response.status_code == 200:
        response_json = response.json()
        data.append({
            "category": category,
            "question": question,
            "retrieved_context": response_json.get("retrieved_context", "검색된 문서 없음"),
            "generated_answer": response_json.get("answer", "답변 없음"),
            "ground_truth": "해당 질문에 대한 사전 정의된 기대 답변"
        })
    else:
        print(f"❌ 요청 실패: {response.status_code}, {response.text}")

    time.sleep(1)  # ✅ 요청 간 1초 대기 (ChromaDB 안정화)

# ✅ CSV로 저장
output_file = "rag_evaluation_data.csv"
df = pd.DataFrame(data)
df.to_csv(output_file, index=False, encoding="utf-8")

print(f"\n✅ 전체 평가 데이터 저장 완료: {output_file}")
