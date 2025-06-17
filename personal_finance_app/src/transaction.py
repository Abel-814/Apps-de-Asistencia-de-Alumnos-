from datetime import date, datetime

class Transaction:
    def __init__(self, date: date | str, description: str, type: str, category: str, amount: float):
        if isinstance(date, str):
            try:
                self.date = datetime.fromisoformat(date).date()
            except ValueError:
                raise ValueError("Date string must be in ISO format (YYYY-MM-DD)")
        elif isinstance(date, date):
            self.date = date
        else:
            raise TypeError("Date must be a datetime.date object or an ISO format string")
        self.description = description
        self.type = type
        self.category = category
        self.amount = amount

    def __repr__(self):
        return (f"Transaction(date={self.date!r}, description={self.description!r}, "
                f"type={self.type!r}, category={self.category!r}, amount={self.amount!r})")

    def to_dict(self):
        return {
            "date": self.date.isoformat(),
            "description": self.description,
            "type": self.type,
            "category": self.category,
            "amount": self.amount
        }

    @staticmethod
    def from_dict(data: dict):
        # Ensure date is parsed correctly from string to date object
        date_obj = date.fromisoformat(data["date"])
        return Transaction(
            date=date_obj, # __init__ will handle this date object
            description=data["description"],
            type=data["type"],
            category=data["category"],
            amount=float(data["amount"])
        )
