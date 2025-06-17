import sys
import os
from datetime import datetime, date, timedelta

# Adjust import path for sibling modules (transaction, ledger, budget)
# This is often needed when running a script inside a package directly.
# However, for `python -m personal_finance_app.src.app`, direct imports should work.
# If running `python app.py` from within src, this path adjustment helps.
# For robustness, especially if considering different execution methods:
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(current_dir) # This goes up to personal_finance_app
# sys.path.insert(0, project_root) # Add project root to path

try:
    from .transaction import Transaction
    from .ledger import Ledger
    from .budget import Budget
except ImportError:
    # Fallback for running app.py directly from src, might be needed in some environments
    # or if the module structure isn't perfectly picked up.
    from transaction import Transaction
    from ledger import Ledger
    from budget import Budget


# --- Configuration ---
# DATA_FILE path assumes app.py is in 'src' and 'data' is a sibling to 'src'
# i.e., project_root/src/app.py and project_root/data/transactions.csv
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "transactions.csv")


# --- Helper Functions ---

def prompt_for_date(prompt_message: str) -> date | None:
    """Prompts the user for a date in YYYY-MM-DD format.
    Loops until a valid date is entered or the input is empty (to cancel).
    """
    while True:
        date_str = input(f"{prompt_message} (YYYY-MM-DD) or leave empty to cancel: ").strip()
        if not date_str:
            return None
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

def prompt_for_float(prompt_message: str) -> float | None:
    """Prompts the user for a float.
    Loops until a valid float is entered or the input is empty (to cancel).
    """
    while True:
        amount_str = input(f"{prompt_message} or leave empty to cancel: ").strip()
        if not amount_str:
            return None
        try:
            return float(amount_str)
        except ValueError:
            print("Invalid amount. Please enter a valid number (e.g., 50.75).")

def prompt_for_string(prompt_message: str, required: bool = True) -> str | None:
    """Prompts the user for a string.
    If required is True, loops until a non-empty string is entered.
    If required is False, an empty input returns None.
    """
    while True:
        input_str = input(prompt_message + ": ").strip()
        if input_str:
            return input_str
        elif not required:
            return None
        else:
            print("This field is required.")

def display_transactions(transactions: list[Transaction]) -> None:
    """Displays a list of transactions or a 'no transactions' message."""
    if not transactions:
        print("No transactions found.")
        return
    print("\n--- Transactions ---")
    for tx in transactions:
        print(f"Date: {tx.date.isoformat()}, Type: {tx.type.capitalize()}, Category: {tx.category}, "
              f"Amount: ${tx.amount:.2f}, Description: {tx.description}")
    print("--------------------\n")

# --- UI Functions for Features ---

