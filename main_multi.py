import time
import os
import requests
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from source_multi import check_tickets

# 환경 변수 로드
load_dotenv()

# 설정 값 가져오기
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TARGET_PRICE = 200  # 목표 가격 (이 가격 미만이라면 구매 진행)
WAIT_TIME = 3

CARD_INFO = {
    "CARD_NUMBER": os.getenv("CARD_NUMBER"),
    "EXP_DATE": os.getenv("EXP_DATE"),
    "SEC_CODE": os.getenv("SEC_CODE"),
    "USERNAME": os.getenv("USERNAME"),
    "ROOM": os.getenv("ROOM"),
    "ROAD": os.getenv("ROAD"),
    "CITY": os.getenv("CITY"),
    "POSTCODE": os.getenv("POSTCODE"),
    "EMAIL": os.getenv("EMAIL"),
    "PASSWORD": os.getenv("PASSWORD")
}

EVENT_URLS = [
    "https://www.ticketmaster.co.uk/oasis-manchester-11-07-2025/event/3E006110E3D61217",
    "https://www.ticketmaster.co.uk/oasis-manchester-12-07-2025/event/3E006110F234138D",
    # "https://www.ticketmaster.co.uk/oasis-manchester-16-07-2025/event/3E006114FEEB15DB",
    "https://www.ticketmaster.co.uk/oasis-manchester-19-07-2025/event/3E0061140C46160E",
    "https://www.ticketmaster.co.uk/oasis-manchester-20-07-2025/event/3E0061140C491612"
    # "https://www.ticketmaster.co.uk/billie-eilish-hit-me-hard-and-manchester-19-07-2025/event/3700609A8CFC2113",
    # "https://www.ticketmaster.co.uk/billie-eilish-hit-me-hard-and-manchester-20-07-2025/event/3700609DE6D83250",
    # "https://www.ticketmaster.co.uk/billie-eilish-hit-me-hard-and-manchester-22-07-2025/event/3700609DE6DB3254",
    # "https://www.ticketmaster.co.uk/billie-eilish-hit-me-hard-and-manchester-23-07-2025/event/3700609DE6DD3260"
]

# ChromeDriver 설정
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # 화면 없이 실행
options.add_argument("--disable-background-timer-throttling")  # 백그라운드에서 타이머 동작 유지
options.add_argument("--disable-renderer-backgrounding")  # 백그라운드에서도 UI 렌더링 유지
options.add_argument("--disable-dev-shm-usage")  # Shared Memory 사용 최소화
options.add_argument("--disable-gpu")  # GPU 사용 방지 (서버 환경에서 실행할 경우 필요)
options.add_argument("--no-sandbox")  # 보안 정책 비활성화 (Docker 같은 환경에서 실행할 경우 필요)

def run_browser(url):
    """각 URL을 처리할 개별 드라이버 실행"""
    while True:  # 무한 루프 실행 (스레드가 종료되지 않도록)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        check_tickets(driver, url, TARGET_PRICE, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, CARD_INFO, WAIT_TIME)
        driver.quit()

# 여러 개의 브라우저 실행 (멀티스레딩)
threads = []
for url in EVENT_URLS:
    thread = threading.Thread(target=run_browser, args=(url,))
    threads.append(thread)
    thread.start()

# 모든 스레드가 끝날 때까지 대기
for thread in threads:
    thread.join()

# 여러 개의 브라우저 실행 (멀티스레딩)
threads = []
for url in EVENT_URLS:
    thread = threading.Thread(target=run_browser, args=(url,), daemon=True)  # daemon=True 설정 (메인 프로그램 종료 시 자동 정리)
    threads.append(thread)
    thread.start()

# 모든 스레드가 무한 루프로 실행됨
while True:
    pass  # 메인 스레드가 종료되지 않도록 유지