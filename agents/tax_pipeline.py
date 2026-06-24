"""
LangGraph Multi-Agent Tax Pipeline
5 Agents: Parser → Income → Deduction → Calculator → Explainer
"""

import os
import json
from typing import TypedDict, List, Dict, Any, Optional
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

load_dotenv()

# ─── LLM Setup ────────────────────────────────────────────────────────────────

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError(
            "❌ GROQ_API_KEY not set!\n"
            "1. Go to https://console.groq.com (Free)\n"
            "2. Create API key\n"
            "3. Add to .env file: GROQ_API_KEY=your_key_here"
        )
    return ChatGroq(
        api_key=api_key,
        model="llama3-8b-8192",
        temperature=0.1,
        max_tokens=2048
    )


# ─── Shared Agent State ────────────────────────────────────────────────────────

class TaxAgentState(TypedDict):
    # Input
    parsed_documents: List[Dict]
    language: str  # "english" or "hindi"

    # Agent outputs (populated step by step)
    income_summary: Dict
    deductions_found: Dict
    missed_deductions: List[str]
    tax_result: Dict
    explanation: str
    recommendations: List[str]

    # Status tracking
    current_step: str
    errors: List[str]


# ─── Agent 1: Income Aggregator ───────────────────────────────────────────────

def income_aggregator_agent(state: TaxAgentState) -> TaxAgentState:
    """Reads parsed docs and builds a complete income picture"""
    print("🔍 Agent 1: Income Aggregator running...")
    state["current_step"] = "income_aggregation"

    docs = state["parsed_documents"]
    income = {
        "basic_salary": 0,
        "hra_received": 0,
        "da": 0,
        "special_allowance": 0,
        "gross_salary": 0,
        "interest_income": 0,
        "other_income": 0,
        "tds_deducted": 0,
        "sources": []
    }

    for doc in docs:
        doc_type = doc.get("document_type", "")

        if "Form 16" in doc_type:
            income["gross_salary"] = doc.get("gross_salary", 0)
            income["basic_salary"] = doc.get("basic_salary", 0)
            income["hra_received"] = doc.get("hra", 0)
            income["tds_deducted"] = doc.get("tds_deducted", 0)
            income["sources"].append("Form 16")

        elif "Salary Slip" in doc_type:
            if income["basic_salary"] == 0:
                income["basic_salary"] = doc.get("basic", 0) * 12
            if income["hra_received"] == 0:
                income["hra_received"] = doc.get("hra", 0) * 12
            income["da"] = doc.get("da", 0) * 12
            income["special_allowance"] = doc.get("special_allowance", 0) * 12
            income["sources"].append("Salary Slip")

        elif "Bank Statement" in doc_type:
            income["interest_income"] += doc.get("interest_earned", 0)
            if income["gross_salary"] == 0 and doc.get("total_salary_credited", 0) > 0:
                income["gross_salary"] = doc.get("total_salary_credited", 0)
            income["sources"].append("Bank Statement")

    # Compute gross if not directly available
    if income["gross_salary"] == 0:
        income["gross_salary"] = (income["basic_salary"] + income["hra_received"] +
                                   income["da"] + income["special_allowance"])

    income["total_income"] = income["gross_salary"] + income["interest_income"] + income["other_income"]

    state["income_summary"] = income
    print(f"   ✅ Total Income identified: ₹{income['total_income']:,.0f}")
    return state


# ─── Agent 2: Deduction Finder ────────────────────────────────────────────────

