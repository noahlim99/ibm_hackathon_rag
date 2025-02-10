import os
from langdetect import detect

def is_korean_text(text):
    """
    텍스트가 한국어인지 확인하는 함수
    """
    try:
        return detect(text) == "ko"
    except Exception as e:
        return f"Error detecting language: {str(e)}"

def check_files_in_directory(directory):
    """
    디렉토리 내 모든 .txt 파일의 한국어 여부 확인
    """
    results = {}
    for file in os.listdir(directory):
        if file.endswith(".txt"):  # .txt 파일만 처리
            file_path = os.path.join(directory, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    results[file] = is_korean_text(content)
            except Exception as e:
                results[file] = f"Error reading file: {str(e)}"
    return results

# 📂 데이터 디렉토리 경로
base_data_dir = "/home/ibmuser01/ibm_hackathon_rag/data"

# 모든 .txt 파일 확인
file_check_results = check_files_in_directory(base_data_dir)

# 결과 출력
for file_name, result in file_check_results.items():
    print(f"File: {file_name}, Is Korean: {result}")
