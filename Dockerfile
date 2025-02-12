FROM python:3.10.11-slim

# FastAPI 기본 포트 설정
ENV PORT 8005

WORKDIR /app

# 가상환경 생성
RUN python3 -m venv /ve

# 가상환경 활성화
ENV PATH="/ve/bin:$PATH"

# requirements.txt 복사
ADD requirements.txt .

# 소스 코드 전체 복사
COPY . .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 도커 컨테이너 내부에서 노출할 포트
EXPOSE $PORT

# 컨테이너 실행 시 FastAPI 앱을 uvicorn으로 실행
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005", "--reload"]

ENV TMPDIR=/path/to/larger/dir
