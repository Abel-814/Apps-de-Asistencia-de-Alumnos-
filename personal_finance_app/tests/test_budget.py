import unittest
from datetime import date
from personal_finance_app.src.transaction import Transaction
from personal_finance_app.src.ledger import Ledger
from personal_finance_app.src.budget import Budget # Adjust import

class TestBudget(unittest.TestCase):
    def setUp(self):
        # For budget tests, ledger can often be an in-memory one (no file path)
        # as we are testing budget logic, not ledger persistence.
        self.ledger = Ledger()
        self.budget_start_date = date(2023, 1, 1)
        self.budget_end_date = date(2023, 1, 31)
        self.budget = Budget("Monthly Jan Test", self.budget_start_date, self.budget_end_date)

    def test_budget_creation_and_attributes(self):
        self.assertEqual(self.budget.name, "Monthly Jan Test")
        self.assertEqual(self.budget.start_date, self.budget_start_date)
        self.assertEqual(self.budget.end_date, self.budget_end_date)
        self.assertEqual(self.budget.category_limits, {}) # Should be empty initially

    def test_set_and_get_limit(self):
        self.budget.set_limit("Food", 200.0)
        self.assertEqual(self.budget.get_limit("Food"), 200.0)
        self.assertIsNone(self.budget.get_limit("Transport"), "Limit for unset category should be None.")

        # Test updating a limit
        self.budget.set_limit("Food", 250.0)
        self.assertEqual(self.budget.get_limit("Food"), 250.0)

        # Test setting limit for another category
        self.budget.set_limit("Utilities", 75.0)
        self.assertEqual(self.budget.get_limit("Utilities"), 75.0)

    def test_get_all_limits(self):
        self.assertEqual(self.budget.get_all_limits(), {}, "Initially, all limits should be empty.")
        self.budget.set_limit("Food", 200.0)
        self.budget.set_limit("Transport", 50.0)
        expected_limits = {"Food": 200.0, "Transport": 50.0}
        self.assertEqual(self.budget.get_all_limits(), expected_limits)

    def test_calculate_spending_vs_budget_scenarios(self):
        # 1. Setup budget limits
        self.budget.set_limit("Food", 100.0)
        self.budget.set_limit("Transport", 50.0)
        self.budget.set_limit("Education", 70.0) # Limit set, but no spending in this category

        # 2. Add transactions to ledger
        # Within budget period and relevant categories
        self.ledger.add_transaction(Transaction(date(2023,1,5),"Groceries","expense","Food",40.0))
        self.ledger.add_transaction(Transaction(date(2023,1,10),"Restaurant","expense","Food",70.0)) # Food total: 110 (Over limit)
        self.ledger.add_transaction(Transaction(date(2023,1,15),"Bus Fare","expense","Transport",30.0)) # Transport total: 30 (Under limit)

        # Transaction in a category without a pre-set limit
        self.ledger.add_transaction(Transaction(date(2023,1,20),"Movie Tickets","expense","Entertainment",25.0))

        # Transaction outside budget period (should be ignored)
        self.ledger.add_transaction(Transaction(date(2023,2,1),"Early Feb Food","expense","Food",10.0))

        # Income transaction (should be ignored by spending calculation)
        self.ledger.add_transaction(Transaction(date(2023,1,20),"Salary Deposit","income","Salary",1000.0))

        # 3. Calculate spending
        report = self.budget.calculate_spending_vs_budget(self.ledger)

        # 4. Assertions for each category
        # Category: Food (Over budget)
        self.assertIn("Food", report)
        self.assertEqual(report["Food"]["limit"], 100.0)
        self.assertEqual(report["Food"]["spent"], 110.0) # 40 + 70
        self.assertEqual(report["Food"]["remaining"], -10.0)

        # Category: Transport (Within budget)
        self.assertIn("Transport", report)
        self.assertEqual(report["Transport"]["limit"], 50.0)
        self.assertEqual(report["Transport"]["spent"], 30.0)
        self.assertEqual(report["Transport"]["remaining"], 20.0)

        # Category: Entertainment (Spending, no pre-set limit)
        self.assertIn("Entertainment", report)
        self.assertEqual(report["Entertainment"]["limit"], 0.0, "Default limit for new categories should be 0.")
        self.assertEqual(report["Entertainment"]["spent"], 25.0)
        self.assertEqual(report["Entertainment"]["remaining"], -25.0)

        # Category: Education (Limit set, no spending)
        self.assertIn("Education", report)
        self.assertEqual(report["Education"]["limit"], 70.0)
        self.assertEqual(report["Education"]["spent"], 0.0)
        self.assertEqual(report["Education"]["remaining"], 70.0)

        # Category: Salary (Income, should not be in spending report)
        self.assertNotIn("Salary", report, "Income categories should not be in spending vs budget report.")


    def test_budget_invalid_date_creation(self):
        with self.assertRaises(ValueError): # start_date after end_date
            Budget("Invalid Dates", date(2023, 2, 1), date(2023, 1, 1))

    def test_set_limit_invalid_inputs(self):
        with self.assertRaises(ValueError): # Negative limit
            self.budget.set_limit("Food", -50.0)
        with self.assertRaises(ValueError): # Empty category string
            self.budget.set_limit("", 100.0)
        # Non-numeric limit should also raise error, e.g. TypeError if not handled by float conversion
        # The set_limit type hint is float, but if string is passed:
        # self.category_limits[category] = float(limit) will handle conversion or raise ValueError
        with self.assertRaises(ValueError):
            self.budget.set_limit("Travel", "not-a-number")


if __name__ == "__main__":
    unittest.main()
