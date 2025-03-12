import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from source_test import check_tickets, send_telegram_alert, extract_event_date, purchase_ticket

# 환경 변수 로드
load_dotenv()

# 설정 값 가져오기
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TARGET_PRICE = 500
WAIT_TIME = 10

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
    "https://www.ticketmaster.co.uk/oasis-manchester-12-07-2025/event/3E006110F234138D"
]

# ChromeDriver 설정
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # 화면 없이 실행
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

while True:
    for url in EVENT_URLS:
        check_tickets(driver, url, TARGET_PRICE, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, CARD_INFO)
    print(f"⏳ Waiting {WAIT_TIME} seconds before checking again...")
    time.sleep(WAIT_TIME)
