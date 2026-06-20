# 부동산 경매 교육 멀티에이전트 RAG 플랫폼

부동산 법원경매의 복잡한 절차와 위험한 권리관계를 **체계적으로 학습하고 연습**할 수 있는 인공지능 기반 교육 서비스입니다.  
오케스트레이터(Router)가 질문을 분석하여 전문 에이전트 그룹으로 적절히 분배하는 멀티에이전트 RAG(Retrieval-Augmented Generation) 아키텍처로 구현되었습니다.

> ⚠️ **중요 면책 고지 (Disclaimer)**  
> 본 서비스는 오직 **교육 및 학습용**으로만 제공됩니다. 특정 경매 물건에 대한 투자 권유나 법률 자문이 아니며, 실제 입찰에 참여하기 전에는 반드시 등기사항증명서, 매각물건명세서 등 공식 서류를 직접 확인하고 전문가(변호사, 법무사 등)의 검토를 거치시기 바랍니다.

---

## 🏛️ 주요 기능 및 서비스 영역

### 1. 경매 절차 안내 챗봇 (민사집행법 기반)

- 법원경매의 신청부터 매각 결정, 대금 납부, 배당 및 명도에 이르기까지 **9단계의 핵심 프로세스**에 대한 상세 Q&A를 제공합니다.
- 답변 시 항상 근거 조문(예: 민사집행법 제91조 등)을 함께 제시하여 신뢰성을 확보합니다.

### 2. 권리분석 집중 튜터

- 경매 사고 및 손실의 핵심 원인이 되는 **말소기준권리** 판단, **임차인의 대항력 유무**, 항상 인수되는 **특수 권리(유치권, 법정지상권 등)**의 개념을 1:1 맞춤 대화형으로 친절하게 지도합니다.
- 결론을 단정적으로 내리지 않고 학습자가 스스로 생각하며 추론하도록 단계별 튜터링을 제공합니다.

### 3. 실전 모의고사 및 AI 자동 채점

- 가상으로 제작된 법원 매각물건명세서와 등기부등본(을구) 데이터를 기반으로 권리분석 퀴즈를 출제합니다.
- 학습자가 답변을 기재하면 AI가 **모범 답안 키와 대조하여 항목별(말소기준권리/대항력/인수권리/위험도) 채점 및 4점 만점 피드백**을 제공합니다.

### 4. AI 입찰가 예측 시뮬레이터 (Price Oracle)

- 사용자가 선택한 물건 유형, 소재 법원, 감정가, 대출 비율, 원하는 목표 세후 수익금 등을 종합 분석하여 **수익을 극대화하는 적정 입찰가 상한선(마지노선)**을 예측합니다.
- 법원별 최근 매각 통계를 적용해 입찰가 대비 낙찰 확률 시뮬레이션 및 예상 경쟁자 수 통계를 시각화합니다.

---

## 🤖 시스템 아키텍처

### 1. 멀티에이전트 라우팅 워크플로우

```
                  [ 사용자 질문 입력 ]
                           │
                  ▼ router.py (오케스트레이터)
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   [ procedure ]        [ tutor ]         [ quiz ]
  절차 안내 에이전트  권리분석 튜터 에이전트  사례 퀴즈 에이전트
  (laws + procedures) (cases+laws+glossary) (sample_cases.json)
```

- **Router (router.py)**: LLM이 사용자의 유저 입력 의도를 분석하여 절차 안내(`procedure`), 권리분석 학습(`tutor`), 퀴즈 실행(`quiz`)으로 스마트하게 분배합니다.
- **RAG 백본 (rag.py)**: 다중 컬렉션 데이터의 임베딩 유사도 검색을 거쳐 벡터 유사 거리순 병합 및 출처 조문 추출/중복제거를 담당합니다.
- **ChromaDB 지식베이스**: clause-aware 조문 청킹을 통해 정확한 법적 근거가 담긴 4종의 데이터 컬렉션을 구축하여 답변의 환각을 방지합니다.

### 2. 지식베이스 컬렉션 구조 (총 186개 청크 빌드)

- **`auction_laws`** (`data/laws/*.md`): 민사집행법 및 주택임대차보호법 핵심 조문 (18개 청크)
- **`auction_procedures`** (`data/procedures/*.md`): 9단계 법원경매 절차 가이드 (9개 청크)
- **`auction_glossary`** (`data/glossary/glossary.json`): **150개**의 부동산 경매 핵심 전문 용어집 (150개 청크)
- **`auction_cases`** (`data/cases/sample_cases.json`): **9건**의 정교한 가상 경매 사례집 (9개 청크)

---

## 📂 프로젝트 디렉터리 구조

