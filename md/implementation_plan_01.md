# 의존성 패키지 파일(requirements.txt 및 pyproject.toml) 정리 계획서

본 계획서는 서비스 소스 코드에서 실제 임포트하여 사용하는 외부 패키지들(Streamlit, LangChain 관련 패키지, ChromaDB, Dotenv, Pandas 등)을 확인하여, 로컬 가상환경 및 클라우드 배포 시 의존성 문제가 없도록 `requirements.txt`(및 `requirement.txt`)와 `pyproject.toml` 파일을 정리하여 작성하는 계획입니다.

## 사용자 검토 요구사항

- **의존성 목록 식별**:
  - UI 구성 및 포털 실행: `streamlit`
  - 멀티에이전트 및 RAG 코어: `langchain`, `langchain-community`, `langchain-openai`, `langchain-anthropic`
  - 벡터 데이터베이스: `chromadb`
  - 환경 설정 및 환경변수 주입: `python-dotenv`
  - 토큰 분할 및 파싱 유틸리티: `tiktoken`
  - 입찰가 예측 엔진 및 시각화 데이터 핸들링: `pandas`
- **산출물 구성**:
  - `requirements.txt` 및 동일 내용의 `requirement.txt` 파일을 작성 및 보완합니다.
  - PEP 621 규격에 맞추어 `pyproject.toml`의 `dependencies` 항목에 해당 의존성 패키지들을 명시적으로 추가하여 선언합니다.

---

## 제안된 변경 사항

### [NEW / MODIFY] [requirements.txt](/Real-Estate-Auction/requirements.txt) / [requirement.txt](/Real-Estate-Auction/requirement.txt)

- 주석과 함께 버전을 명시하여 외부 패키지 의존성을 정리해 작성합니다.

### [NEW / MODIFY] [pyproject.toml](/Real-Estate-Auction/pyproject.toml)

- `dependencies` 배열 항목에 모든 의존 패키지 정의 목록을 추가합니다.

---

## 검증 계획

### 자동/수동 검증

- 작성된 `pyproject.toml`의 TOML 구문 및 `requirements.txt` 포맷을 검사합니다.
