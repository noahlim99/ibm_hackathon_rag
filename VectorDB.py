import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

# 📌 카테고리별 문서를 벡터화하여 저장
def prepare_chroma_db_by_category(base_data_dir, persist_base_dir):
    """
    카테고리별로 문서를 벡터화하여 ChromaDB에 저장
    """
    # 사용할 임베딩 모델 초기화
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # 데이터 디렉토리 내 각 카테고리 디렉토리를 처리
    for category in os.listdir(base_data_dir):
        category_path = os.path.join(base_data_dir, category)
        if not os.path.isdir(category_path):
            continue  # 디렉토리가 아니면 스킵

        print(f"📂 카테고리 '{category}' 처리 중...")

        all_documents = []  # 카테고리 내 모든 문서를 저장할 리스트

        # 해당 카테고리의 모든 txt 파일 로드
        for file in os.listdir(category_path):
            file_path = os.path.join(category_path, file)
            if not file.endswith(".txt"):
                continue  # txt 파일만 처리

            print(f"📄 문서 처리: {file_path}")
            try:
                loader = TextLoader(file_path, encoding="utf-8")
                document_text = loader.load()[0].page_content  # 텍스트 로드

                # ✅ 파일을 하나의 Document 객체로 처리
                doc = Document(page_content=document_text, metadata={"source": file_path})
                all_documents.append(doc)

            except Exception as e:
                print(f"❌ 파일 처리 중 오류 발생: {file_path} - {str(e)}")
                continue

        # 📌 카테고리별 벡터DB 저장 디렉토리 생성
        category_persist_dir = os.path.join(persist_base_dir, category)
        os.makedirs(category_persist_dir, exist_ok=True)

        # 📌 카테고리별 벡터DB 생성 및 저장
        vector_db = Chroma.from_documents(
            documents=all_documents,
            embedding=embedding_model,
            persist_directory=category_persist_dir
        )
        print(f"✅ 저장 완료: {category_persist_dir} (총 {len(all_documents)}개 문서 저장)")

# 실행
if __name__ == "__main__":
    # 📂 카테고리별 데이터가 저장된 경로 (data 디렉토리)
    base_data_dir = "/home/ibmuser01/ibm_hackathon_rag/data"
    
    # 📂 벡터DB 저장 경로
    persist_base_dir = "/home/ibmuser01/ibm_hackathon_rag/vectorDB"

    # 카테고리별 벡터DB 생성
    prepare_chroma_db_by_category(base_data_dir, persist_base_dir)
