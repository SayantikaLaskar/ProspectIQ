"""Shared domain constants and finance math for Prospect IQ.

Kept in one place so the data generator, the affordability engine and the
product-matching logic all agree on the same loan terms.
"""

# Retail loan products offered by the bank, with indicative terms.
# `max_foir` = the share of net monthly income the bank will let the *total*
# obligation (existing EMIs + the new EMI) consume for this product.
PRODUCTS = {
    "PERSONAL_LOAN": {
        "code": "PERSONAL_LOAN",
        "label": "Personal Loan",
        "annual_rate": 0.14,
        "tenure_months": 48,
        "min_amount": 50_000,
        "max_amount": 2_000_000,
        "max_foir": 0.50,
    },
    "HOME_LOAN": {
        "code": "HOME_LOAN",
        "label": "Home Loan",
        "annual_rate": 0.085,
        "tenure_months": 240,
        "min_amount": 1_500_000,
        "max_amount": 30_000_000,
        "max_foir": 0.55,
    },
    "AUTO_LOAN": {
        "code": "AUTO_LOAN",
        "label": "Auto Loan",
        "annual_rate": 0.10,
        "tenure_months": 84,
        "min_amount": 300_000,
        "max_amount": 5_000_000,
        "max_foir": 0.50,
    },
    "MORTGAGE_LOAN": {
        "code": "MORTGAGE_LOAN",
        "label": "Mortgage / Loan Against Property",
        "annual_rate": 0.105,
        "tenure_months": 180,
        "min_amount": 1_000_000,
        "max_amount": 20_000_000,
        "max_foir": 0.50,
    },
}

PRODUCT_ORDER = ["PERSONAL_LOAN", "HOME_LOAN", "AUTO_LOAN", "MORTGAGE_LOAN"]


def emi(principal: float, annual_rate: float, months: int) -> float:
    """Equated monthly instalment for a reducing-balance loan."""
    r = annual_rate / 12.0
    if months <= 0:
        return principal
    if r <= 0:
        return principal / months
    factor = (1 + r) ** months
    return principal * r * factor / (factor - 1)


def max_principal_for_emi(monthly_budget: float, annual_rate: float, months: int) -> float:
    """Largest principal whose EMI fits within `monthly_budget`."""
    r = annual_rate / 12.0
    if monthly_budget <= 0:
        return 0.0
    if r <= 0:
        return monthly_budget * months
    factor = (1 + r) ** months
    return monthly_budget * (factor - 1) / (r * factor)
