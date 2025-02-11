import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter  # 텍스트 청크화

# 📌 카테고리별 문서를 벡터화하여 각각의 ChromaDB에 저장
def prepare_chroma_db_by_category(base_data_dir, persist_base_dir):
    """
    카테고리별로 문서를 벡터화하여 ChromaDB에 저장
    """
    # 사용할 임베딩 모델 초기화
    embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en")

    # 텍스트 청크 설정 (추천값 적용)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,  # 한 청크의 최대 토큰 수
        chunk_overlap=300  # 청크 간 겹치는 토큰 수
    )

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
                # 텍스트 로드
                loader = TextLoader(file_path, encoding="utf-8")
                document_text = loader.load()[0].page_content

                # 텍스트를 청크로 나누기
                chunks = text_splitter.split_text(document_text)

                # ✅ 청크를 Document 객체로 변환
                for chunk in chunks:
                    doc = Document(page_content=chunk, metadata={"source": file_path, "category": category})
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
        print(f"✅ 저장 완료: {category_persist_dir} (총 {len(all_documents)}개 청크 저장)")

# 실행
if __name__ == "__main__":
    # 📂 카테고리별 데이터가 저장된 경로 (data 디렉토리)
    base_data_dir = "/home/ibmuser01/ibm_hackathon_rag/data"
    
    # 📂 벡터DB 저장 경로
    persist_base_dir = "/home/ibmuser01/ibm_hackathon_rag/vectorDB"

    # 카테고리별 벡터DB 생성
    prepare_chroma_db_by_category(base_data_dir, persist_base_dir)
