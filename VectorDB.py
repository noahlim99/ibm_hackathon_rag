import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter  # 텍스트 청크화

# 📌 문서를 벡터화하여 단일 ChromaDB에 저장
def prepare_chroma_db(base_data_dir, persist_dir):
    # 사용할 임베딩 모델 초기화
    embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en")

    # 텍스트 청크 설정 (추천값 적용)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,  # 한 청크의 최대 토큰 수
        chunk_overlap=300  # 청크 간 겹치는 토큰 수
    )

    all_documents = []  # 모든 문서를 저장할 리스트

    # 데이터 디렉토리 내 모든 txt 파일 처리
    for file in os.listdir(base_data_dir):
        file_path = os.path.join(base_data_dir, file)
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
                doc = Document(page_content=chunk, metadata={"source": file_path})
                all_documents.append(doc)

        except Exception as e:
            print(f"❌ 파일 처리 중 오류 발생: {file_path} - {str(e)}")
            continue

    # 📌 단일 벡터DB 저장 디렉토리 생성
    os.makedirs(persist_dir, exist_ok=True)

    # 📌 단일 벡터DB 생성 및 저장
    vector_db = Chroma.from_documents(
        documents=all_documents,
        embedding=embedding_model,
        persist_directory=persist_dir
    )
    print(f"✅ 저장 완료: {persist_dir} (총 {len(all_documents)}개 청크 저장)")

# 실행
if __name__ == "__main__":
    # 📂 데이터가 저장된 경로 (data 디렉토리)
    base_data_dir = "/home/ibmuser01/ibm_hackathon_rag/data"
    
    # 📂 벡터DB 저장 경로
    persist_dir = "/home/ibmuser01/ibm_hackathon_rag/vectorDB"

    # 벡터DB 생성
    prepare_chroma_db(base_data_dir, persist_dir)