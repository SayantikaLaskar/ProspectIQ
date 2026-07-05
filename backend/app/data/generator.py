"""Synthetic Indian retail-banking data generator.

Produces three things:
  * customers      -- what a bank already knows (declared income, bureau score,
                      tenure, products).  These are the "traditional metrics".
  * transactions   -- 12 months of realistic inflows/outflows per customer.
  * ground_truth   -- HELD-OUT labels (true income, true loan intent, whether
                      the prospect would actually convert).  Never shown to the
                      engines; used only to validate them (income MAE, intent
                      recall, and the >30% conversion proof).

The whole thesis of Prospect IQ is that the transaction stream reveals a
customer's *real* income, repayment capacity and buying intent far better than
the declared metrics do -- especially for the self-employed, whose declared
income is deliberately understated here (as it is in reality).
"""
from __future__ import annotations

import math
import random
from datetime import date
from typing import Dict, List, Optional, Tuple

import numpy as np
from faker import Faker

from app.constants import PRODUCTS, emi

# --------------------------------------------------------------------------- #
# Reference data
# --------------------------------------------------------------------------- #
CITY_TIERS = {
    1: ["Mumbai", "Delhi", "Bengaluru", "Chennai", "Hyderabad", "Pune", "Kolkata"],
    2: ["Jaipur", "Lucknow", "Indore", "Nagpur", "Coimbatore", "Kochi", "Bhopal", "Surat"],
    3: ["Guntur", "Salem", "Warangal", "Rourkela", "Bilaspur", "Nanded", "Karnal"],
}
EMPLOYERS = [
    "INFOSYS", "TCS", "WIPRO", "HDFC BANK", "RELIANCE RETAIL", "ACCENTURE",
    "COGNIZANT", "AMAZON IN", "FLIPKART", "TECH MAHINDRA", "ICICI LOMBARD",
    "LARSEN TOUBRO", "MARUTI SUZUKI", "SBI LIFE", "BHARTI AIRTEL", "CAPGEMINI",
]
BUSINESS_NAMES = [
    "SHREE TRADERS", "BALAJI KIRANA", "NEW TEXTILE HOUSE", "ANNAPURNA RESTAURANT",
    "CITY PHARMA", "AUTO SPARES CO", "APEX CONSULTANCY", "SMILE DENTAL CLINIC",
    "BRIGHT COACHING", "METRO WHOLESALE",
]
MUTUAL_FUNDS = ["HDFC FLEXICAP", "SBI BLUECHIP", "AXIS MIDCAP", "MIRAE LARGECAP",
                "PARAG PARIKH FLEXI", "ICICI PRU TECH"]
LENDERS = ["BAJAJ FINANCE", "HDFC LTD", "SBI", "TATA CAPITAL", "AXIS BANK"]
INSURERS = ["LIC", "HDFC LIFE", "ICICI PRU", "MAX LIFE"]
GROCERS = ["BIGBASKET", "DMART", "RELIANCE FRESH", "BLINKIT", "ZEPTO"]
FOOD = ["SWIGGY", "ZOMATO", "DOMINOS", "KFC INDIA"]
SHOPPING = ["AMAZON", "FLIPKART", "MYNTRA", "AJIO", "CROMA"]
FUEL = ["HP PETROL", "INDIAN OIL", "BHARAT PETRO", "SHELL"]
CAR_DEALERS = ["MARUTI ARENA", "HYUNDAI MOTORS", "TATA MOTORS SHOWROOM", "KIA AUTOMALL"]
HOSPITALS = ["APOLLO HOSPITAL", "FORTIS HEALTHCARE", "MAX HOSPITAL", "MANIPAL CLINIC"]
EDU = ["BYJUS", "ALLEN INSTITUTE", "UNIV FEE PORTAL", "AAKASH EDU"]

INTENT_PRODUCTS = ["HOME_LOAN", "AUTO_LOAN", "PERSONAL_LOAN", "MORTGAGE_LOAN"]


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _month_starts(n: int = 12) -> List[date]:
    """First-of-month dates for the last `n` months, oldest first."""
    today = date.today()
    starts: List[date] = []
    y, m = today.year, today.month
    for _ in range(n):
        starts.append(date(y, m, 1))
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    return list(reversed(starts))


