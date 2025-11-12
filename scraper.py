# scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By # 元素定位方法
from selenium.webdriver.support.ui import WebDriverWait # 等待條件
from selenium.webdriver.support import expected_conditions as EC # 預期條件，搭配 WebDriverWait 使用
from selenium.common.exceptions import (
    TimeoutException, # 超時例外
    NoSuchElementException, # 找不到元素例外
    ElementClickInterceptedException, # 元素點擊中斷例外
)
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options # 使用 chrome 瀏覽器
from webdriver_manager.chrome import ChromeDriverManager

# --- 標準函式庫導入 (Standard Library Imports) ---
from typing import List, Dict # type hint
import re
import time


def scrape_books() -> List[Dict]:
    """
    從博客來爬取「LLM」相關書籍資料，模擬搜尋並處理分頁。

    Returns:
        books (List[Dict]): 書籍資料列表，每本書包含 title, author, price, link
    """
    books: List[Dict] = []

    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--window-size=1920,1080")

    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
    except Exception as e:
        print(f"WebDriver 啟動失敗: {e}")
        return books

    try:
        driver.get("https://www.books.com.tw/")
        time.sleep(3)  # 等待首頁載入

        try:
            close_ad = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "close_top_banner"))
            )
            close_ad.click()
            time.sleep(1)  # 等待廣告消失
        except TimeoutException:
            pass  # 沒有廣告就忽略

        #     # 關閉可能的彈窗
        # try:
        #     close_btn = WebDriverWait(driver, 5).until(
        #         EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-close, .popup-close"))
        #     )
        #     close_btn.click()
        #     time.sleep(1)
        # except TimeoutException:
        #     pass  # 沒有彈窗就忽略

        try:
            search_input = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "key"))
            )
            search_input.clear()
            search_input.send_keys("LLM")
            search_button = driver.find_element(By.CSS_SELECTOR, "button.search_btn")
            search_button.click()
        except TimeoutException:
            print("搜尋框載入超時，請確認網路或網站變動")
            return books

        # 等待搜尋結果頁載入
        time.sleep(3)
        # 關閉廣告
        try:
            close_ad = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "close_top_banner"))
            )
            close_ad.click()
            time.sleep(1)  # 等待廣告消失
        except TimeoutException:
            pass  # 沒有廣告就忽略

        try:
            # 確保頁面已經靜止
            time.sleep(2)

            # 1. 嘗試定位到 <label> 元素
            book_category_label = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.ID, "filter_cat_1_1")
                )
            )

            # 2. 使用 JavaScript 執行點擊
            driver.execute_script("arguments[0].click();", book_category_label)
            #print("成功使用 JavaScript 點擊「圖書」分類篩選。")

            # 等待篩選結果載入 (可能需要較長時間)
            time.sleep(5)
            #失效
            # book_category = WebDriverWait(driver, 10).until(
            #     EC.element_to_be_clickable((By.ID, "filter_cat_1_1"))
            # )
            # 勾選「圖書」分類
        except TimeoutException:
            print("圖書分類按鈕載入超時，將使用預設搜尋結果")

        # 等待書籍列表區域載入
        current_page = 1
        try:
            # 定位 select 元素
            select_elem = driver.find_element(By.ID, "page_select")

            # 取第一個 option 文字
            total_pages_text = select_elem.find_element(By.TAG_NAME, "option").text  # "共 3 頁"

            total_pages = int(re.search(r'\d+', total_pages_text).group())
            #print(total_pages)  # 3
        except Exception:
            print("無法取得總頁數，預設為 1 頁")
            total_pages = 1

        print(f"偵測到總共有 {total_pages} 頁。")

        while True:
            print(f"正在爬取第 {current_page} / {total_pages} 頁...")
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-searchbox"))
                )
            except TimeoutException:
                print(f"第 {current_page} 頁書籍列表載入超時，跳過")
                continue
            items = driver.find_elements(By.CSS_SELECTOR, "div.table-td[id^='prod-itemlist-']")
            #print(f"本頁找到 {len(items)} 本書籍。")
            for item in items:
                try:
                    a_tag = item.find_element(By.CSS_SELECTOR, "h4 a")
                    title = a_tag.text.strip()
                    link = a_tag.get_attribute("href")
                except NoSuchElementException:
                    title = "N/A"
                    link = "N/A"

                try:
                    authors = item.find_elements(By.CSS_SELECTOR, "p.author a")
                    author = ",".join([a.text.strip() for a in authors]) if authors else "N/A"
                except Exception:
                    author = "N/A"

                try:
                    li_text = item.find_element(By.CSS_SELECTOR, "ul.price li").text
                    # 尋找第一個大於 0 的數字
                    nums = re.findall(r"\d+", li_text)
                    price = int(nums[-1]) if nums else 0  # 取最後一個數字，通常是價格
                except Exception:
                    price = 0

                books.append({
                    "title": title,
                    "author": author,
                    "price": price,
                    "link": link
                })

            current_page += 1

            # 下一頁
            if(current_page > total_pages):
                break
            try:
                next_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "next"))
                )
                next_btn.click()
                time.sleep(1)
            except NoSuchElementException:
                break
            except ElementClickInterceptedException:
                # 透過 JavaScript 點擊
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(1)

    finally:
        driver.quit()

    return books
