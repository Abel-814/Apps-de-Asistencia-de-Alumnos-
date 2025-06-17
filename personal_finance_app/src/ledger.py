from typing import List, Optional, Dict, Any
import datetime
import csv
import os
from .transaction import Transaction # Assuming Transaction class is in transaction.py

class Ledger:
    def __init__(self, data_file_path: Optional[str] = None):
        # Ensure datetime.date is available, prefer specific import if not using datetime.datetime
        # from datetime import date # This should be at the top of the file.
        self.transactions: List[Transaction] = []
        self.data_file_path: Optional[str] = data_file_path
        if self.data_file_path and os.path.exists(self.data_file_path):
            self.load_from_csv()

    def add_transaction(self, transaction: Transaction) -> None:
        """Adds a transaction to the ledger."""
        self.transactions.append(transaction)

    def view_transactions(self) -> List[Transaction]:
        """Returns all transactions in the ledger."""
        return self.transactions

    def get_transactions_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> List[Transaction]:
        """Retrieves transactions within a specific date range."""
        # Placeholder implementation
        return [
            t for t in self.transactions
            if start_date <= t.date <= end_date
        ]

    def get_transactions_by_type(self, transaction_type: str) -> List[Transaction]:
        """Retrieves transactions of a specific type (e.g., 'income', 'expense')."""
        # Placeholder implementation
        return [
            t for t in self.transactions
            if t.type.lower() == transaction_type.lower()
        ]

    def get_transactions_by_category(self, category: str) -> List[Transaction]:
        """Retrieves transactions belonging to a specific category."""
        # Placeholder implementation
        return [
            t for t in self.transactions
            if t.category.lower() == category.lower()
        ]

    def update_transaction(self, transaction_id: int, updated_details: Dict[str, Any]) -> bool:
        """Updates an existing transaction identified by its ID (index for now)."""
        # Placeholder: Using index as transaction_id for now.
        # This will need a more robust ID system in a real application.
        if 0 <= transaction_id < len(self.transactions):
            transaction_to_update = self.transactions[transaction_id]
            for key, value in updated_details.items():
                if hasattr(transaction_to_update, key):
                    if key == 'date' and isinstance(value, str):
                        setattr(transaction_to_update, key, datetime.date.fromisoformat(value))
                    elif key == 'amount' and isinstance(value, (int, str)):
                        setattr(transaction_to_update, key, float(value))
                    else:
                        setattr(transaction_to_update, key, value)
            return True
        return False # Transaction not found

    def delete_transaction(self, transaction_id: int) -> bool:
        """Deletes a transaction identified by its ID (index for now)."""
        # Placeholder: Using index as transaction_id for now.
        if 0 <= transaction_id < len(self.transactions):
            del self.transactions[transaction_id]
            return True
        return False # Transaction not found

    def save_to_csv(self, file_path: Optional[str] = None) -> None:
        """Saves the ledger transactions to a CSV file."""
        current_file_path = file_path if file_path is not None else self.data_file_path
        if not current_file_path:
            print("Error: No file path specified for saving CSV.")
            return

        # Ensure the directory exists
        dir_name = os.path.dirname(current_file_path)
        if dir_name: # Check if dirname is not empty (e.g. for relative paths)
            os.makedirs(dir_name, exist_ok=True)

        try:
            with open(current_file_path, 'w', newline='') as csvfile:
                if not self.transactions:
                    # If there are no transactions, an empty file will be created.
                    # Or, if you prefer to not write headers for an empty transaction list:
                    # csvfile.write('') # Ensure the file is empty if no transactions
                    return

                # Use the first transaction to determine headers
                headers = self.transactions[0].to_dict().keys()
                writer = csv.DictWriter(csvfile, fieldnames=headers)

                writer.writeheader()
                for transaction in self.transactions:
                    writer.writerow(transaction.to_dict())
        except IOError as e:
            print(f"Error saving transactions to CSV {current_file_path}: {e}")

    def load_from_csv(self, file_path: Optional[str] = None) -> None:
        """Loads transactions from a CSV file into the ledger."""
        current_file_path = file_path if file_path is not None else self.data_file_path
        if not current_file_path:
            print("Error: No file path specified for loading CSV.")
            return

        if not os.path.exists(current_file_path):
            print(f"Info: CSV file not found at {current_file_path}. Starting with an empty ledger.")
            return

        try:
            with open(current_file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                self.transactions = [] # Clear existing transactions before loading
                for row in reader:
                    try:
                        # Ensure amount is float, from_dict should handle date conversion
                        row['amount'] = float(row['amount'])
                        transaction = Transaction.from_dict(row)
                        self.add_transaction(transaction)
                    except ValueError as ve:
                        print(f"Error processing row: {row}. Invalid data: {ve}")
                    except KeyError as ke:
                        print(f"Error processing row: {row}. Missing key: {ke}")
        except FileNotFoundError:
            print(f"Info: CSV file not found at {current_file_path}. No transactions loaded.")
        except IOError as e:
            print(f"Error loading transactions from CSV {current_file_path}: {e}")

    def generate_income_vs_expense_report(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, float]:
        """
        Generates a report of total income vs. total expenses for a given period.
        """
        if not isinstance(start_date, datetime.date) or not isinstance(end_date, datetime.date): # type: ignore
            # This check is technically redundant if type hints are enforced by a static checker
            # but good for runtime if objects of incorrect type are passed.
            # isinstance(start_date, date) would require "from datetime import date"
            raise TypeError("Start date and end date must be datetime.date objects.")
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date.")

        relevant_transactions = self.get_transactions_by_date_range(start_date, end_date)

        total_income = 0.0
        total_expenses = 0.0

        for transaction in relevant_transactions:
            if transaction.type.lower() == 'income':
                total_income += transaction.amount
            elif transaction.type.lower() == 'expense':
                total_expenses += transaction.amount

        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_flow': total_income - total_expenses
        }

    def generate_spending_by_category_report(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, float]:
        """
        Generates a report of spending by category for a given period.
        """
        if not isinstance(start_date, datetime.date) or not isinstance(end_date, datetime.date): # type: ignore
            raise TypeError("Start date and end date must be datetime.date objects.")
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date.")

        relevant_transactions = self.get_transactions_by_date_range(start_date, end_date)
        spending_by_category: Dict[str, float] = {}

        for transaction in relevant_transactions:
            if transaction.type.lower() == 'expense':
                category = transaction.category
                spending_by_category[category] = spending_by_category.get(category, 0.0) + transaction.amount

        return spending_by_category
