from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from frappe_openapi.registry import classify_method_file, get_doctype_app_map


class TestDocTypeAppMap(TestCase):
	def test_app_ownership_uses_module_and_keeps_unmapped_doctypes(self):
		modules = [SimpleNamespace(name="Accounts", app_name="erpnext")]
		doctypes = [
			SimpleNamespace(name="Sales Invoice", module="Accounts"),
			SimpleNamespace(name="Custom Record", module="Missing Module"),
		]
		with patch("frappe_openapi.registry.frappe.get_all", side_effect=[modules, doctypes]):
			result = get_doctype_app_map.__wrapped__()
		self.assertEqual(result, {"Sales Invoice": "erpnext", "Custom Record": None})


class TestMethodClassification(TestCase):
	def setUp(self):
		self.app_path = Path("/tmp/frappe_openapi_test/erpnext")
		self.classification_map = {
			"module_by_folder": {"accounts": "Accounts"},
			"doctype_by_folder": {("accounts", "sales_invoice"): "Sales Invoice"},
		}

	def classify(self, relative_path: str) -> dict:
		return classify_method_file(
			"erpnext",
			self.app_path,
			self.app_path / relative_path,
			self.classification_map,
		)

	def test_doctype_controller_file_is_classified_as_doctype(self):
		classification = self.classify("accounts/doctype/sales_invoice/sales_invoice.py")

		self.assertEqual(classification["kind"], "doctype")
		self.assertEqual(classification["module"], "Accounts")
		self.assertEqual(classification["doctype"], "Sales Invoice")

	def test_doctype_package_file_is_classified_as_doctype(self):
		classification = self.classify("accounts/doctype/sales_invoice/sales_invoice_dashboard.py")

		self.assertEqual(classification["kind"], "doctype")
		self.assertEqual(classification["module"], "Accounts")
		self.assertEqual(classification["doctype"], "Sales Invoice")

	def test_module_file_is_classified_as_module(self):
		classification = self.classify("accounts/report/general_ledger/general_ledger.py")

		self.assertEqual(classification["kind"], "module")
		self.assertEqual(classification["module"], "Accounts")
		self.assertIsNone(classification["doctype"])
