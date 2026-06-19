# 🚀 Streamlit Cloud 배포 가이드

## 1. 사전 준비

- GitHub 계정
- [Streamlit Cloud](https://streamlit.io/cloud) 계정 (GitHub 연동)
- OpenAI API 키

## 2. GitHub에 푸시

```bash
git add .
git commit -m "feat: 멀티에이전트 RAG 경매 교육 서비스"
git push origin main
```

> ⚠️ `.env` 파일은 `.gitignore`에 포함되어 있으므로 푸시되지 않습니다.
> API 키는 절대 GitHub에 올리지 마세요!

## 3. Streamlit Cloud 연결

1. [share.streamlit.io](https://share.streamlit.io) 접속
2. **New app** 클릭
3. 설정:
   - **Repository**: 본 프로젝트 리포지토리 선택
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. **Deploy** 클릭

## 4. Secrets 설정 (중요!)

Streamlit Cloud에서는 `.env` 대신 **Secrets**를 사용합니다.

1. 배포된 앱의 **Settings** → **Secrets** 메뉴
2. 아래 TOML 형식으로 입력:

```toml
OPENAI_API_KEY = "sk-your-openai-api-key-here"
LLM_PROVIDER = "openai"
EMBEDDING_PROVIDER = "openai"
```

3. **Save** 클릭 → 앱이 자동으로 재시작됩니다

> `app.py`가 Secrets를 환경변수로 자동 연결합니다.

## 5. 첫 접속 시 자동 구축

배포 후 첫 접속 시 `chroma_db`가 없으면 **자동으로 지식베이스를 구축**합니다.
이 과정은 1~2분 소요될 수 있습니다 (임베딩 생성).

## 6. 트러블슈팅

### ❌ `ModuleNotFoundError`
- `requirements.txt`에 누락된 패키지가 없는지 확인
- Streamlit Cloud는 `requirements.txt`를 자동으로 설치합니다

### ❌ API 키 오류
- Secrets에 `OPENAI_API_KEY`가 올바르게 설정되었는지 확인
- 키 앞뒤의 공백 제거

### ❌ 빌드 실패
- Python 버전 확인 (`runtime.txt`에 `python-3.11.0` 등 지정 가능)
- ChromaDB는 빌드 시 C++ 컴파일이 필요할 수 있음 → `packages.txt`에 `build-essential` 추가

### ⏱️ 콜드스타트가 느림
- 무료 플랜은 앱이 비활성화되면 슬립 → 재접속 시 부팅 시간 발생
- 첫 접속 시 DB 구축이 겹치면 더 느릴 수 있음

## 7. 비용 및 주의사항

- **Streamlit Cloud 무료 플랜**: 퍼블릭 앱 무제한
- **OpenAI API**: 사용량에 따라 과금 (GPT-4o-mini는 상대적으로 저렴)
- **공개 URL**: 무료 플랜은 앱이 공개됨 — 민감한 데이터 주의
- **슬립 정책**: 일정 시간 미사용 시 슬립 → 재접속 시 부팅

## 8. 로컬 실행 (개발용)

```bash
pip install -r requirements.txt
cp .env.example .env        # .env에 OPENAI_API_KEY 입력
python ingest.py --dry-run  # 청킹만 검증 (키 불필요)
python ingest.py            # DB 구축 (키 필요)
streamlit run app.py        # 브라우저에서 열림
```