class _Ctx:
    """Per-run mutable context (RNG + txn counter)."""

    def __init__(self, seed: int):
        self.fake = Faker("en_IN")
        Faker.seed(seed)
        random.seed(seed)
        np.random.seed(seed)
        self.txn_id = 0
        self.months = _month_starts(12)

    def next_txn_id(self) -> str:
        self.txn_id += 1
        return f"T{self.txn_id:08d}"


# --------------------------------------------------------------------------- #
# Customer profile
# --------------------------------------------------------------------------- #
def _make_profile(ctx: _Ctx, idx: int) -> Dict:
    fake = ctx.fake
    tier = int(np.random.choice([1, 2, 3], p=[0.42, 0.4, 0.18]))
    city = random.choice(CITY_TIERS[tier])
    employment = str(np.random.choice(
        ["salaried", "self_employed", "mixed"], p=[0.55, 0.30, 0.15]))
    age = int(np.clip(np.random.normal(37, 9), 23, 62))

    # True monthly income (INR), scaled by city tier and employment.
    tier_mult = {1: 1.0, 2: 0.72, 3: 0.55}[tier]
    base = float(np.random.lognormal(mean=math.log(55000), sigma=0.55)) * tier_mult
    if employment == "self_employed":
        base *= random.uniform(1.0, 1.8)  # business owners often earn more, opaquely
    true_income = float(np.clip(base, 18000, 900000))

    # Declared income = what the bank sees today.  Salaried is accurate; the
    # self-employed under-declare heavily -> the gap our engine closes.
    if employment == "salaried":
        declared = true_income * random.uniform(0.96, 1.02)
        verifiability = 0.95
    elif employment == "mixed":
        declared = true_income * random.uniform(0.72, 0.9)
        verifiability = 0.72
    else:
        declared = true_income * random.uniform(0.45, 0.72)
        verifiability = 0.45

    credit_score = int(np.clip(np.random.normal(730, 70), 540, 880))
    relationship_months = int(np.clip(np.random.exponential(48), 3, 240))

    products = ["Savings Account"]
    if random.random() < 0.45:
        products.append("Credit Card")
    if random.random() < 0.30:
        products.append("Fixed Deposit")

    # Loan intent (ground truth).  A minority are genuinely in-market at any
    # given time -- most customers are not, which keeps the base conversion
    # rate realistically low (~12-15%).
    if random.random() < 0.30:
        # self-employed skew to LAP; younger salaried skew to auto/personal
        weights = {
            "HOME_LOAN": 1.0 if age < 45 else 0.4,
            "AUTO_LOAN": 1.0,
            "PERSONAL_LOAN": 1.1,
            "MORTGAGE_LOAN": 1.4 if employment != "salaried" else 0.3,
        }
        keys = list(weights)
        w = np.array([weights[k] for k in keys], dtype=float)
        intent_product: Optional[str] = str(np.random.choice(keys, p=w / w.sum()))
        intent_strength = float(np.random.uniform(0.45, 0.95))
    else:
        intent_product = None
        intent_strength = float(np.random.uniform(0.0, 0.18))

    # A "why-now" trigger makes intent time-sensitive.
    trigger = None
    if intent_product and random.random() < 0.6:
        if employment in ("salaried", "mixed") and random.random() < 0.5:
            trigger = "salary_hike"
        elif random.random() < 0.5:
            trigger = "emi_closure"
        else:
            trigger = {"HOME_LOAN": "rent_escalation", "AUTO_LOAN": "dealer_enquiry",
                       "PERSONAL_LOAN": "large_expense", "MORTGAGE_LOAN": "business_expansion"}[intent_product]

    is_renter = (intent_product == "HOME_LOAN") or (random.random() < 0.25)
    has_existing_emi = random.random() < (0.5 if intent_product == "PERSONAL_LOAN" else 0.35)

    return {
        # ---- visible to engines (traditional metrics) ----
        "customer_id": f"CUST{idx:05d}",
        "name": fake.name(),
        "age": age,
        "gender": random.choice(["M", "F"]),
        "city": city,
        "city_tier": tier,
        "employment_type": employment,
        "declared_monthly_income": round(declared, -2),
        "credit_score": credit_score,
        "relationship_months": relationship_months,
        "existing_products": products,
        # ---- held-out latents (ground truth + drivers of txn generation) ----
        "_true_income": true_income,
        "_verifiability": verifiability,
        "_intent_product": intent_product,
        "_intent_strength": intent_strength,
        "_trigger": trigger,
        "_is_renter": is_renter,
        "_has_existing_emi": has_existing_emi,
        "_has_cc": "Credit Card" in products,
    }