```
Real-Estate-Auction/
├── app.py                      # 메인 Streamlit 웹 애플리케이션 진입점
├── pyproject.toml / requirements.txt
├── .env.example / .gitignore
├── .streamlit/
│   └── config.toml             # Streamlit 테마 및 사이드바 설정
├── data/                       # 지식베이스 원천 데이터
│   ├── laws/                   # 민사집행법, 주택임대차보호법 조문 md
│   ├── procedures/             # 경매 9단계 절차 가이드 md
│   ├── glossary/               # 확장된 150개 경매 용어 JSON
│   └── cases/                  # 확장된 9개 가상 경매 사례 JSON
├── pages/                      # Streamlit 멀티페이지 라우팅 엔트리
│   ├── auction_procedure.py    # 📋 경매 절차 안내 페이지
│   ├── rights_analysis.py      # 📚 권리분석 튜터 페이지
│   ├── case_quiz.py            # 📝 사례 퀴즈 연습 페이지
│   ├── glossary.py             # 🔍 경매 용어 사전 페이지
│   └── bid_prediction.py       # 💰 AI 입찰가 예측 페이지
└── src/                        # 애플리케이션 소스 코드
    ├── core/                   # 리팩토링된 핵심 백엔드/RAG 엔진
    │   ├── __init__.py
    │   ├── common.py           # 공통 레이아웃, CSS, sys.path 설정
    │   ├── config.py           # 경로 설정 및 전역 환경변수 로더
    │   ├── providers.py        # LLM 및 임베딩 팩토리 인터페이스
    │   ├── ingest.py           # clause-aware 청킹 및 ChromaDB 빌더
    │   ├── rag.py              # 다중 컬렉션 RAG 검색 및 통합 엔진
    │   ├── agents.py           # 절차/튜터 RAG 에이전트 정의
    │   ├── router.py           # 오케스트레이션 라우터 분류기
    │   ├── quiz.py             # 가상 퀴즈 출제 및 정답 대조 채점기
    │   └── cli.py              # CLI 기반 테스트 도구
    ├── glossary/ui.py          # 초성 필터 검색 기반 용어 사전 UI
    ├── price_oracle/           # AI 입찰가 예측 시뮬레이터 엔진/UI
    │   ├── __init__.py
    │   ├── engine.py           # 비용 역산 및 낙찰 확률 연산 모델
    │   └── ui.py               # 시각화 통계 및 입력 슬라이더 UI
    ├── procedure/ui.py         # 9단계 타임라인 아코디언 및 챗 UI
    ├── quiz/ui.py              # 모의 명세서 렌더링 및 채점 피드백 UI
    └── tutor/ui.py             # 개념 족보 가이드 및 1:1 튜터 UI
```

---

## 🚀 실행 및 배포 가이드

### 1. 로컬 환경 실행 준비

```bash
# 1) 가상환경 생성 및 활성화
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Mac/Linux
source .venv/bin/activate

# 2) 필수 패키지 설치
pip install -r requirements.txt

# 3) 환경변수 설정
cp .env.example .env
# 생성된 .env 파일 내에 OpenAI 또는 Anthropic API 키를 입력합니다.
# 예시:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-...
# EMBEDDING_PROVIDER=openai
```

### 2. 지식베이스 구축 및 CLI 동작 테스트

```bash
# RAG용 ChromaDB 컬렉션 구축 (최초 1회 필수 실행)
.venv\Scripts\python.exe src/core/ingest.py

# (선택) 청킹 및 직렬화 정합성만 키 없이 테스트하고 싶을 때
.venv\Scripts\python.exe src/core/ingest.py --dry-run

# 터미널에서 백엔드 라우터 및 RAG 에이전트 응답 확인
.venv\Scripts\python.exe src/core/cli.py "말소기준권리가 뭐야?"
```

### 3. Streamlit 웹 UI 실행

```bash
# 웹 서비스 구동
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 경로로 접속하여 미려하게 디자인된 부동산 경매 AI 튜터 포털을 조작할 수 있습니다.

### 4. Streamlit Cloud 클라우드 배포

- 배포와 관련된 가이드는 별도의 [DEPLOY.md](/md/DEPLOY.md)에 상세히 기술되어 있습니다.
- `Streamlit Cloud` 배포 시, `Secrets` 대시보드 옵션에 `.env`와 동일한 양식의 API Key 값들을 TOML 형식으로 입력해 주어야 작동합니다.
- 배포 서버 구동 시 ChromaDB 폴더가 없을 경우, `common.py`에 구현된 `ensure_db()`가 동작하여 자동으로 지식베이스 임베딩 인제스트 프로세스를 실행하므로 별도의 초기 데이터 셋업 과정이 요구되지 않습니다.

---

## 🛠️ 기술 스택 및 라이브러리

- **Frontend / Portal**: Streamlit (Premium Custom styling + Tailwind CSS 폰트 제어)
- **RAG Engine / Agent**: LangChain Framework
- **Vector Database**: ChromaDB (Persistent DB)
- **Embedding Model**: OpenAI `text-embedding-3-small` / HuggingFace 로컬 한글 임베딩 전환 지원
- **LLM Model**: OpenAI `gpt-4o-mini` (초기값) / Anthropic `claude-3-haiku` 지원

---

## 🗺️ 빌드 로드맵 (완료)

- [x] **1단계**: 프로젝트 기본 설계 및 샘플 데이터 수집
- [x] **2단계**: clause-aware 마크다운 조문 청킹 스크립트 작성 (`ingest.py`)
- [x] **3단계**: 단일 RAG 기반 질의응답 및 출처 표기 백본 구축 (`rag.py`)
- [x] **4단계**: 유도형 대화 튜터 및 JSON 정답 직접 대조식 모의고사 채점기 구현 (`quiz.py`)
- [x] **5단계**: 오케스트레이터 분류 라우터 설계 (`router.py`)
- [x] **6단계**: Streamlit 채팅 UI, 퀴즈 전용 채점 폼 및 디스클레이머 푸터 연동 (`app.py`)
- [x] **7단계**: Streamlit Cloud Secrets 연동 및 배포 최적화 (`DEPLOY.md`)
- [x] **8단계**: 목표 수익률 비용 역산 및 낙찰 확률 통계 시뮬레이션 기반 Price Oracle(AI 입찰가 예측) 구현 완료
- [x] **9단계**: 백엔드/엔진 모듈을 `src/core/`로 이동하는 폴더 구조화 및 동적 경로 바인딩 리팩토링 적용 완료
