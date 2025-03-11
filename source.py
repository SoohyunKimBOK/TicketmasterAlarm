import time
import os
import requests
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def extract_event_date(event_url):
    """이벤트 URL에서 날짜 부분만 추출"""
    match = re.search(r'oasis-manchester-(\d{2}-\d{2}-\d{4})', event_url)
    if match:
        return match.group(1)  # 날짜 부분만 반환
    return "Unknown Date"  # 날짜를 찾지 못하면 기본값 반환

def check_tickets(driver, event_url, TARGET_PRICE, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, CARD_INFO):
    """Ticketmaster에서 Resale 티켓을 감지하는 함수"""
    try:
        driver.get(event_url)
        time.sleep(5)  # 페이지가 완전히 로드될 때까지 대기

        minus_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'Stepper__MinusButton')]"))
        )
        minus_button.click()
        find_tickets_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='findTicketsBtn']"))
        )
        find_tickets_button.click()
        checkbox_wrapper = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'Checkbox__CheckboxWrapper')]"))
        )
        checkbox_wrapper.click()
        proceed_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span/span[text()='Proceed to Buy']]"))
        )
        proceed_button.click()

        try:
            resale_ticket_label = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Verified Resale Ticket')]")))
            resale_ticket_container = resale_ticket_label.find_element(By.XPATH, "./parent::div")
            ticket_price_element = resale_ticket_container.find_element(By.XPATH, ".//span[contains(text(), '£')]")
            ticket_price = ticket_price_element.text
            event_date = extract_event_date(event_url)  # 날짜 추출
            price_match = re.search(r'\d+(\.\d+)?', ticket_price)

            if price_match:
                price_value = float(price_match.group())  # 숫자로 변환 (소수점 포함)
                if price_value < TARGET_PRICE:
                    message = f"🎟️ Verified Resale Ticket Found!\n📅 Date: {event_date}\n💰 Price: {ticket_price}"
                    print(message)
                    # send_telegram_alert(message)
                    purchase_ticket(driver, CARD_INFO)
            return True  # 티켓이 있으면 True 반환하여 종료
        except Exception as e:
            print("No Tickets Available. Retrying...")
            return False

    except Exception as e:
        print("Error")
        pass

def send_telegram_alert(message):
    """텔레그램 메시지를 보내는 함수"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        print("✅ Telegram Alert Sent!")
    except requests.exceptions.RequestException as e:
        print("❌ Telegram Alert Failed!", e)

def login(driver):
    try:
        # 이메일 입력
        email_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "email")))
        email_input.send_keys(os.getenv("EMAIL"))

        # 비밀번호 입력
        password_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys(os.getenv("PASSWORD"))

        # 로그인 버튼 클릭
        sign_in_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-bdd='sign-in-button']")))
        sign_in_button.click()

        print("✅ 로그인 완료!")

        # 로그인 후 페이지 로드 대기
        time.sleep(5)
    except Exception:
        print("🔓 로그인 페이지가 감지되지 않음. 티켓 구매 진행.")

def purchase_ticket(driver, CARD_INFO):
    """티켓 구매 프로세스 자동화"""
    try:
        # 1️⃣ Verified Resale Ticket 버튼 클릭
        resale_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Verified Resale Ticket']")))
        resale_button.click()
        print("Step6")

        # 로그인 창 감지
        sign_in_header = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Sign In')]"))
        )
        if sign_in_header:
            login(driver)

        # 2️⃣ "+" 버튼 클릭하여 티켓 개수 선택
        plus_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='increment-quantity']")))
        plus_button.click()
        print("Step7")

        # 3️⃣ 약관 동의 체크박스 클릭
        time.sleep(3)
        checkbox_span = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "(//input[@name='termsAgreed']/following-sibling::span)[last()]")))
        checkbox_span.click()
        print("Step8")

        # 4️⃣ "Continue To Payment" 버튼 클릭
        continue_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='checkout-submit']")))
        continue_button.click()
        print("Step9")


        # 1️⃣ 카드 번호 입력
        card_iframe = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='Iframe for card number']"))
        )
        driver.switch_to.frame(card_iframe)  # iframe 내부로 이동
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-fieldtype='encryptedCardNumber']"))
        ).send_keys(CARD_INFO["CARD_NUMBER"])
        driver.switch_to.default_content()  # 원래 페이지로 복귀
        print("✅ 카드 번호 입력 완료!")

        # 2️⃣ 만료일 입력
        exp_iframe = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='Iframe for expiry date']"))
        )
        driver.switch_to.frame(exp_iframe)  # iframe 내부로 이동
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-fieldtype='encryptedExpiryDate']"))
        ).send_keys(CARD_INFO["EXP_DATE"])
        driver.switch_to.default_content()
        print("✅ 만료일 입력 완료!")

        # 3️⃣ CVC 코드 입력
        sec_iframe = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='Iframe for security code']"))
        )
        driver.switch_to.frame(sec_iframe)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-fieldtype='encryptedSecurityCode']"))
        ).send_keys(CARD_INFO["SEC_CODE"])
        driver.switch_to.default_content()
        print("✅ 보안 코드 입력 완료!")

        # 4️⃣ 카드 소유자 이름 입력
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='holderName']"))
        ).send_keys(CARD_INFO["USERNAME"])
        print("✅ 카드 소유자 이름 입력 완료!")

        # 5️⃣ 집번호 입력
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='houseNumberOrName']"))
        ).send_keys(CARD_INFO["ROOM"])
        print("✅ 집번호 입력 완료!")

        # 6️⃣ 도로명 입력
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='street']"))
        ).send_keys(CARD_INFO["ROAD"])
        print("✅ 도로명 입력 완료!")

        # 7️⃣ 도시 입력
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='city']"))
        ).send_keys(CARD_INFO["CITY"])
        print("✅ 도시 입력 완료!")

        # 8️⃣ 우편번호 입력
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='postalCode']"))
        ).send_keys(CARD_INFO["POSTCODE"])
        print("✅ 우편번호 입력 완료!")

        # 6️⃣ "Pay" 버튼 클릭
        pay_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'adyen-checkout__button--pay')]"))
        )
        # pay_button.click()
        print("✅ Pay 버튼 클릭 완료!")

        print("✅ Purchase Completed! Waiting 3 minutes...")
        time.sleep(180)  # 3분 대기

    except Exception as e:
        print(f"⚠️ Purchase process failed: {e}")