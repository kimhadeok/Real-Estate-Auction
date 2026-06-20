# 각 에이전트별 전용 기획/기술 문서 생성 계획서

본 계획서는 현재 부동산 경매 AI 튜터 RAG 플랫폼 프로젝트의 구성 요소를 세부 역할인 기획(`@pla`), 개발(`@dev`), 디자인(`@des`) 관점으로 분류·분석하고, 이를 각 에이전트 전용 가이드라인 및 상세 문서인 `md/pla.md`, `md/dev.md`, `md/des.md`로 기획 및 생성하는 작업 계획입니다.

## 사용자 검토 요구사항
- **에이전트별 분석 방향**:
  1. **기획자 관점 (`md/pla.md`)**: 서비스 핵심 가치, 경매 도메인 기획(9단계 절차 및 권리분석 핵심 쟁점), RAG 지식베이스 데이터셋 구축 기획, 시나리오 및 기능 사양(Price Oracle 및 사례 퀴즈 설계 의도), 면책 조항(Disclaimer) 등 정책 정리.
  2. **개발자 관점 (`md/dev.md`)**: 프로젝트 아키텍처, `src/core/` 하위 모듈별 소스 코드 상세 명세 및 동작 원리, 멀티에이전트 라우팅 및 RAG 로직, 의존성 패키지 관리, 가상환경 구성 및 디렉토리 트리.
  3. **디자이너 관점 (`md/des.md`)**: 화면 UI 설계 원칙, 레이아웃 규격(GNB TOP 메뉴 구성, 사이드바 숨김), 테마 컬러 시스템(Primary/Secondary/Accent/Warning 등), 페이지별 시각요소 배치(타임라인, 아코디언, 채점 피드백, 차트 등), 공통 CSS 주입 기법.

---

## 제안된 변경 사항

### [NEW] [pla.md](file:///d:/My-Dev/GitHub/Real-Estate-Auction/md/pla.md)
- 기획 에이전트가 작성한 기획 관점의 전체 서비스 기획서 및 데이터 스펙 명세서입니다.

### [NEW] [dev.md](file:///d:/My-Dev/GitHub/Real-Estate-Auction/md/dev.md)
- 개발 에이전트가 작성한 백엔드 아키텍처 및 소스 모듈 명세서입니다.

### [NEW] [des.md](file:///d:/My-Dev/GitHub/Real-Estate-Auction/md/des.md)
- 디자인 에이전트가 작성한 프론트엔드 UI 디자인 및 CSS 스타일 명세서입니다.

---

## 검증 계획

### 수동 검증
- 생성된 3개 파일(`md/pla.md`, `md/dev.md`, `md/des.md`)이 마크다운 포맷에 맞추어 올바르게 작성되었는지 검토합니다.
