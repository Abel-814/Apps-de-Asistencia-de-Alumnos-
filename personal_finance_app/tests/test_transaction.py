import unittest
from datetime import date
from personal_finance_app.src.transaction import Transaction # Adjust import if necessary

class TestTransaction(unittest.TestCase):
    def test_transaction_creation_and_attributes(self):
        # Test with valid date object
        d = date(2023, 10, 26)
        t = Transaction(d, "Salary", "income", "Salary", 3000.00)
        self.assertEqual(t.date, d)
        self.assertEqual(t.description, "Salary")
        self.assertEqual(t.type, "income")
        self.assertEqual(t.category, "Salary")
        self.assertEqual(t.amount, 3000.00)

        # Test with valid date string
        t_str_date = Transaction("2023-11-15", "Groceries", "expense", "Food", 50.0)
        self.assertEqual(t_str_date.date, date(2023, 11, 15))

    def test_transaction_to_dict(self):
        d = date(2023, 10, 26)
        t = Transaction(d, "Coffee", "expense", "Food", 3.50)
        expected_dict = {
            "date": "2023-10-26",
            "description": "Coffee",
            "type": "expense",
            "category": "Food",
            "amount": 3.50,
        }
        self.assertEqual(t.to_dict(), expected_dict)

    def test_transaction_from_dict(self):
        data_dict = {
            "date": "2023-10-27",
            "description": "Lunch",
            "type": "expense",
            "category": "Food",
            "amount": 12.75,
        }
        t = Transaction.from_dict(data_dict)
        self.assertEqual(t.date, date(2023, 10, 27))
        self.assertEqual(t.description, "Lunch")
        self.assertEqual(t.amount, 12.75)

    def test_transaction_invalid_date_string(self):
        with self.assertRaises(ValueError): # Assuming Transaction converts to date obj on init
            Transaction("invalid-date", "Test", "income", "Test", 100.0)

    def test_transaction_invalid_amount_type(self):
        # Assuming amount is converted to float or validation exists
        # The Transaction class's amount is type-hinted as float.
        # If a string is passed that cannot be converted by float(),
        # it would raise a TypeError when Transaction.from_dict calls float(data["amount"]).
        # However, if directly passing to __init__, Python's float conversion might raise TypeError or ValueError
        # For direct __init__, it's a TypeError if an operation is attempted on incompatible types.
        # Let's assume direct instantiation for this test case, and it's handled by Python's typing or initial conversion logic.
        # If Transaction.__init__ immediately tries float("not-a-float"), it's a ValueError.
        # If it's assigned and then used in a math operation, it could be TypeError.
        # Given Transaction(date, desc, type, cat, amount: float), if "not-a-float" is passed,
        # and the __init__ doesn't explicitly try/except float(), this test might depend on Python's behavior or a static type checker.
        # For robustness, let's assume the constructor or from_dict method ensures amount becomes a float.
        # Transaction.from_dict explicitly calls float(data["amount"]). So this is a ValueError.
        # If Transaction.__init__ also calls float() on amount if it's not already float, then ValueError.
        # If not, and we rely on type hints, then passing a string to a float-hinted param is more about static analysis.
        # Let's stick to testing from_dict behavior for this, as it's more explicit.
        data_dict_invalid_amount = {
            "date": "2023-10-27", "description": "Test", "type": "income", "category": "Test", "amount": "not-a-float"
        }
        with self.assertRaises(ValueError):
            Transaction.from_dict(data_dict_invalid_amount)

        # Test direct __init__ with a non-float amount (if __init__ also tries to convert)
        # This depends on the exact implementation of __init__. If it expects float and gets string,
        # it might be a TypeError at usage, or ValueError if it tries to convert.
        # Current Transaction.__init__ does not explicitly convert amount, it relies on the caller passing float.
        # So, a direct pass of string "not-a-float" would not raise error at __init__, but later if used as float.
        # However, the problem description implies testing invalid type.
        # The prompt's original test was: Transaction(date.today(), "Test", "income", "Test", "not-a-float")
        # This will not immediately raise error in current Transaction class if it's just assignment.
        # For this test to be meaningful for __init__, __init__ would need to enforce float conversion.
        # Let's assume the intention is that amount should always be a valid number.
        # If we call `Transaction(date.today(), "Test", "income", "Test", "not-a-float")`
        # it will store "not-a-float" as self.amount. This test would fail.
        # The class should probably enforce this. For now, I'll keep the from_dict test which is clear.
        # To make the original test pass, Transaction.__init__ should be: self.amount = float(amount)
        # I will assume this enforcement is intended for robustness.
        # If Transaction.__init__ is self.amount = float(amount_input), then this is ValueError.
        # The current Transaction class is `self.amount = amount`.
        # This means `Transaction(date.today(), "Test", "income", "Test", "not-a-float")` will not raise error on init.
        # The test `with self.assertRaises(TypeError)` for this direct call implies that operations would fail.
        # This is not ideal. The class should validate its inputs.
        # Given the prompt, I will write the test as if the class *should* raise an error.
        # A simple `self.amount = float(amount)` in `__init__` would make this a ValueError.
        # Let's assume this strictness for the test.
        with self.assertRaises(ValueError): # Changed from TypeError to ValueError assuming float() conversion
             Transaction(date_input=date.today(), description="Test", type="income", category="Test", amount="not-a-float")


if __name__ == "__main__":
    unittest.main()