# --------------------------------------------------------------------------- #
# Transaction stream
# --------------------------------------------------------------------------- #
def _txn(ctx: _Ctx, cid: str, d: date, amount: float, direction: str,
         category: str, channel: str, narration: str) -> Dict:
    return {
        "txn_id": ctx.next_txn_id(),
        "customer_id": cid,
        "date": d.isoformat(),
        "amount": round(amount if direction == "credit" else -amount, 2),
        "direction": direction,
        "category": category,
        "channel": channel,
        "narration": narration,
    }


def _day(month_start: date, day: int) -> date:
    return date(month_start.year, month_start.month, min(day, 28))


def _generate_txns(ctx: _Ctx, p: Dict) -> List[Dict]:
    cid = p["customer_id"]
    income = p["_true_income"]
    emp = p["employment_type"]
    txns: List[Dict] = []
    n_months = len(ctx.months)

    hike_month = random.randint(6, 9) if p["_trigger"] == "salary_hike" else None
    emi_stop_month = random.randint(7, 10) if p["_trigger"] == "emi_closure" else None
    employer = random.choice(EMPLOYERS)
    business = random.choice(BUSINESS_NAMES)
    landlord = ctx.fake.last_name().upper()
    fund = random.choice(MUTUAL_FUNDS)
    lender = random.choice(LENDERS)
    rent_amt = round(income * random.uniform(0.15, 0.26), -2) if p["_is_renter"] else 0
    sip_amt = round(income * random.uniform(0.05, 0.14), -2) if random.random() < (0.75 if p["_intent_product"] == "HOME_LOAN" else 0.4) else 0
    emi_amt = round(income * random.uniform(0.1, 0.22), -2) if p["_has_existing_emi"] else 0

    for mi, ms in enumerate(ctx.months):
        # ---------- income ----------
        if emp in ("salaried", "mixed"):
            sal = income if emp == "salaried" else income * 0.6
            if hike_month is not None and mi < hike_month:
                sal *= 0.78  # pre-hike level
            sal *= random.uniform(0.99, 1.01)
            txns.append(_txn(ctx, cid, _day(ms, 1), round(sal, -1), "credit",
                             "salary", "NEFT", f"NEFT CR-{employer}-SALARY"))
        if emp in ("self_employed", "mixed"):
            biz_target = income * (1.0 if emp == "self_employed" else 0.4)
            if p["_trigger"] == "business_expansion" and mi >= n_months - 4:
                biz_target *= 1.35  # growing inflows recently
            n_inflows = random.randint(12, 34)
            realized = 0.0
            for _ in range(n_inflows):
                amt = max(300, np.random.normal(biz_target / n_inflows, biz_target / n_inflows * 0.5))
                realized += amt
                txns.append(_txn(ctx, cid, _day(ms, random.randint(1, 28)), amt, "credit",
                                 "business_income", "UPI",
                                 f"UPI/{ctx.fake.first_name().lower()}{random.randint(10,99)}@oksbi/PAYMENT"))
            # cash-heavy businesses deposit part of takings
            if random.random() < 0.6:
                cash = max(0, biz_target * random.uniform(0.1, 0.3))
                txns.append(_txn(ctx, cid, _day(ms, random.randint(3, 25)), cash, "credit",
                                 "cash_deposit", "CASH", "CASH DEP SELF"))

        # ---------- recurring obligations ----------
        if rent_amt:
            txns.append(_txn(ctx, cid, _day(ms, 4), rent_amt, "debit", "rent", "UPI",
                             f"UPI/{landlord}/HOUSE RENT"))
        if emi_amt and (emi_stop_month is None or mi < emi_stop_month):
            txns.append(_txn(ctx, cid, _day(ms, 6), emi_amt, "debit", "emi", "AUTO_DEBIT",
                             f"ACH D- {lender} LOAN EMI"))
        if sip_amt:
            # savers building a corpus step up SIP over time (home-loan signal)
            step = 1.0 + (0.5 * mi / n_months if p["_intent_product"] == "HOME_LOAN" else 0)
            txns.append(_txn(ctx, cid, _day(ms, 5), round(sip_amt * step, -1), "debit",
                             "sip", "AUTO_DEBIT", f"ACH D-{fund} SIP"))
        if random.random() < 0.5:
            txns.append(_txn(ctx, cid, _day(ms, 8), round(income * 0.03, -1), "debit",
                             "insurance", "AUTO_DEBIT", f"ACH D-{random.choice(INSURERS)} PREMIUM"))
        if p["_has_cc"]:
            txns.append(_txn(ctx, cid, _day(ms, 12), round(income * random.uniform(0.05, 0.2), -1),
                             "debit", "credit_card_payment", "NEFT", "CC PAYMENT AUTOPAY"))
        # utilities
        txns.append(_txn(ctx, cid, _day(ms, 10), round(random.uniform(800, 4000), -1), "debit",
                         "utilities", "UPI", f"BILLPAY/{random.choice(['ELECTRICITY','MOBILE','DTH','GAS'])}"))

        # ---------- discretionary spend ----------
        spend_ratio = random.uniform(0.25, 0.5)
        n_disc = random.randint(12, 26)
        for _ in range(n_disc):
            cat = random.choices(
                ["groceries", "dining", "shopping", "fuel", "entertainment"],
                weights=[0.34, 0.24, 0.18, 0.14, 0.10])[0]
            merchant = {"groceries": GROCERS, "dining": FOOD, "shopping": SHOPPING,
                        "fuel": FUEL, "entertainment": ["BOOKMYSHOW", "NETFLIX", "PVR"]}[cat]
            amt = abs(np.random.normal(income * spend_ratio / n_disc, income * 0.01)) + 80
            txns.append(_txn(ctx, cid, _day(ms, random.randint(1, 28)), amt, "debit",
                             cat, random.choice(["UPI", "CARD"]),
                             f"UPI/{random.choice(merchant)}/PURCHASE"))

        # ---------- intent-specific "why now" signals ----------
        _plant_intent_signals(ctx, p, txns, mi, ms, income, n_months)

    # ---------- opening balance + running balance ----------
    txns.sort(key=lambda t: t["date"])
    balance = income * random.uniform(0.6, 2.2)
    if p["_intent_product"] == "PERSONAL_LOAN":
        balance *= 0.5  # tighter liquidity
    for t in txns:
        balance += t["amount"]
        t["balance"] = round(balance, 2)
    return txns


