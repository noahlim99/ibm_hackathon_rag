import os
import pandas as pd
import matplotlib.pyplot as plt
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from langchain_huggingface import HuggingFaceEndpoint
from huggingface_hub import HfApi

# ✅ Hugging Face API Key 설정
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "your-huggingface-api-key"

# ✅ Hugging Face 인증 테스트
api = HfApi()
try:
    user_info = api.whoami()
    print("✅ Hugging Face 인증 성공:", user_info)
except Exception as e:
    print("❌ Hugging Face 인증 실패:", e)
    exit(1)  # 인증 실패 시 프로그램 종료

# ✅ 공개 Hugging Face 모델 사용 (FLAN-T5-Large)
llm = HuggingFaceEndpoint(
    repo_id="google/flan-t5-large",  # ✅ 공개 모델로 변경
    task="text2text-generation",
    temperature=0.7,
    max_new_tokens=512
)

# ✅ 평가 데이터 불러오기
input_file = "rag_evaluation_data.csv"
df = pd.read_csv(input_file)

# ✅ Hugging Face 모델로 평가 수행
results = evaluate(
    df,
    metrics=[
        answer_relevancy,
        context_precision,
        faithfulness
    ],
    llm=llm
)

# ✅ 평가 결과 저장
output_file = "ragas_evaluation_results_hf.csv"
results.to_csv(output_file, index=False)

# ✅ 시각화: 평가 지표별 성능 비교
plt.figure(figsize=(10, 6))
plt.bar(results.columns, results.iloc[0], color=['blue', 'green', 'orange'])
plt.xlabel("RAGAS Metrics")
plt.ylabel("Score")
plt.ylim(0, 1)
plt.title("RAGAS Evaluation Results (Using Hugging Face Model)")

# ✅ 그래프 저장 및 출력
plt.savefig("ragas_evaluation_chart_hf.png")
plt.show()

print("\n✅ RAGAS 평가 완료 및 결과 저장 완료!")
print(f"📂 평가 결과 파일: {output_file}")
print("📊 시각화된 평가 결과: ragas_evaluation_chart_hf.png")
