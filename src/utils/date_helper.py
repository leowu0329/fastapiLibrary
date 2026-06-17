from datetime import datetime, timedelta, timezone

class DateHelper:
    @staticmethod
    def get_current_time() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def calculate_due_date(days: int = 14) -> datetime:
        return datetime.now(timezone.utc) + timedelta(days=days)

    @staticmethod
    def calculate_overdue_days(due_date: datetime) -> int:
        now = datetime.now(timezone.utc)
        if now > due_date:
            delta = now - due_date
            return delta.days
        return 0

    @staticmethod
    def calculate_fine(overdue_days: int, fine_per_day: int = 5) -> int:
        return overdue_days * fine_per_day