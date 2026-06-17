# 圖書館管理系統後端 (FastAPI + MongoDB Cloud)

本系統專為企業級彈性擴充設計，採用縱向模組化切分 (Modular Monolith) 搭配 Clean Code 精神建構。

## 本地開發步驟

1. 複製環境變數設定：
   ```bash
   cp .env.example .env

1. 執行：
   ```bash
   uvicorn main:app --reload