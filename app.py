# app.py
import sys
from scraper import scrape_books
from database import init_db, insert_books, query_by_title, query_by_author

def print_book_row(b):
    # 格式化印出單筆書籍
    print(f"書名：{b['title']}")
    print(f"作者：{b['author']}")
    print(f"價格：{b['price']}")


def update_database_flow() -> None:
    """
    從博客來爬取最新書籍資料並更新 SQLite 資料庫。

    過程：
    - 顯示總頁數
    - 每頁爬取完成後顯示進度
    - 寫入資料庫並回報新增筆數
    """
    print("開始從網路爬取最新書籍資料...")

    # 爬取書籍， scrape_books 會回傳書籍列表
    books = scrape_books()

    total_fetched = len(books)
    print("爬取完成。")

    # 寫入資料庫
    inserted = insert_books(books)
    print(f"資料庫更新完成！共爬取 {total_fetched} 筆資料，新增了 {inserted} 筆新書記錄。")

def query_flow():
    while True:
        print("\n--- 查詢書籍 ---")
        print("a. 依書名查詢")
        print("b. 依作者查詢")
        print("c. 返回主選單")
        print("---------------")
        ch = input("請選擇查詢方式 (a-c):").strip()
        if ch == "c":
            return
        elif ch == "a":
            kw = input("輸入書名關鍵字：").strip()
            if not kw:
                print("關鍵字不可為空。")
                continue
            rows = query_by_title(kw)
            if not rows:
                print("查無資料")
            else:
                print("\n====================")
                for r in rows:
                    print_book_row(r)
                    if r != rows[-1]: # -1表示最後一筆
                        print("---")
                print("====================")
        elif ch == "b":
            kw = input("輸入作者關鍵字：").strip()
            if not kw:
                print("關鍵字不可為空。")
                continue
            rows = query_by_author(kw)
            if not rows:
                print("查無資料")
            else:
                print("\n====================")
                for r in rows:
                    print_book_row(r)
                    if r != rows[-1]: # -1表示最後一筆
                        print("---")
                print("====================")
        else:
            print("無效選項，請重新輸入。")


def main():
    init_db()
    while True:
        print("\n----- 博客來 LLM 書籍管理系統 -----")
        print("1. 更新書籍資料庫")
        print("2. 查詢書籍")
        print("3. 離開")
        print("---------------------------------")
        choice = input("請選擇操作選項 (1-3):").strip()
        if choice == "3":
            print("感謝使用，系統已退出。")
            sys.exit(0) # 傳給作業系統的退出狀態碼（exit code）
        elif choice == "1":
            update_database_flow()
        elif choice == "2":
            query_flow()
        else:
            print("無效選項，請重新輸入。")

if __name__ == "__main__":
    main()