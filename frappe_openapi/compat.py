import frappe


def override_whitelisted_method(method: str) -> str:
	"""Resolve method overrides on Frappe versions with and without the helper."""
	resolver = getattr(frappe, "override_whitelisted_method", None)
	if resolver is not None:
		return resolver(method)

	overrides = frappe.get_hooks("override_whitelisted_methods", {}).get(method, [])
	return overrides[-1] if overrides else method
