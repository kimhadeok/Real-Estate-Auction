# -*- coding: utf-8 -*-
"""
urlcheck.py — 법원경매 사이트 검색 및 결과 CSV 저장 스크립트 (지정 페이지 수집 기능)
"""

import sys
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException, UnexpectedAlertPresentException

# ==============================================================================
# 설정 변수: 수집할 페이지 번호를 지정하세요.
# (스크립트 실행 시 인자로도 입력받을 수 있습니다: python urlcheck.py 3)
# ==============================================================================
PAGE_TO_CRAWL = 1

# 실행 인자가 있으면 해당 값을 수집할 페이지 번호로 사용
if len(sys.argv) > 1:
    try:
        PAGE_TO_CRAWL = int(sys.argv[1])
    except ValueError:
        print(f"⚠️ 올바르지 않은 페이지 번호 인자입니다. 기본값인 {PAGE_TO_CRAWL}페이지를 수집합니다.")

# Windows 콘솔 인코딩 문제를 해결하기 위해 stdout/stderr를 UTF-8로 설정
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def setup_driver():
    print("[1/5] Chrome WebDriver 초기화 중...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    return driver

def scrape_auction():
    url = "https://www.courtauction.go.kr/pgj/index.on?w2xPath=/pgj/ui/pgj100/PGJ151F00.xml"
    driver = None
    try:
        driver = setup_driver()
        
        print(f"[2/5] 페이지 이동 중: {url}")
        driver.get(url)
        
        # WebSquare 로딩 대기
        time.sleep(5)
        
        # 1. 검색 버튼 클릭 (사용자 요구사항에 맞추어 mf_wfm_mainFrame_btn_rletInit 클릭)
        target_btn_id = "mf_wfm_mainFrame_btn_rletInit"
        print(f"[3/5] 버튼 클릭 시도 (ID: {target_btn_id})")
        
        wait = WebDriverWait(driver, 15)
        
        button_to_click = None
        try:
            button_to_click = driver.find_element(By.ID, target_btn_id)
            print(f"-> 지정된 ID '{target_btn_id}' 버튼을 발견했습니다.")
        except Exception:
            print(f"-> 지정된 ID '{target_btn_id}' 버튼을 찾지 못했습니다.")
            
        actual_search_btn_id = "mf_wfm_mainFrame_btn_gdsDtlSrch"
        actual_search_button = None
        try:
            actual_search_button = driver.find_element(By.ID, actual_search_btn_id)
            print(f"-> 실제 검색 버튼 '{actual_search_btn_id}'을 발견했습니다.")
        except Exception:
            print(f"-> 실제 검색 버튼 '{actual_search_btn_id}'을 찾지 못했습니다.")

        # 사용자가 지정한 초기화/검색 버튼 클릭
        if button_to_click:
            print(f"-> 버튼 클릭: {button_to_click.get_attribute('value')} (ID: {target_btn_id})")
            button_to_click.click()
            time.sleep(2)
            
            # 혹시 경고창이 뜨면 수락
            try:
                alert = driver.switch_to.alert
                print(f"경고창 발생: {alert.text}")
                alert.accept()
            except NoAlertPresentException:
                pass

        # 만약 사용자가 지정한 버튼이 초기화 버튼인 경우, 실제 검색을 수행하기 위해 검색 버튼을 클릭
        if actual_search_button and button_to_click and "초기화" in (button_to_click.get_attribute("value") or ""):
            print(f"-> 지정된 버튼이 초기화 버튼이므로, 실제 검색을 위해 '{actual_search_btn_id}' 버튼을 클릭합니다.")
            actual_search_button.click()
            time.sleep(2)
            
            # 경고창 수락
            try:
                alert = driver.switch_to.alert
                print(f"경고창 발생: {alert.text}")
                alert.accept()
            except NoAlertPresentException:
                pass
        elif not button_to_click and actual_search_button:
            print(f"-> 지정된 버튼을 찾을 수 없어 실제 검색 버튼 '{actual_search_btn_id}'을 클릭합니다.")
            actual_search_button.click()
            time.sleep(2)

        # 2. 결과 로드 대기
        print("[4/5] 검색 결과 로드 대기 중...")
        grid_table_id = "mf_wfm_mainFrame_grd_gdsDtlSrchResult_body_table"
        
        try:
            # 테이블 내부 tr 요소가 채워질 때까지 대기
            wait.until(EC.presence_of_element_located((By.XPATH, f"//table[@id='{grid_table_id}']//tr")))
            print("-> 검색 결과 테이블 로드 완료")
        except TimeoutException:
            print("⚠️ 검색 결과 로드 타임아웃.")
            return

        # 3. 지정된 페이지로 이동
        # ul태그 class="w2pageList_ul" 안의 자식 li태그 class="w2pageList_li_label"을 찾습니다.
        try:
            print(f"-> 페이지 목록 탐색 중 (목표 페이지: {PAGE_TO_CRAWL}페이지)...")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.w2pageList_ul li.w2pageList_li_label")))
            page_elements = driver.find_elements(By.CSS_SELECTOR, "ul.w2pageList_ul li.w2pageList_li_label")
            print(f"-> 발견된 총 페이지 개수: {len(page_elements)}개")
            
            target_idx = PAGE_TO_CRAWL - 1
            if 0 <= target_idx < len(page_elements):
                print(f"-> {PAGE_TO_CRAWL}페이지 버튼 클릭 (텍스트: '{page_elements[target_idx].text}')")
                page_elements[target_idx].click()
                time.sleep(3)  # 페이지 로드를 위한 안전 대기
                # 테이블 로드 재확인
                wait.until(EC.presence_of_element_located((By.XPATH, f"//table[@id='{grid_table_id}']//tr")))
            else:
                print(f"⚠️ 요청한 {PAGE_TO_CRAWL}페이지는 범위를 벗어났습니다 (총 1~{len(page_elements)}페이지). 기본 1페이지로 진행합니다.")
        except Exception as pe:
            print(f"⚠️ 페이지네이션 요소 탐색 또는 클릭 실패: {pe}. 현재 로드된 페이지로 수집을 진행합니다.")

        # 4. 데이터 파싱
        # 현재 화면에 로드된 tr 요소들 추출
        rows = driver.find_elements(By.XPATH, f"//table[@id='{grid_table_id}']//tr")
        print(f"-> 수집된 tr 행 개수: {len(rows)}개")
        
        raw_rows = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [cell.text.strip().replace("\n", " ") for cell in cells]
            if any(row_data):
                raw_rows.append(row_data)

        # 2줄짜리 물리적 행 병합
        combined_data = []
        i = 0
        while i < len(raw_rows) - 1:
            row1 = raw_rows[i]
            row2 = raw_rows[i+1]
            
            if len(row1) >= 8 and len(row2) >= 3:
                court_case = row1[1]  # 법원/사건번호
                item_no = row1[2]     # 물건번호
                address = row1[3]     # 소재지 및 내역
                appraisal = row1[6]   # 감정평가액
                dept_date = row1[7]   # 담당계/매각기일
                
                usage = row2[0]       # 물건용도
                min_price = row2[1]   # 최저매각가격
                status = row2[2]      # 진행상태
                
                combined_data.append([
                    court_case,
                    item_no,
                    usage,
                    address,
                    appraisal,
                    min_price,
                    dept_date,
                    status
                ])
                i += 2
            else:
                i += 1

        print(f"-> 병합 완료된 물건 개수: {len(combined_data)}개")
        
        if not combined_data:
            print("❌ 수집된 데이터가 없습니다.")
            return

        # 5. DataFrame 생성 및 CSV 저장
        headers = [
            "법원/사건번호", 
            "물건번호", 
            "물건용도", 
            "소재지 및 내역", 
            "감정평가액", 
            "최저매각가격", 
            "담당계/매각기일", 
            "진행상태"
        ]
        
        df = pd.DataFrame(combined_data, columns=headers)
        
        # 저장 경로 폴더 생성
        output_dir = "./data/price_oracle"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"auction_results_{PAGE_TO_CRAWL}.csv")
        
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"[5/5] 성공! {PAGE_TO_CRAWL}페이지 데이터를 '{output_file}'에 저장했습니다.")
        
        # 미리보기
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(f"\n=== {PAGE_TO_CRAWL}페이지 데이터프레임 미리보기 ===")
        print(df.head(5))
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        if driver:
            screenshot_path = "error_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"-> 디버깅용 스크린샷 저장: '{screenshot_path}'")
    finally:
        if driver:
            driver.quit()
            print("-> 브라우저를 종료했습니다.")

if __name__ == "__main__":
    scrape_auction()
