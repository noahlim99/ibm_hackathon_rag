import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document  # ✅ Document 객체 사용

# 파일 로드 및 처리 함수
def process_file(file_path):
    """파일을 로드하고 텍스트를 분할하는 함수"""
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".docx"):
        loader = UnstructuredWordDocumentLoader(file_path)
    elif file_path.endswith(".txt"):
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        print(f"❌ 지원되지 않는 파일 형식: {file_path}")
        return []

    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)

    return split_docs  # ✅ Document 객체 반환

# ChromaDB 저장 (SQLite3 사용)
def prepare_chroma_db(data_dir, persist_directory):
    """IBM 서버에 저장된 데이터를 SQLite3 기반 ChromaDB로 벡터화하여 저장"""
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    all_documents = []  # ✅ Document 객체 리스트로 저장

    for root, _, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"📂 처리 중: {file_path}")
            chunks = process_file(file_path)
            if chunks:
                all_documents.extend(chunks)  # ✅ Document 객체 저장

    # **SQLite3 기반 ChromaDB 저장**
    vector_db = Chroma.from_documents(
        documents=all_documents,
        embedding=embedding_model,
        persist_directory=persist_directory  # ✅ SQLite3 기반 저장 (기본 설정)
    )

    print(f"저장 완료! 저장 위치: {persist_directory}")

# 실행
if __name__ == "__main__":
    data_dir = "/home/ibmuser01/team5_beta/data"  # 데이터 저장 경로
    persist_directory = "/home/ibmuser01/team5_beta/chromadb_sqlite"  # SQLite3 저장 경로

    prepare_chroma_db(data_dir, persist_directory)