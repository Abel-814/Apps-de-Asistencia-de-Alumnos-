# Personal Finance CLI App

A simple command-line application to help you manage your personal finances efficiently and securely. Track income and expenses, create budgets, and analyze your spending patterns.

## Features

*   **Transaction Management:** Add, view, and categorize income and expense transactions.
*   **Data Persistence:** Transactions are saved locally in a CSV file (`data/transactions.csv`).
*   **Budgeting:** Define monthly (or custom period) budgets for different spending categories and track your progress.
*   **Reporting:**
    *   Generate summaries of income vs. expenses for specific periods.
    *   View spending breakdowns by category.
*   **Command-Line Interface:** Easy-to-use CLI for all operations.

## Project Structure

```
personal_finance_app/
├── data/
│   └── transactions.csv  # Stores your financial data
├── src/
│   ├── __init__.py
│   ├── app.py            # Main CLI application logic
│   ├── budget.py         # Budget class and logic
│   ├── ledger.py         # Ledger class (manages transactions)
│   └── transaction.py    # Transaction class
├── tests/
│   ├── __init__.py
│   ├── test_budget.py
│   ├── test_ledger.py
│   └── test_transaction.py
└── README.md
```

## Prerequisites

*   Python 3.7+

## Setup and Installation

1.  **Clone the repository (if applicable) or download the files.**
2.  **Navigate to the project's root directory (`personal_finance_app`).**
3.  **(Recommended) Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

## Running the Application

From the root directory of the project (`personal_finance_app`):

```bash
python -m src.app
```
This will start the CLI application. Follow the on-screen prompts to manage your finances.

## Usage

The application will present a main menu with the following options:

1.  **Add Transaction:** Record a new income or expense. You'll be prompted for date, description, type (income/expense), category, and amount.
2.  **View Transactions:**
    *   View all transactions.
    *   Filter transactions by date range, type, or category.
3.  **Manage Budget:**
    *   Set/Update the budget period (start and end dates).
    *   Set spending limits for specific categories within the budget period.
    *   View current category limits.
    *   See a report of your spending compared to your budget.
4.  **View Reports:**
    *   Generate an "Income vs. Expense" summary for a chosen period.
    *   Generate a "Spending by Category" report for a chosen period.
5.  **Save and Exit:** Saves all current data to `data/transactions.csv` and closes the application. Data is also loaded automatically when the application starts.

## Running Tests

To ensure the application's core logic is working correctly, you can run the automated unit tests. From the root directory of the project (`personal_finance_app`):

```bash
python -m unittest discover tests
```
All tests should pass.

---

*This is a sample application. For actual financial data, ensure you manage the `data/transactions.csv` file securely.*
