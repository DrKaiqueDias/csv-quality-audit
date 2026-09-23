import json
import tempfile
import unittest
from pathlib import Path
from audit import audit


class AuditTests(unittest.TestCase):
    def run_audit(self, text, **kwargs):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "data.csv"
            path.write_text(text, encoding="utf-8")
            return audit(path, **kwargs)

    def test_good_rows(self):
        report = self.run_audit("id,amount\na,10\nb,20\n", required=["id"], numeric=["amount"])
        self.assertTrue(report["passed"])
        self.assertEqual(report["rows"], 2)

    def test_missing_numeric_and_shape(self):
        report = self.run_audit("id,amount\n,2\nb,nan\nc,3,extra\n",
                                required=["id"], numeric=["amount"])
        self.assertEqual(report["failed_rows"], 3)
        self.assertEqual(report["malformed_rows"], 1)
        self.assertEqual(report["missing_by_column"]["id"], 1)
        self.assertEqual(report["invalid_numeric_by_column"]["amount"], 1)

    def test_one_row_not_counted_twice(self):
        report = self.run_audit("id,amount\n,bad\n", required=["id"], numeric=["amount"])
        self.assertEqual(report["failed_rows"], 1)

    def test_optional_blanks(self):
        report = self.run_audit("id,amount\na, \n", numeric=["amount"])
        self.assertTrue(report["passed"])
        self.assertEqual(report["missing_by_column"]["amount"], 1)

    def test_quoted_fields_and_blank_lines(self):
        report = self.run_audit('id,note\na,"line one\nline two"\n\nb,"x,y"\n')
        self.assertEqual(report["rows"], 2)
        self.assertTrue(report["passed"])

    def test_schema_errors(self):
        for text, options in (("", {}), ("id,id\na,b\n", {}),
                              ("id\n", {}), ("id\na\n", {"required": ["missing"]})):
            with self.assertRaises(ValueError):
                self.run_audit(text, **options)

    def test_report_excludes_values(self):
        report = self.run_audit("id,amount\nPRIVATE_EXAMPLE,bad\n", numeric=["amount"])
        self.assertNotIn("PRIVATE_EXAMPLE", json.dumps(report))
        self.assertNotIn("bad", json.dumps(report))

    def test_non_finite_numbers(self):
        for value in ("NaN", "Infinity", "-inf", "not-a-number"):
            report = self.run_audit(f"id,amount\na,{value}\n", numeric=["amount"])
            self.assertEqual(report["invalid_numeric_by_column"]["amount"], 1)


if __name__ == "__main__":
    unittest.main()
