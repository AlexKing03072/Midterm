# 博客來 LLM 書籍爬蟲與資料庫 CLI

## 專案簡介

這是一個 Python 專案，功能如下：

- 自動爬取博客來網路書店「LLM」相關書籍資料。
- 自動抓取所有分頁的書籍資訊。
- 將資料清理後存入 SQLite 資料庫。
- 提供命令列介面 (CLI) 查詢書籍，支持書名或作者模糊搜尋。

專案架構：

project/
│
├─ app.py # 主程式，CLI 入口
├─ scraper.py # 爬蟲功能
├─ database.py # SQLite 資料庫操作
├─ books.db # SQLite 資料庫（程式執行後生成）
└─ requirements.txt

## 功能說明

### 1. 更新書籍資料庫

- 爬取博客來「LLM」書籍資訊。
- 自動抓取所有分頁。
- 將資料存入 SQLite，避免重複寫入。

### 2. 查詢書籍

- 支援依 **書名** 或 **作者** 查詢。
- 使用模糊比對 (`LIKE '%keyword%'`)。
- 若找到資料，格式化印出結果；若無，顯示「查無資料」。

### 3. 離開系統

- 結束程式。

---

## 安裝方法

1. 建議使用虛擬環境：
```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows