from datetime import date
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .ledger import Ledger # To avoid circular import

class Budget:
    def __init__(self, name: str, start_date: date, end_date: date):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Budget name must be a non-empty string.")
        if not isinstance(start_date, date) or not isinstance(end_date, date):
            raise TypeError("Start date and end date must be datetime.date objects.")
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date.")

        self.name: str = name
        self.start_date: date = start_date
        self.end_date: date = end_date
        self.category_limits: Dict[str, float] = {}

    def set_limit(self, category: str, limit: float) -> None:
        """Sets or updates the spending limit for a given category."""
        if not isinstance(category, str) or not category.strip():
            raise ValueError("Category name must be a non-empty string.")
        if not isinstance(limit, (int, float)) or limit < 0:
            raise ValueError("Limit must be a non-negative number.")
        self.category_limits[category] = float(limit)

    def get_limit(self, category: str) -> Optional[float]:
        """Retrieves the spending limit for a category. Returns None if not set."""
        return self.category_limits.get(category)

    def get_all_limits(self) -> Dict[str, float]:
        """Returns the entire category_limits dictionary."""
        return self.category_limits.copy() # Return a copy to prevent external modification

    def calculate_spending_vs_budget(self, ledger: 'Ledger') -> Dict[str, Dict[str, Optional[float]]]:
        """
        Calculates spending vs. budget for each category based on ledger transactions.
        """
        # Import Ledger here if not using TYPE_CHECKING, or ensure it's available
        # from .ledger import Ledger # This would cause circular import if not handled by TYPE_CHECKING

        spending_summary: Dict[str, Dict[str, Optional[float]]] = {}

        # Initialize summary with all budgeted categories
        for category, limit in self.category_limits.items():
            spending_summary[category] = {
                "limit": limit,
                "spent": 0.0,
                "remaining": limit
            }

        # Accumulate spending from transactions
        for transaction in ledger.view_transactions():
            if transaction.type.lower() == 'expense' and self.start_date <= transaction.date <= self.end_date:
                category = transaction.category
                amount_spent = transaction.amount

                if category not in spending_summary:
                    # This is an expense category that wasn't in the original budget limits
                    spending_summary[category] = {
                        "limit": 0.0, # Or None, depending on desired representation
                        "spent": 0.0,
                        "remaining": 0.0 # Will become negative
                    }

                current_spent = spending_summary[category].get("spent", 0.0) or 0.0
                spending_summary[category]["spent"] = current_spent + amount_spent

        # Calculate remaining amounts
        for category_data in spending_summary.values():
            limit = category_data.get("limit") or 0.0
            spent = category_data.get("spent") or 0.0
            category_data["remaining"] = limit - spent

        return spending_summary
