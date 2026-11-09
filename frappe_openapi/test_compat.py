from unittest import TestCase
from unittest.mock import Mock, patch

from frappe_openapi import compat


class TestMethodOverrides(TestCase):
	def test_native_resolver_is_used_when_available(self):
		frappe = Mock(override_whitelisted_method=Mock(return_value="app.override"))
		with patch.object(compat, "frappe", frappe):
			self.assertEqual(compat.override_whitelisted_method("app.method"), "app.override")
		frappe.override_whitelisted_method.assert_called_once_with("app.method")
		frappe.get_hooks.assert_not_called()

	def test_legacy_frappe_preserves_methods_without_overrides(self):
		frappe = Mock(spec=["get_hooks"])
		frappe.get_hooks.return_value = {}
		with patch.object(compat, "frappe", frappe):
			self.assertEqual(compat.override_whitelisted_method("app.method"), "app.method")

	def test_legacy_frappe_uses_last_override(self):
		frappe = Mock(spec=["get_hooks"])
		frappe.get_hooks.return_value = {"app.method": ["first.override", "last.override"]}
		with patch.object(compat, "frappe", frappe):
			self.assertEqual(compat.override_whitelisted_method("app.method"), "last.override")
		frappe.get_hooks.assert_called_once_with("override_whitelisted_methods", {})
