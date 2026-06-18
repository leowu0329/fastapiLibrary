from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from config.database import get_database
from src.modules.books.book_repository import BookRepository
from src.modules.books.book_service import BookService
from src.modules.books.book_entity import BookCreate, BookUpdate, BookResponse
from src.middlewares.auth import verify_admin
from typing import List
import csv
import io
import re

router = APIRouter(prefix="/books", tags=["圖書與館藏管理"])

# 依賴注入取得服務層
def get_book_service(db=Depends(get_database)):
    repo = BookRepository(db)
    return BookService(repo)

# --- 1. 🥇 終極強固修正版：批次匯入圖書資料 CSV (支援逗號、分號、Tab 鍵智慧自適應) ---
@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_books_from_csv(
    file: UploadFile = File(...), 
    service: BookService = Depends(get_book_service), 
    admin=Depends(verify_admin)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="不合法的檔案格式，目前批次匯入僅支援標準 .csv 檔案"
        )
    
    try:
        contents = await file.read()
        
        # 智慧多編碼相容解析 (相容 UTF-8 繁中與微軟 Excel CP950)
        try:
            decoded_text = contents.decode('utf-8-sig')
        except UnicodeDecodeError:
            try:
                decoded_text = contents.decode('cp950')
            except Exception as enc_err:
                raise HTTPException(status_code=400, detail=f"檔案編碼錯誤，無法解析: {str(enc_err)}")
        
        text_stream = io.StringIO(decoded_text)
        
        # 💡 【核心修正點一】：在分隔符號候選清單中，正式加入 '\t' (Tab 鍵)
        # 這能讓 csv.Sniffer 完美識別出微軟 Excel 所匯出的高品質制表符表格數據
        try:
            sample = text_stream.read(2048)
            text_stream.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters=',;\t')
            csv_reader = csv.reader(text_stream, dialect)
        except Exception:
            text_stream.seek(0)
            csv_reader = csv.reader(text_stream)

        # 💡 【核心修正點二】：強固型表頭智慧判定過濾
        # 只要第一行任何一處包含了 ID、書、名、作者、ISBN，就判定它是欄位標題，必須果斷跳過！
        first_row = next(csv_reader, None)
        if first_row:
            first_row_str = "".join(first_row).upper()
            if any(kw in first_row_str for kw in ["ID", "書", "名", "作者", "ISBN"]):
                pass # 精確判定為欄位名稱列，順暢跳過，不進行退回！
            else:
                # 沒偵測到任何表頭關鍵字，代表是無表頭的純數據，這時才回退指針
                text_stream.seek(0)
        
        inserted_count = 0
        errors = []
        
        for row in csv_reader:
            # 安全防禦：過濾真實空行
            if not row or len([col for col in row if col.strip()]) < 2:
                continue
                
            try:
                # 💡 【核心修正點三】：除了 strip() 空格，必須連同外圍的引號 `"` 與 `'` 一併清除乾淨
                title = row[1].strip().strip('"').strip("'").strip() if len(row) > 1 else ""
                author = row[2].strip().strip('"').strip("'").strip() if len(row) > 2 else "匿名作者"
                category = row[4].strip().strip('"').strip("'").strip() if len(row) > 4 else "資訊科學"
                
                # 💡 【核心修正點四】：超強效正則純數字提取
                # 完美將公式鎖定型 `="9789862115336"` 或帶有單引號的 `'0123456789` 全部洗回乾淨的純數字字串
                raw_cell_isbn = str(row[3])
                clean_isbn_match = re.findall(r'\d+', raw_cell_isbn)
                clean_isbn = "".join(clean_isbn_match) if clean_isbn_match else ""
                
                # 洗清庫存整數，防禦非數字字元
                raw_stock_str = str(row[5]).strip().strip('"').strip() if len(row) > 5 else "1"
                stock = int(raw_stock_str) if raw_stock_str.isdigit() else 1
                
                # 基礎必填欄位防守
                if not title or not clean_isbn:
                    errors.append(f"跳過不完整列: 書名為 '{title}'，洗滌後之 ISBN 為 '{clean_isbn}'")
                    continue

                # 封裝並進行強型別校驗
                book_data = BookCreate(
                    title=title,
                    author=author,
                    isbn=clean_isbn,
                    category=category,
                    stock=stock
                )
                
                # 真正呼叫與新版儲存庫對齊的 add_book 方法，寫入遠端 MongoDB Atlas
                await service.add_book(book_data)
                inserted_count += 1
                
            except Exception as row_err:
                errors.append(f"跳過書籍 '{row[1] if len(row)>1 else '未知'}': {str(row_err)}")
                continue
            
        return {
            "status": "success",
            "inserted_count": inserted_count,
            "message": f"匯入作業圓滿結束。智慧解碼與自適應解析引擎成功洗入 {inserted_count} 筆新藏書至 MongoDB Cloud！",
            "details": errors[:5]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解析匯入檔案時發生系統內部崩潰: {str(e)}"
        )

# --- 2. 上架新書 (單筆) ---
@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def add_new_book(book_in: BookCreate, service: BookService = Depends(get_book_service), admin=Depends(verify_admin)):
    return await service.add_book(book_in)

# --- 3. 搜尋/獲取所有圖書 ---
@router.get("/", response_model=List[BookResponse])
async def search_books(keyword: str = "", service: BookService = Depends(get_book_service)):
    return await service.query_books(keyword)

# --- 4. 更新圖書資訊/調整庫存數量 ---
@router.put("/{book_id}", response_model=BookResponse)
async def update_book(book_id: str, book_in: BookUpdate, service: BookService = Depends(get_book_service), admin=Depends(verify_admin)):
    updated_book = await service.modify_book(book_id, book_in)
    if not updated_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="編輯失敗，找不到對應的圖書紀錄 ID")
    return updated_book

# --- 5. 報廢/永久下架圖書 ---
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: str, service: BookService = Depends(get_book_service), admin=Depends(verify_admin)):
    success = await service.remove_book(book_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="下架失敗，找不到對應的圖書紀錄 ID")
    return None