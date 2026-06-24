"""
Indian Tax Calculator - FY 2024-25
Handles both Old and New Tax Regime
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class TaxableIncome:
    basic_salary: float = 0
    hra_received: float = 0
    da: float = 0
    special_allowance: float = 0
    other_allowances: float = 0
    interest_income: float = 0       # savings account interest
    fd_interest: float = 0
    other_income: float = 0
    tds_deducted: float = 0
    advance_tax_paid: float = 0

    @property
    def gross_salary(self):
        return (self.basic_salary + self.hra_received + self.da +
                self.special_allowance + self.other_allowances)

    @property
    def total_income(self):
        return self.gross_salary + self.interest_income + self.fd_interest + self.other_income


@dataclass
class Deductions:
    # 80C - Max 1.5L
    pf_contribution: float = 0
    ppf: float = 0
    elss_mutual_fund: float = 0
    lic_premium: float = 0
    home_loan_principal: float = 0
    nsc: float = 0
    sukanya_samriddhi: float = 0
    tuition_fees: float = 0

    # 80D - Health Insurance - Max 25K (60K for senior citizen)
    health_insurance_self: float = 0
    health_insurance_parents: float = 0

    # HRA Exemption inputs
    rent_paid_monthly: float = 0
    city_type: str = "non-metro"      # "metro" or "non-metro"

    # 80TTA - Savings interest - Max 10K
    savings_interest: float = 0

    # 80E - Education Loan Interest (no limit)
    education_loan_interest: float = 0

    # 80G - Donations
    donations: float = 0

    # NPS - 80CCD(1B) - Additional 50K
    nps_contribution: float = 0

    @property
    def section_80c_total(self):
        total = (self.pf_contribution + self.ppf + self.elss_mutual_fund +
                 self.lic_premium + self.home_loan_principal + self.nsc +
                 self.sukanya_samriddhi + self.tuition_fees)
        return min(total, 150000)  # Max 1.5L

    @property
    def section_80d_total(self):
        self_limit = 25000
        parent_limit = 25000
        return min(self.health_insurance_self, self_limit) + min(self.health_insurance_parents, parent_limit)

    @property
    def section_80tta_total(self):
        return min(self.savings_interest, 10000)

    @property
    def nps_80ccd_total(self):
        return min(self.nps_contribution, 50000)


def calculate_hra_exemption(basic: float, da: float, hra_received: float,
                             rent_monthly: float, city_type: str) -> float:
    """Calculate HRA exemption under Section 10(13A)"""
    if rent_monthly == 0 or hra_received == 0:
        return 0

    annual_rent = rent_monthly * 12
    basic_da = basic + da

    # HRA exemption = Minimum of:
    # 1. Actual HRA received
    # 2. 50% of (Basic+DA) for metro / 40% for non-metro
    # 3. Actual rent paid - 10% of (Basic+DA)

    metro_percent = 0.50 if city_type == "metro" else 0.40

    hra_1 = hra_received
    hra_2 = basic_da * metro_percent
    hra_3 = max(0, annual_rent - (basic_da * 0.10))

    return min(hra_1, hra_2, hra_3)


def calculate_tax_new_regime(taxable_income: float) -> float:
    """
    New Tax Regime Slabs - FY 2024-25
    Standard deduction of 75,000 allowed
    """
    if taxable_income <= 300000:
        return 0
    elif taxable_income <= 700000:
        tax = (taxable_income - 300000) * 0.05
    elif taxable_income <= 1000000:
        tax = (400000 * 0.05) + (taxable_income - 700000) * 0.10
    elif taxable_income <= 1200000:
        tax = (400000 * 0.05) + (300000 * 0.10) + (taxable_income - 1000000) * 0.15
    elif taxable_income <= 1500000:
        tax = (400000 * 0.05) + (300000 * 0.10) + (200000 * 0.15) + (taxable_income - 1200000) * 0.20
    else:
        tax = (400000 * 0.05) + (300000 * 0.10) + (200000 * 0.15) + (300000 * 0.20) + (taxable_income - 1500000) * 0.30

    # Rebate u/s 87A — if income <= 7L, tax = 0
    if taxable_income <= 700000:
        tax = 0

    # Add 4% Health & Education Cess
    tax = tax * 1.04
    return round(tax, 2)


def calculate_tax_old_regime(taxable_income: float) -> float:
    """
    Old Tax Regime Slabs - FY 2024-25
    """
    if taxable_income <= 250000:
        return 0
    elif taxable_income <= 500000:
        tax = (taxable_income - 250000) * 0.05
    elif taxable_income <= 1000000:
        tax = (250000 * 0.05) + (taxable_income - 500000) * 0.20
    else:
        tax = (250000 * 0.05) + (500000 * 0.20) + (taxable_income - 1000000) * 0.30

    # Rebate u/s 87A — if income <= 5L, tax = 0
    if taxable_income <= 500000:
        tax = 0

    # Add 4% Health & Education Cess
    tax = tax * 1.04
    return round(tax, 2)


def compute_full_tax(income: TaxableIncome, deductions: Deductions) -> Dict:
    """
    Main function — computes tax under both regimes and compares
    Returns full breakdown dict
    """
    gross = income.total_income

    # ---- NEW REGIME ----
    standard_deduction_new = 75000
    new_taxable = max(0, gross - standard_deduction_new)
    new_tax = calculate_tax_new_regime(new_taxable)

    # ---- OLD REGIME ----
    standard_deduction_old = 50000
    hra_exemption = calculate_hra_exemption(
        income.basic_salary, income.da,
        income.hra_received,
        deductions.rent_paid_monthly,
        deductions.city_type
    )

    old_taxable = (gross
                   - standard_deduction_old
                   - hra_exemption
                   - deductions.section_80c_total
                   - deductions.section_80d_total
                   - deductions.section_80tta_total
                   - deductions.education_loan_interest
                   - deductions.nps_80ccd_total
                   - deductions.donations)
    old_taxable = max(0, old_taxable)
    old_tax = calculate_tax_old_regime(old_taxable)

    # ---- REFUND / PAYABLE ----
    total_tds = income.tds_deducted + income.advance_tax_paid
    new_refund_payable = total_tds - new_tax
    old_refund_payable = total_tds - old_tax

    best_regime = "New Regime" if new_tax <= old_tax else "Old Regime"
    savings = abs(new_tax - old_tax)

    return {
        "gross_income": gross,

        # New Regime
        "new_regime": {
            "standard_deduction": standard_deduction_new,
            "taxable_income": new_taxable,
            "tax": new_tax,
            "tds_paid": total_tds,
            "refund_payable": new_refund_payable,
            "status": "Refund" if new_refund_payable > 0 else "Payable"
        },

        # Old Regime
        "old_regime": {
            "standard_deduction": standard_deduction_old,
            "hra_exemption": hra_exemption,
            "80c_deduction": deductions.section_80c_total,
            "80d_deduction": deductions.section_80d_total,
            "80tta_deduction": deductions.section_80tta_total,
            "80e_deduction": deductions.education_loan_interest,
            "80ccd_deduction": deductions.nps_80ccd_total,
            "80g_deduction": deductions.donations,
            "total_deductions": (standard_deduction_old + hra_exemption +
                                  deductions.section_80c_total + deductions.section_80d_total +
                                  deductions.section_80tta_total + deductions.education_loan_interest +
                                  deductions.nps_80ccd_total + deductions.donations),
            "taxable_income": old_taxable,
            "tax": old_tax,
            "tds_paid": total_tds,
            "refund_payable": old_refund_payable,
            "status": "Refund" if old_refund_payable > 0 else "Payable"
        },

        # Recommendation
        "recommendation": {
            "best_regime": best_regime,
            "savings": savings,
            "reason": f"{'New' if best_regime == 'New Regime' else 'Old'} Regime saves ₹{savings:,.0f} in taxes"
        }
    }
