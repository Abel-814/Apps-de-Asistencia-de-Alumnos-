import unittest
import os
import csv
from datetime import date, datetime # datetime might be used by Ledger or Transaction indirectly
from personal_finance_app.src.transaction import Transaction
from personal_finance_app.src.ledger import Ledger # Adjust import

# Use a specific test file path that's clearly for tests
TEST_CSV_FILE = os.path.join(os.path.dirname(__file__), "test_transactions_ledger.csv")

class TestLedger(unittest.TestCase):
    def setUp(self):
        """Set up a new ledger and clean any pre-existing test CSV file."""
        # Ensure a clean slate for each test by removing the test file if it exists
        if os.path.exists(TEST_CSV_FILE):
            os.remove(TEST_CSV_FILE)
        self.ledger = Ledger(data_file_path=TEST_CSV_FILE)

    def tearDown(self):
        """Clean up the test CSV file after each test."""
        if os.path.exists(TEST_CSV_FILE):
            os.remove(TEST_CSV_FILE)

    def test_add_and_view_transactions(self):
        self.assertEqual(len(self.ledger.view_transactions()), 0, "Ledger should be initially empty.")
        t1 = Transaction(date(2023, 1, 1), "Income 1", "income", "Salary", 100.0)
        self.ledger.add_transaction(t1)
        self.assertEqual(len(self.ledger.view_transactions()), 1, "Ledger should have 1 transaction after adding one.")
        self.assertIn(t1, self.ledger.view_transactions(), "Added transaction should be in the ledger.")
        self.assertEqual(self.ledger.view_transactions()[0].description, "Income 1")

    def test_save_and_load_csv(self):
        t1 = Transaction(date(2023, 1, 1), "Rent", "expense", "Housing", 500.0)
        t2 = Transaction(date(2023, 1, 5), "Groceries", "expense", "Food", 75.0)
        self.ledger.add_transaction(t1)
        self.ledger.add_transaction(t2)
        self.ledger.save_to_csv() # Saves to TEST_CSV_FILE

        # Verify file was created
        self.assertTrue(os.path.exists(TEST_CSV_FILE), "CSV file should be created by save_to_csv.")

        new_ledger = Ledger(data_file_path=TEST_CSV_FILE) # Loads on init
        loaded_transactions = new_ledger.view_transactions()
        self.assertEqual(len(loaded_transactions), 2, "Should load 2 transactions from CSV.")

        # Check data integrity (dates are tricky due to object comparison)
        self.assertEqual(loaded_transactions[0].description, "Rent")
        self.assertEqual(loaded_transactions[0].date, date(2023,1,1))
        self.assertEqual(loaded_transactions[0].amount, 500.0)

        self.assertEqual(loaded_transactions[1].description, "Groceries")
        self.assertEqual(loaded_transactions[1].date, date(2023,1,5))
        self.assertEqual(loaded_transactions[1].amount, 75.0)

    def test_load_from_non_existent_file(self):
        # setUp ensures file doesn't exist initially for self.ledger
        # For this test, create a ledger instance pointing to a different non-existent file
        # to be absolutely sure it's not affected by setUp/tearDown of TEST_CSV_FILE
        non_existent_path = os.path.join(os.path.dirname(__file__), "non_existent_temp_file.csv")
        if os.path.exists(non_existent_path): # Pre-caution
             os.remove(non_existent_path)

        temp_ledger = Ledger(data_file_path=non_existent_path)
        self.assertEqual(len(temp_ledger.view_transactions()), 0, "Ledger should be empty if CSV does not exist.")
        self.assertFalse(os.path.exists(non_existent_path), "load_from_csv should not create a file if it doesn't exist.")


    def test_load_from_empty_csv_with_header(self):
        # Create an empty CSV file with only headers (some CSV writers might do this)
        with open(TEST_CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["date", "description", "type", "category", "amount"]) # Expected headers

        empty_ledger = Ledger(data_file_path=TEST_CSV_FILE)
        self.assertEqual(len(empty_ledger.view_transactions()), 0, "Ledger should be empty if CSV only has headers.")

    def test_load_from_truly_empty_csv(self):
        # Create a truly empty CSV file (0 bytes)
        with open(TEST_CSV_FILE, 'w', newline='') as f:
            pass # Just create the file

        empty_ledger = Ledger(data_file_path=TEST_CSV_FILE)
        # Current implementation of load_from_csv might try to read headers.
        # An empty file will cause csv.DictReader to potentially raise an error or read nothing.
        # If it raises error, the transactions list remains empty. If it reads nothing, also empty.
        self.assertEqual(len(empty_ledger.view_transactions()), 0, "Ledger should be empty if CSV is completely empty.")


    def test_get_transactions_by_type(self):
        t1 = Transaction(date(2023, 1, 1), "Salary", "income", "Work", 2000.0)
        t2 = Transaction(date(2023, 1, 2), "Groceries", "expense", "Food", 50.0)
        t3 = Transaction(date(2023, 1, 3), "Bonus", "income", "Work", 500.0)
        self.ledger.add_transaction(t1)
        self.ledger.add_transaction(t2)
        self.ledger.add_transaction(t3)

        income_transactions = self.ledger.get_transactions_by_type("income")
        self.assertEqual(len(income_transactions), 2)
        # Check if correct transactions are returned (order might matter or not, depending on spec)
        self.assertTrue(all(t.type == "income" for t in income_transactions))

        expense_transactions = self.ledger.get_transactions_by_type("expense")
        self.assertEqual(len(expense_transactions), 1)
        self.assertEqual(expense_transactions[0].description, "Groceries")
        self.assertTrue(all(t.type == "expense" for t in expense_transactions))

        # Test with a type that has no transactions
        other_transactions = self.ledger.get_transactions_by_type("other")
        self.assertEqual(len(other_transactions), 0)


    def test_generate_income_vs_expense_report(self):
        self.ledger.add_transaction(Transaction(date(2023, 1, 1), "Inc1", "income", "S", 100.0))
        self.ledger.add_transaction(Transaction(date(2023, 1, 2), "Exp1", "expense", "F", 30.0))
        self.ledger.add_transaction(Transaction(date(2023, 1, 15), "Inc2", "income", "S", 200.0))
        self.ledger.add_transaction(Transaction(date(2023, 2, 1), "Exp2", "expense", "H", 70.0)) # Outside range

        report = self.ledger.generate_income_vs_expense_report(date(2023, 1, 1), date(2023, 1, 31))
        self.assertEqual(report['total_income'], 300.0)
        self.assertEqual(report['total_expenses'], 30.0)
        self.assertEqual(report['net_flow'], 270.0)

        # Test with a range that has no transactions
        empty_report = self.ledger.generate_income_vs_expense_report(date(2020,1,1), date(2020,1,31))
        self.assertEqual(empty_report['total_income'], 0.0)
        self.assertEqual(empty_report['total_expenses'], 0.0)
        self.assertEqual(empty_report['net_flow'], 0.0)


    def test_generate_spending_by_category_report(self):
        self.ledger.add_transaction(Transaction(date(2023,1,1), "Food1", "expense", "Food", 20.0))
        self.ledger.add_transaction(Transaction(date(2023,1,2), "Transport1", "expense", "Transport", 10.0))
        self.ledger.add_transaction(Transaction(date(2023,1,3), "Food2", "expense", "Food", 25.0))
        # Income transaction, should be ignored
        self.ledger.add_transaction(Transaction(date(2023,1,4), "Salary", "income", "Work", 1000.0))
        # Transaction outside date range
        self.ledger.add_transaction(Transaction(date(2023,2,1), "Food3", "expense", "Food", 30.0))

        report = self.ledger.generate_spending_by_category_report(date(2023,1,1), date(2023,1,31))
        self.assertEqual(report.get("Food"), 45.0) # 20 + 25
        self.assertEqual(report.get("Transport"), 10.0)
        self.assertIsNone(report.get("Utilities"), "Category 'Utilities' should not exist in report if no spending.")
        self.assertIsNone(report.get("Work"), "Income categories should not be in spending report.")

        # Test with a range that has no expense transactions
        empty_report = self.ledger.generate_spending_by_category_report(date(2020,1,1), date(2020,1,31))
        self.assertEqual(len(empty_report), 0)


if __name__ == "__main__":
    unittest.main()
