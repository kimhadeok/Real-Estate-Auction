# 부동산 경매 AI 튜터 백엔드 기술 명세서 (dev.md)

**개발 에이전트 (`@dev`) 작성**

본 문서는 플랫폼의 시스템 아키텍처, 핵심 파이썬 소스 모듈 명세, 모듈 탐색 경로 바인딩 방식, 그리고 의존성 관리 구조를 다룬 백엔드 개발 명세서입니다.

---

## 1. 프로젝트 아키텍처 및 모듈 위치 리팩토링

가장 큰 코드 아키텍처적 개선은 루트에 분산되어 있던 핵심 백엔드/엔진 모듈들을 `src/core/` 하위로 이동하여 관심사 분리(SoC)를 고도화하고, UI 레이어(`src/glossary`, `src/procedure` 등)와 확실하게 결격시킨 점입니다.

### 1.1 모듈 탐색 경로 (`sys.path`) 동적 바인딩 원리
- **발생했던 문제**: `common.py` 및 기타 모듈들이 `src/core/` 폴더 안으로 이주하면서, 기존 루트 실행 방식 하에서 상호 참조 임포트(`import config` 등) 시 `ModuleNotFoundError`를 유발했습니다.
- **해결 방식**: 각 실행 파일의 최상단에 `sys.path.insert(0, ...)`를 주입하는 래퍼 방식을 설계했습니다.
  - `app.py` (루트 진입): `Path(__file__).resolve().parent / "src" / "core"`를 삽입하여 `src/core` 내의 모든 모듈을 최우선 탐색하게 만듭니다.
  - `src/core/common.py` (공통 UI/CSS): `Path(__file__).resolve().parent`를 통해 자신의 위치를 탐색 경로에 등록합니다.
  - `pages/*.py` (멀티페이지 진입): `Path(__file__).resolve().parent.parent / "src" / "core"`를 통해 `src/core` 모듈들을 자동 로드 가능하도록 바인딩합니다.
  - `ingest.py`, `cli.py` (직접 실행): `sys.path.insert(0, str(Path(__file__).resolve().parent))`를 주입해 단독 실행 시에도 자사 모듈을 바로 탐색하도록 격리했습니다.

---

## 2. `src/core/` 핵심 엔진 소스 분석

### 2.1 `config.py` (전역 설정)
- **경로 바인딩**: `BASE_DIR = Path(__file__).resolve().parent.parent.parent`로 상향 조정해, 모듈이 리팩토링되어 위치를 이동했음에도 데이터 디렉토리(`data/`, `chroma_db/`, `prompts/`) 경로를 항상 프로젝트 루트 기준으로 정확하게 추적합니다.
- **다중 LLM/임베딩 지원**: `.env` 설정에 따라 OpenAI(`gpt-4o-mini`, `text-embedding-3-small`)와 Anthropic(`claude-3-haiku`), 그리고 로컬 한글 임베딩(`HuggingFaceEmbeddings`) 객체를 유기적으로 스위칭합니다.

### 2.2 `ingest.py` (데이터 청킹 및 ChromaDB 빌더)
- **Clause-aware 청킹**: 법률 문서는 `## 제OO조` 단위, 절차는 `## N단계` 단위의 마크다운 헤더를 기준으로 데이터 분리를 정밀하게 처리합니다. 800자 초과 시 문장 오버랩 분할을 지원합니다.
- **ChromaDB Persistent Client**: 영구 벡터스토어를 저장하며, 재실행 시 기존 동일 컬렉션을 자동으로 안전하게 드롭한 후 다시 생성해 데이터 중복 누적을 방지합니다.

### 2.3 `rag.py` & `router.py` (검색 엔진 및 라우터)
- **다중 컬렉션 RAG (`rag.py`)**: 하나의 에이전트가 여러 벡터 데이터 컬렉션을 동시 탐색하는 구조입니다. 반환된 청크들은 코사인 유사도 거리순으로 재정렬 및 병합(Merge)되며, 출처 목록의 중복을 제거하여 명확하게 리턴합니다.
- **오케스트레이션 라우터 (`router.py`)**: 단 한 번의 LLM 프롬프트 분석으로 사용자 쿼리를 파악해 `procedure`, `tutor`, `quiz` 라벨로 분류하고, 해당 전문 에이전트 객체나 퀴즈 채점 메소드로 유연하게 라우팅합니다.

### 2.4 `quiz.py` (사례 퀴즈 및 채점)
- **데이터 로드**: RAG 검색을 통하지 않고 로컬 `sample_cases.json` 파일을 직접 역직렬화하여, 채점 전까지 해설 및 정답 딕셔너리(`analysis`)를 완전히 분리하여 보안(Anti-Leak)을 유지합니다.
- **유형별 자동 채점**: 사용자가 제출한 텍스트와 정답 키 텍스트를 LLM 프롬프트 메시지 구조(`SystemMessage`, `HumanMessage`)로 구성 및 결합하여 정밀한 피드백과 평가 점수를 생성합니다.

---

## 3. 패키지 및 의존성 관리

의존성은 두 종류의 파일로 완벽하게 이중 관리되어, 로컬 pip 환경과 현대적인 프로젝트 매니저 및 클라우드 배포(Streamlit Cloud) 환경을 모두 수용합니다.

### 3.1 `requirements.txt` / `requirement.txt` (pip 호환성)
```txt
streamlit>=1.30.0
langchain>=0.2.0
langchain-openai>=0.1.0
langchain-anthropic>=0.1.0
langchain-community>=0.2.0
chromadb>=0.4.22
python-dotenv>=1.0.0
tiktoken>=0.5.0
pandas>=2.0.0
```

### 3.2 `pyproject.toml` (PEP 621 표준 명세)
- `[project]` 테이블 하위에 프로젝트 명칭, 파이썬 규격(`requires-python = ">=3.10"`), 그리고 `dependencies` 배열 내에 위 9개 필수 패키지 명세를 상호 일치하게 선언하였습니다.
- TOML 구문 및 파이썬 `tomllib` 파싱 자동 검증 스크립트를 거쳐 무결성이 입증되었습니다.