def add_transaction_ui(ledger: Ledger) -> None:
    """Handles the UI for adding a new transaction."""
    print("\n--- Add New Transaction ---")
    transaction_date = prompt_for_date("Enter transaction date")
    if not transaction_date:
        print("Transaction cancelled.")
        return

    description = prompt_for_string("Enter description", required=True)
    if not description: # Should not happen if required=True, but as safeguard
        print("Description is required. Transaction cancelled.")
        return

    while True:
        transaction_type = prompt_for_string("Enter type (income/expense)", required=True)
        if transaction_type and transaction_type.lower() in ["income", "expense"]:
            transaction_type = transaction_type.lower()
            break
        else:
            print("Invalid type. Please enter 'income' or 'expense'.")

    category = prompt_for_string("Enter category (e.g., Groceries, Salary)", required=True)
    if not category:
        print("Category is required. Transaction cancelled.")
        return

    amount = prompt_for_float("Enter amount")
    if amount is None: # Check for None explicitly, as 0 is a valid amount
        print("Amount is required. Transaction cancelled.")
        return
    if amount < 0:
        print("Amount cannot be negative. Use 'expense' type for outgoing money. Transaction cancelled.")
        return

    try:
        # The Transaction class __init__ expects a date object or an ISO string.
        # prompt_for_date returns a date object, so it's fine.
        transaction = Transaction(date_input=transaction_date, description=description,
                                  type=transaction_type, category=category, amount=amount)
        ledger.add_transaction(transaction)
        print("Transaction added successfully!")
    except ValueError as e:
        print(f"Error creating transaction: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def view_transactions_ui(ledger: Ledger) -> None:
    """Handles the UI for viewing transactions."""
    print("\n--- View Transactions ---")
    print("1. View All Transactions")
    print("2. Filter by Date Range")
    print("3. Filter by Type (Income/Expense)")
    print("4. Filter by Category")
    print("0. Back to Main Menu")

    choice = input("Enter your choice: ").strip()

    if choice == '1':
        display_transactions(ledger.view_transactions())
    elif choice == '2':
        start_date = prompt_for_date("Enter start date for range")
        if not start_date: return
        end_date = prompt_for_date("Enter end date for range")
        if not end_date: return
        if start_date > end_date:
            print("Start date cannot be after end date.")
            return
        display_transactions(ledger.get_transactions_by_date_range(start_date, end_date))
    elif choice == '3':
        while True:
            transaction_type = prompt_for_string("Enter type to filter (income/expense)", required=True)
            if transaction_type and transaction_type.lower() in ["income", "expense"]:
                display_transactions(ledger.get_transactions_by_type(transaction_type.lower()))
                break
            else:
                print("Invalid type. Please enter 'income' or 'expense'.")
    elif choice == '4':
        category = prompt_for_string("Enter category to filter", required=True)
        if category:
            display_transactions(ledger.get_transactions_by_category(category))
    elif choice == '0':
        return
    else:
        print("Invalid choice. Please try again.")


def manage_budget_ui(budget: Budget, ledger: Ledger) -> None:
    """Handles the UI for managing the budget."""
    print("\n--- Manage Budget ---")
    print(f"Current Budget: {budget.name} ({budget.start_date.isoformat()} to {budget.end_date.isoformat()})")
    print("1. Set/Update Budget Period")
    print("2. Set Category Spending Limit")
    print("3. View Category Limits")
    print("4. View Spending vs. Budget")
    print("0. Back to Main Menu")

    choice = input("Enter your choice: ").strip()

    if choice == '1':
        print("\n-- Set Budget Period --")
        new_name = prompt_for_string("Enter budget name (e.g., Monthly Expenses)", required=True)
        start_date = prompt_for_date("Enter new start date")
        end_date = prompt_for_date("Enter new end date")

        if new_name and start_date and end_date:
            if start_date > end_date:
                print("Start date cannot be after end date. Budget period not updated.")
                return
            budget.name = new_name
            budget.start_date = start_date
            budget.end_date = end_date
            print(f"Budget period updated to '{budget.name}' ({budget.start_date.isoformat()} to {budget.end_date.isoformat()}).")
        else:
            print("Missing information. Budget period not updated.")

    elif choice == '2':
        print("\n-- Set Category Limit --")
        category = prompt_for_string("Enter category name", required=True)
        limit = prompt_for_float("Enter spending limit for this category")
        if category and limit is not None:
            if limit < 0:
                print("Limit cannot be negative. Limit not set.")
                return
            try:
                budget.set_limit(category, limit)
                print(f"Limit for '{category}' set to ${limit:.2f}.")
            except ValueError as e:
                print(f"Error setting limit: {e}")
        else:
            print("Category or limit not provided. Limit not set.")

    elif choice == '3':
        print("\n-- Category Limits --")
        limits = budget.get_all_limits()
        if not limits:
            print("No category limits set for the current budget.")
        else:
            for category, limit in limits.items():
                print(f"Category: {category}, Limit: ${limit:.2f}")
        print("---------------------")

    elif choice == '4':
        print("\n-- Spending vs. Budget --")
        # Ensure the budget object itself is up-to-date if period was changed
        # The calculate_spending_vs_budget method uses the budget's current start/end dates
        report = budget.calculate_spending_vs_budget(ledger)
        if not report:
            print("No spending data available or no limits set to compare against.")
        else:
            print(f"Report for Budget: {budget.name} ({budget.start_date.isoformat()} to {budget.end_date.isoformat()})")
            for category, data in report.items():
                limit = data.get('limit', 0.0) or 0.0 # Ensure float for formatting
                spent = data.get('spent', 0.0) or 0.0 # Ensure float for formatting
                remaining = data.get('remaining', 0.0) or 0.0 # Ensure float

                print(f"Category: {category:<20} | Limit: ${limit:>10.2f} | Spent: ${spent:>10.2f} | Remaining: ${remaining:>10.2f}")
                if remaining < 0:
                    print(f"  Status: Overspent by ${abs(remaining):.2f}")
                elif spent > 0 and limit > 0 :
                     print(f"  Status: {(spent/limit)*100:.2f}% of budget used.")
                elif spent == 0 and limit > 0:
                    print(f"  Status: No spending in this category.")
                elif limit == 0 and spent > 0:
                    print(f"  Status: Spent ${spent:.2f} (No limit set).")

    elif choice == '0':
        return
    else:
        print("Invalid choice. Please try again.")


def view_reports_ui(ledger: Ledger) -> None:
    """Handles the UI for viewing financial reports."""
    print("\n--- View Reports ---")
    print("1. Income vs. Expense Report")
    print("2. Spending by Category Report")
    print("0. Back to Main Menu")

    choice = input("Enter your choice: ").strip()

    if choice == '1':
        print("\n-- Income vs. Expense Report --")
        start_date = prompt_for_date("Enter start date for report period")
        if not start_date: return
        end_date = prompt_for_date("Enter end date for report period")
        if not end_date: return

        if start_date > end_date:
            print("Start date cannot be after end date.")
            return

        try:
            report = ledger.generate_income_vs_expense_report(start_date, end_date)
            print(f"\nReport for period: {start_date.isoformat()} to {end_date.isoformat()}")
            print(f"Total Income:    ${report['total_income']:.2f}")
            print(f"Total Expenses:  ${report['total_expenses']:.2f}")
            print(f"Net Flow:        ${report['net_flow']:.2f}")
            print("---------------------------------")
        except Exception as e:
            print(f"Could not generate report: {e}")

    elif choice == '2':
        print("\n-- Spending by Category Report --")
        start_date = prompt_for_date("Enter start date for report period")
        if not start_date: return
        end_date = prompt_for_date("Enter end date for report period")
        if not end_date: return

        if start_date > end_date:
            print("Start date cannot be after end date.")
            return

        try:
            report = ledger.generate_spending_by_category_report(start_date, end_date)
            print(f"\nSpending by Category ({start_date.isoformat()} to {end_date.isoformat()}):")
            if not report:
                print("No spending in this period or categories.")
            else:
                for category, amount in report.items():
                    print(f"Category: {category:<20} | Spent: ${amount:>10.2f}")
            print("---------------------------------")
        except Exception as e:
            print(f"Could not generate report: {e}")

    elif choice == '0':
        return
    else:
        print("Invalid choice. Please try again.")


# --- Main Menu and Execution ---

def main_menu(ledger: Ledger, budget: Budget) -> None:
    """Displays the main menu and handles user navigation."""
    while True:
        print("\n--- Personal Finance App ---")
        print("1. Add Transaction")
        print("2. View Transactions")
        print("3. Manage Budget")
        print("4. View Reports")
        print("5. Save and Exit")
        print("----------------------------")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            add_transaction_ui(ledger)
        elif choice == '2':
            view_transactions_ui(ledger)
        elif choice == '3':
            manage_budget_ui(budget, ledger)
        elif choice == '4':
            view_reports_ui(ledger)
        elif choice == '5':
            print("Saving data...")
            try:
                ledger.save_to_csv() # Uses the path given at Ledger initialization
                print("Data saved successfully.")
            except Exception as e:
                print(f"Error saving data: {e}")
            print("Exiting application. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Ensure the data directory exists, if not, Ledger's save_to_csv will create it.
    # However, good practice to ensure DATA_FILE path is resolvable.
    # The DATA_FILE path construction already handles OS-specific separators.

    # Initialize Ledger. This will also load data if the CSV exists.
    ledger = Ledger(data_file_path=DATA_FILE)
    print(f"Data will be loaded from/saved to: {os.path.abspath(DATA_FILE)}")


    # Initialize a default current_budget for the current month
    today = date.today()
    start_of_month = today.replace(day=1)

    # Calculate end_of_month carefully
    if today.month == 12:
        # For December, end of month is Dec 31, or (Jan 1 of next year) - 1 day
        end_of_month = date(today.year, 12, 31)
        # More robust: (next year, month 1, day 1) - 1 day
        # end_of_month = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        # For other months, (current year, next month, day 1) - 1 day
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    current_budget_name = f"{today.strftime('%B %Y')} Budget"
    current_budget = Budget(name=current_budget_name, start_date=start_of_month, end_date=end_of_month)

    # Load any existing budget limits for this default budget? (Future enhancement)
    # For now, it starts fresh or would need manual setup via UI.

    main_menu(ledger, current_budget)