def deduction_finder_agent(state: TaxAgentState) -> TaxAgentState:
    """Finds deductions from docs AND uses LLM to spot what's missing"""
    print("🔍 Agent 2: Deduction Finder running...")
    state["current_step"] = "deduction_finding"

    docs = state["parsed_documents"]
    deductions = {
        "pf_contribution": 0,
        "lic_premium": 0,
        "ppf": 0,
        "elss": 0,
        "nps": 0,
        "health_insurance": 0,
        "health_insurance_parents": 0,
        "rent_paid_monthly": 0,
        "savings_interest": 0,
        "education_loan": 0,
        "donations": 0,
        "city_type": "non-metro"
    }

    # Extract from documents
    for doc in docs:
        doc_type = doc.get("document_type", "")

        if "Salary Slip" in doc_type or "Form 16" in doc_type:
            if "pf_deduction" in doc:
                pf_annual = doc["pf_deduction"] * 12 if doc_type == "Salary Slip" else doc["pf_deduction"]
                deductions["pf_contribution"] = pf_annual

        elif "Investment Proof" in doc_type:
            inv_type = doc.get("investment_type", "")
            amount = doc.get("amount", 0)
            if "LIC" in inv_type:
                deductions["lic_premium"] += amount
            elif "PPF" in inv_type:
                deductions["ppf"] += amount
            elif "ELSS" in inv_type:
                deductions["elss"] += amount
            elif "NPS" in inv_type:
                deductions["nps"] += amount
            elif "Health" in inv_type:
                deductions["health_insurance"] += amount

        elif "Bank Statement" in doc_type:
            deductions["savings_interest"] = doc.get("interest_earned", 0)

    # Use LLM to identify possibly missed deductions
    try:
        llm = get_llm()
        income = state["income_summary"]
        prompt = f"""
You are an expert Indian tax advisor (CA).
Based on the following income and deductions found, identify which common deductions the person might be MISSING.

Income: ₹{income.get('total_income', 0):,.0f} per year
Basic Salary: ₹{income.get('basic_salary', 0):,.0f}
HRA Received: ₹{income.get('hra_received', 0):,.0f}

Deductions already found:
- PF: ₹{deductions['pf_contribution']:,.0f}
- LIC: ₹{deductions['lic_premium']:,.0f}
- PPF: ₹{deductions['ppf']:,.0f}
- ELSS: ₹{deductions['elss']:,.0f}
- Health Insurance (self): ₹{deductions['health_insurance']:,.0f}
- NPS: ₹{deductions['nps']:,.0f}

List ONLY the deductions that are missing and commonly applicable.
Format as JSON array of strings. Example:
["HRA exemption (if paying rent, upload rent receipts)", "80D health insurance for parents (max ₹25,000)"]

Return ONLY the JSON array, no other text.
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        missed_text = response.content.strip()
        if missed_text.startswith("["):
            missed = json.loads(missed_text)
        else:
            missed = ["Check 80C limit (max ₹1.5L)", "Consider NPS for additional ₹50K deduction under 80CCD(1B)"]
    except Exception as e:
        print(f"   ⚠️  LLM call skipped: {e}")
        missed = [
            "80C - Consider ELSS mutual funds if 80C limit not fully utilized (max ₹1.5L)",
            "80D - Health insurance for parents (max ₹25,000)",
            "80CCD(1B) - NPS contribution for extra ₹50,000 deduction",
            "HRA Exemption - Upload rent receipts if you pay rent"
        ]

    state["deductions_found"] = deductions
    state["missed_deductions"] = missed
    print(f"   ✅ Found {len(missed)} potentially missed deductions")
    return state


# ─── Agent 3: Tax Calculator ──────────────────────────────────────────────────

def tax_calculator_agent(state: TaxAgentState) -> TaxAgentState:
    """Runs the actual tax math for old and new regime"""
    print("🔍 Agent 3: Tax Calculator running...")
    state["current_step"] = "tax_calculation"

    from utils.tax_calculator import (
        TaxableIncome, Deductions, compute_full_tax
    )

    inc = state["income_summary"]
    ded = state["deductions_found"]

    income_obj = TaxableIncome(
        basic_salary=inc.get("basic_salary", 0),
        hra_received=inc.get("hra_received", 0),
        da=inc.get("da", 0),
        special_allowance=inc.get("special_allowance", 0),
        interest_income=inc.get("interest_income", 0),
        tds_deducted=inc.get("tds_deducted", 0)
    )

    ded_obj = Deductions(
        pf_contribution=ded.get("pf_contribution", 0),
        lic_premium=ded.get("lic_premium", 0),
        ppf=ded.get("ppf", 0),
        elss_mutual_fund=ded.get("elss", 0),
        health_insurance_self=ded.get("health_insurance", 0),
        health_insurance_parents=ded.get("health_insurance_parents", 0),
        nps_contribution=ded.get("nps", 0),
        rent_paid_monthly=ded.get("rent_paid_monthly", 0),
        city_type=ded.get("city_type", "non-metro"),
        savings_interest=ded.get("savings_interest", 0),
        education_loan_interest=ded.get("education_loan", 0),
        donations=ded.get("donations", 0)
    )

    result = compute_full_tax(income_obj, ded_obj)
    state["tax_result"] = result
    rec = result["recommendation"]
    print(f"   ✅ Best regime: {rec['best_regime']} — saves ₹{rec['savings']:,.0f}")
    return state


# ─── Agent 4: Explainer ───────────────────────────────────────────────────────

def explainer_agent(state: TaxAgentState) -> TaxAgentState:
    """Generates a plain Hindi/English explanation of the tax calculation"""
    print("🔍 Agent 4: Explainer Agent running...")
    state["current_step"] = "explanation"

    language = state.get("language", "english")
    tax = state["tax_result"]
    income = state["income_summary"]
    missed = state["missed_deductions"]
    rec = tax["recommendation"]

    try:
        llm = get_llm()

        if language == "hindi":
            lang_instruction = "Respond ONLY in simple Hindi (Devanagari script). Use simple everyday language."
        else:
            lang_instruction = "Respond in simple English. Avoid jargon."

        prompt = f"""
