from datetime import datetime, timedelta, timezone

class DateHelper:
    @staticmethod
    def get_current_time() -> datetime:
        # 統一使用帶有 UTC 時區的標準時間
        return datetime.now(timezone.utc)

    @staticmethod
    def calculate_due_date(days: int = 14) -> datetime:
        return datetime.now(timezone.utc) + timedelta(days=days)

    @staticmethod
    def calculate_overdue_days(due_date: datetime) -> int:
        now = datetime.now(timezone.utc)
        
        # 核心防禦：如果從 MongoDB 拿出來的 due_date 沒有時區資訊 (naive)
        # 強制幫它加上 UTC 時區 (aware)，消除相減時的型別衝突
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)
            
        if now > due_date:
            delta = now - due_date
            return delta.days
        return 0

    @staticmethod
    def calculate_fine(overdue_days: int, fine_per_day: int = 5) -> int:
        return overdue_days * fine_per_day