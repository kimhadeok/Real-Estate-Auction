# AI 입찰가 예측을 위한 데이터(CSV) 관리 계획 및 표준화 방안

본 문서는 법원경매 정보 페이지에서 수집한 CSV 데이터를 'AI 입찰가 예측(Price Oracle)' 서비스에 효과적으로 연동하고 관리하기 위한 전처리 규칙 및 파일 관리 계획을 정의합니다.

---

## 1. 개요 (Overview)
AI 입찰가 예측 모델의 신뢰도는 입력 데이터의 일관성에 크게 좌우됩니다. 대법원 경매정보 사이트에서 수집한 데이터는 물건의 종류(아파트, 다세대, 단독주택, 임야 등) 및 사건 형태(단독, 중복, 병합 사건)에 따라 테이블의 구조가 다르게 렌더링되거나 수동 수정 시 컬럼 개수 불일치가 발생합니다. 

따라서 수집된 CSV 파일들을 체계적으로 정제하고 통일된 규격으로 관리하는 방안을 수립합니다.

---

## 2. 현재 데이터 현황 및 문제점 분석
현재 `./data/price_oracle/` 경로에 저장된 CSV 파일들을 분석한 결과 다음과 같은 특징과 문제점이 확인되었습니다.

1. **컬럼 개수 불일치 (Schema Mismatch)**:
   - **정상 레코드**: 법원/사건번호, 물건번호, 물건용도, 소재지 및 내역, 감정평가액, 최저매각가격, 담당계/매각기일, 진행상태의 총 **8개 컬럼** 구조를 가집니다.
   - **불완전 레코드**: `auction_results_4.csv`, `auction_results_9.csv` 등 일부 파일에서 단독주택이나 근린건물 등 토지/건물 일괄 매각 건의 경우, **2개 컬럼**(`법원/사건번호` 및 `소재지 및 내역`만 존재) 형태로 데이터가 입력되어 컬럼 개수 불일치가 발생합니다.
2. **결측치 및 서식 문제**:
   - 감정평가액이나 최저매각가격 등의 필드에 쉼표(`,`)가 포함되어 있거나, 유찰 비율(`(100%)`, `(32%)` 등)이 섞여 있어 수치형 파싱 오류 위험이 존재합니다.
   - 일부 값이 공백 또는 `NaN` 상태로 존재하여 시스템 불안정을 유발할 수 있습니다.

---

## 3. 데이터 정제 및 표준화 규칙

AI 입찰가 예측 엔진이 안전하게 데이터를 읽고 분석할 수 있도록 아래의 **3대 정제 규칙**을 적용합니다.

### 규칙 ①: 모든 컬럼의 문자열(String) 타입 처리
- CSV 파일을 로드할 때 모든 컬럼을 **텍스트(String)** 타입으로 처리합니다.
- 감정가 및 최저입찰가 등에 포함된 쉼표(`,`)나 문자열 단위(원, %, 만원)로 인한 숫자 변환 오류를 방지하기 위함입니다. 필요 시 정규식을 통해 수치형 변환 프로세스를 별도로 태웁니다.

### 규칙 ②: 결측값 및 빈 셀의 공백(`""`) 대체
- 값이 비어 있거나 `NaN`, `Null`, `None` 등으로 인식되는 결측치는 모두 공백 문자열(`""`)로 일관되게 치환합니다.
- AI 예측 시 Null-safety를 보장하고 조건 검색 시의 예외 발생을 차단합니다.

### 규칙 ③: 컬럼 개수 불일치 구분 및 강제 표준화 (Padding)
- 파일 내의 각 행을 읽을 때 컬럼 개수를 검사합니다.
- 컬럼 개수가 8개 미만인 행(예: 2개 컬럼만 기입된 행)은 다음과 같이 분리하여 처리합니다.
  - **구분 및 감지**: 로드 시 컬럼 수가 8개인지 검사하여 비정상 레코드를 별도로 분류합니다.
  - **공백 패딩(Padding)**: 데이터 파이프라인에서 누락된 나머지 6개 컬럼에 빈 문자열(`""`)을 채워 넣어 **강제로 8개 컬럼 형태의 표준 스키마**를 맞춥니다.
  - **데이터 유실 방지**: 사건번호와 상세 주소만 있는 데이터라도 AI 분석 시 법원 정보 및 필지 정보를 매핑하여 활용할 수 있도록 누락 처리하지 않고 살려둡니다.

---

## 4. 효과적인 파일 관리 계획

### 4.1 디렉터리 구조 표준화
수집 단계와 정제 단계를 명확히 분리하여 데이터 오염을 방지합니다.

```
d:\My-Dev\GitHub\Real-Estate-Auction\data\price_oracle\
├── raw\           # 수집기(urlcheck.py)가 생성한 원본 CSV (페이지별 보관)
│   ├── auction_results_1.csv
│   ├── auction_results_2.csv
│   └── ...
└── processed\     # 정제 및 표준화 스크립트가 병합 완료한 단일 CSV (AI 사용 데이터)
    └── auction_results_merged.csv
```

### 4.2 데이터 파이프라인 자동화 설계
매번 수동으로 데이터를 검사하기 어렵기 때문에 아래와 같은 파이썬 정제 스크립트(`preprocess.py`)를 개발하여 주기적으로 실행하는 것을 권장합니다.

#### 파이썬 전처리 코드 예시 (Concept):
```python
import os
import pandas as pd

def standardize_csv(raw_dir, output_file):
    standard_headers = [
        "법원/사건번호", "물건번호", "물건용도", "소재지 및 내역", 
        "감정평가액", "최저매각가격", "담당계/매각기일", "진행상태"
    ]
    all_rows = []
    
    # 1. raw 폴더의 모든 CSV 순회
    for filename in os.listdir(raw_dir):
        if filename.endswith(".csv") and filename.startswith("auction_results_"):
            filepath = os.path.join(raw_dir, filename)
            
            # 모든 데이터를 문자열로 로드하고 결측치를 공백으로 치환
            df = pd.read_csv(filepath, dtype=str).fillna("")
            
            # 각 행을 순회하며 컬럼 개수 교정
            for idx, row in df.iterrows():
                row_list = list(row)
                
                # 컬럼 개수가 부족한 경우 패딩 적용
                if len(row_list) < 8:
                    row_list = row_list + [""] * (8 - len(row_list))
                elif len(row_list) > 8:
                    row_list = row_list[:8] # 넘치는 경우 자름
                    
                all_rows.append(row_list)
                
    # 2. 통합 및 저장
    merged_df = pd.DataFrame(all_rows, columns=standard_headers)
    merged_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"총 {len(merged_df)}건의 정제 및 병합 완료 -> {output_file}")

# 실행 예시
# standardize_csv("./data/price_oracle/raw", "./data/price_oracle/processed/auction_results_merged.csv")
```

---

## 5. 기대 효과
1. **AI 예측 엔진과의 호환성 극대화**: 스키마 오류로 인한 API 크래시 방지 및 예측 파이프라인 안정화.
2. **데이터 결측 안심 처리**: 유실되기 쉬운 복잡한 사건 주소 정보를 안전하게 보존하고 누락 값을 예외 없이 처리 가능.
3. **분석 효율성 증대**: 일관성 있게 정제된 텍스트 데이터를 임베딩(Embedding) 하거나 RAG(검색 증강 생성) 지식 베이스로 신속하게 변환 가능.