You are a friendly Indian CA (Chartered Accountant) explaining tax results to a salaried employee.
{lang_instruction}

Here are the results:
- Gross Annual Income: ₹{income.get('total_income', 0):,.0f}
- New Regime Tax: ₹{tax['new_regime']['tax']:,.0f}
- Old Regime Tax: ₹{tax['old_regime']['tax']:,.0f}
- Best Choice: {rec['best_regime']}
- You save: ₹{rec['savings']:,.0f} by choosing {rec['best_regime']}
- TDS already paid: ₹{tax['new_regime']['tds_paid']:,.0f}
- Under best regime — {'Refund: ₹' + str(abs(tax['new_regime']['refund_payable'] if rec['best_regime']=='New Regime' else tax['old_regime']['refund_payable'])) if (tax['new_regime']['refund_payable'] if rec['best_regime']=='New Regime' else tax['old_regime']['refund_payable']) > 0 else 'Tax Payable: ₹' + str(abs(tax['new_regime']['refund_payable'] if rec['best_regime']=='New Regime' else tax['old_regime']['refund_payable']))}

Possibly missed deductions: {', '.join(missed[:3]) if missed else 'None'}

Write a short (5-7 line) friendly explanation covering:
1. Their income and which regime is better and why
2. Whether they get refund or need to pay more tax
3. One most important deduction they should claim

Be warm, simple, and encouraging.
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        explanation = response.content.strip()
    except Exception as e:
        print(f"   ⚠️  LLM explanation skipped: {e}")
        best = rec['best_regime']
        best_data = tax['new_regime'] if best == 'New Regime' else tax['old_regime']
        refund_payable = best_data['refund_payable']
        status = "refund" if refund_payable > 0 else "tax payable"
        explanation = (
            f"Your gross annual income is ₹{income.get('total_income', 0):,.0f}. "
            f"Based on our analysis, {best} is better for you, saving ₹{rec['savings']:,.0f}. "
            f"Under {best}, your tax is ₹{best_data['tax']:,.0f}. "
            f"Since your employer deducted ₹{best_data['tds_paid']:,.0f} as TDS, "
            f"you have a {status} of ₹{abs(refund_payable):,.0f}. "
            f"{'Great news — you\'ll get a refund!' if refund_payable > 0 else 'You need to pay this additional tax before the ITR deadline.'}"
        )

    state["explanation"] = explanation

    # Build recommendations
    recs = []
    best = rec['best_regime']
    best_data = tax['new_regime'] if best == 'New Regime' else tax['old_regime']

    recs.append(f"✅ File ITR under {best} to save ₹{rec['savings']:,.0f}")

    if best_data['refund_payable'] > 0:
        recs.append(f"💰 You are eligible for a refund of ₹{abs(best_data['refund_payable']):,.0f} — file ITR to claim it!")
    else:
        recs.append(f"⚠️ Pay ₹{abs(best_data['refund_payable']):,.0f} as advance tax before March 31 to avoid interest")

    for m in missed[:2]:
        recs.append(f"📌 {m}")

    recs.append("📅 ITR filing deadline: July 31, 2024 (for FY 2023-24)")

    state["recommendations"] = recs
    print("   ✅ Explanation generated")
    return state


# ─── Build the LangGraph Pipeline ─────────────────────────────────────────────

def build_tax_pipeline():
    """Build and compile the multi-agent graph"""
    graph = StateGraph(TaxAgentState)

    graph.add_node("income_aggregator", income_aggregator_agent)
    graph.add_node("deduction_finder", deduction_finder_agent)
    graph.add_node("tax_calculator", tax_calculator_agent)
    graph.add_node("explainer", explainer_agent)

    graph.set_entry_point("income_aggregator")
    graph.add_edge("income_aggregator", "deduction_finder")
    graph.add_edge("deduction_finder", "tax_calculator")
    graph.add_edge("tax_calculator", "explainer")
    graph.add_edge("explainer", END)

    return graph.compile()


def run_tax_analysis(parsed_documents: List[Dict], language: str = "english") -> TaxAgentState:
    """
    Main entry point — runs all 4 agents and returns complete analysis
    """
    pipeline = build_tax_pipeline()

    initial_state: TaxAgentState = {
        "parsed_documents": parsed_documents,
        "language": language,
        "income_summary": {},
        "deductions_found": {},
        "missed_deductions": [],
        "tax_result": {},
        "explanation": "",
        "recommendations": [],
        "current_step": "start",
        "errors": []
    }

    print("\n🚀 Starting Tax Analysis Pipeline...")
    print("=" * 50)
    result = pipeline.invoke(initial_state)
    print("=" * 50)
    print("✅ Pipeline complete!\n")
    return result