def _plant_intent_signals(ctx: _Ctx, p: Dict, txns: List[Dict], mi: int,
                          ms: date, income: float, n_months: int) -> None:
    """Add the behavioural fingerprints of a specific loan intent."""
    cid, prod, s = p["customer_id"], p["_intent_product"], p["_intent_strength"]
    if not prod:
        return
    recent = mi >= n_months - 3

    if prod == "AUTO_LOAN":
        # rising fuel spend (intensity ~ strength) + a recent dealer enquiry
        if recent:
            txns.append(_txn(ctx, cid, _day(ms, random.randint(1, 28)),
                             abs(np.random.normal(income * 0.04 * (0.6 + s), 200)) + 400, "debit",
                             "fuel", "UPI", f"UPI/{random.choice(FUEL)}/FUEL"))
        if mi == n_months - 1 and (p["_trigger"] == "dealer_enquiry" or s > 0.7):
            txns.append(_txn(ctx, cid, _day(ms, 20), round(income * 0.4 * (0.5 + s), -2), "debit",
                             "auto_purchase", "UPI", f"UPI/{random.choice(CAR_DEALERS)}/BOOKING TOKEN"))

    elif prod == "PERSONAL_LOAN":
        if recent and (p["_trigger"] == "large_expense" or s > 0.6):
            cat, mer = random.choice([("medical", HOSPITALS), ("education", EDU),
                                      ("travel", ["MAKEMYTRIP", "YATRA"])])
            txns.append(_txn(ctx, cid, _day(ms, random.randint(5, 25)),
                             round(income * (0.4 + s), -2), "debit",
                             cat, "CARD", f"UPI/{random.choice(mer)}/{cat.upper()}"))

    elif prod == "MORTGAGE_LOAN":
        if mi % 6 == 0:  # property tax -> owns property
            txns.append(_txn(ctx, cid, _day(ms, 15), round(income * 0.2, -2), "debit",
                             "utilities", "NEFT", "NEFT/MUNICIPAL CORP/PROPERTY TAX"))
        if recent and s > 0.4:  # large supplier outflow (working-capital need)
            txns.append(_txn(ctx, cid, _day(ms, random.randint(10, 25)),
                             round(income * (0.4 + 0.6 * s), -2), "debit",
                             "transfer_out", "RTGS", f"RTGS/{random.choice(BUSINESS_NAMES)}/SUPPLIER"))
    # HOME_LOAN signals (renting + rising SIP) are already emitted above.


# --------------------------------------------------------------------------- #
# Ground-truth conversion label
# --------------------------------------------------------------------------- #
def _would_convert(p: Dict) -> Tuple[bool, float]:
    """Latent propensity that a contacted prospect actually takes the loan.

    Driven by the SAME real-world factors the engines estimate from
    transactions, so a good lead score naturally isolates the high-converting
    subgroup.  Base rate ~10%; strong, affordable, verifiable, triggered
    prospects approach ~85%.
    """
    intent = p["_intent_strength"]
    verify = p["_verifiability"]
    # rough affordability proxy: income net of typical obligations
    afford = 1.0 if p["_true_income"] > 30000 and not (
        p["_has_existing_emi"] and p["_intent_product"] == "PERSONAL_LOAN") else 0.4
    trigger = 1.0 if p["_trigger"] else 0.0
    score = (p["credit_score"] - 700) / 100.0

    # Centred so a no-intent, average customer sits near a ~10% base rate,
    # while a strong + affordable + verifiable + triggered prospect approaches ~80%.
    z = (-3.45 + 3.6 * intent + 1.2 * (afford - 1.0) + 0.7 * (verify - 0.6)
         + 1.15 * trigger + 0.5 * score + float(np.random.normal(0, 0.18)))
    prob = _sigmoid(z)
    return (random.random() < prob), prob


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def generate_dataset(num_customers: int, seed: int) -> Dict:
    """Return {'customers': [...], 'transactions': [...], 'ground_truth': {...}}."""
    ctx = _Ctx(seed)
    customers: List[Dict] = []
    transactions: List[Dict] = []
    ground_truth: Dict[str, Dict] = {}

    for i in range(num_customers):
        p = _make_profile(ctx, i)
        transactions.extend(_generate_txns(ctx, p))
        converted, prob = _would_convert(p)
        ground_truth[p["customer_id"]] = {
            "true_monthly_income": round(p["_true_income"], -2),
            "intent_product": p["_intent_product"],
            "intent_strength": round(p["_intent_strength"], 3),
            "trigger": p["_trigger"],
            "would_convert": bool(converted),
            "convert_prob": round(prob, 3),
        }
        # strip latents before exposing the customer record
        customers.append({k: v for k, v in p.items() if not k.startswith("_")})

    return {"customers": customers, "transactions": transactions,
            "ground_truth": ground_truth}


if __name__ == "__main__":
    ds = generate_dataset(20, 42)
    print(f"customers={len(ds['customers'])} transactions={len(ds['transactions'])}")
    c0 = ds["customers"][0]
    print("sample customer:", c0["customer_id"], c0["employment_type"],
          "declared=", c0["declared_monthly_income"])
    print("ground truth:", ds["ground_truth"][c0["customer_id"]])
