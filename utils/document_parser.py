"""
Document Parser - Extracts structured data from PDFs
Handles: Bank Statements, Form 16, Salary Slips, Investment Proofs
"""

import re
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Optional


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        return f"ERROR: Could not read PDF - {str(e)}"


def detect_document_type(text: str) -> str:
    """Auto-detect what type of document was uploaded"""
    text_lower = text.lower()

    if any(kw in text_lower for kw in ["form 16", "form-16", "tds certificate", "certificate of tax deducted"]):
        return "form16"
    elif any(kw in text_lower for kw in ["bank statement", "account statement", "transaction history", "ifsc"]):
        return "bank_statement"
    elif any(kw in text_lower for kw in ["salary slip", "pay slip", "payslip", "pay stub", "earnings statement"]):
        return "salary_slip"
    elif any(kw in text_lower for kw in ["premium", "lic", "policy", "insurance", "ppf", "elss", "mutual fund"]):
        return "investment_proof"
    elif any(kw in text_lower for kw in ["rent receipt", "rent paid", "landlord"]):
        return "rent_receipt"
    else:
        return "unknown"


def parse_form16(text: str) -> Dict:
    """Parse Form 16 - extract salary and TDS info"""
    data = {
        "document_type": "Form 16",
        "employer_name": "",
        "pan": "",
        "gross_salary": 0,
        "basic_salary": 0,
        "hra": 0,
        "tds_deducted": 0,
        "pf_deduction": 0,
        "raw_fields": {}
    }

    # Extract PAN
    pan_match = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', text)
    if pan_match:
        data["pan"] = pan_match.group()

    # Extract monetary amounts with labels
    patterns = {
        "gross_salary": r'gross\s+salary[^\d]*?([\d,]+(?:\.\d{2})?)',
        "basic_salary": r'basic\s+salary[^\d]*?([\d,]+(?:\.\d{2})?)',
        "hra": r'h\.?r\.?a\.?[^\d]*?([\d,]+(?:\.\d{2})?)',
        "tds_deducted": r'tax\s+deducted[^\d]*?([\d,]+(?:\.\d{2})?)',
        "pf_deduction": r'provident\s+fund[^\d]*?([\d,]+(?:\.\d{2})?)',
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                data[field] = float(amount_str)
            except ValueError:
                pass

    # Extract employer name (usually near "Name of Employer" or "Employer Name")
    emp_match = re.search(r'(?:employer|company)\s*name[:\s]+([A-Za-z\s&.]+?)(?:\n|,|\d)', text, re.IGNORECASE)
    if emp_match:
        data["employer_name"] = emp_match.group(1).strip()

    return data


def parse_bank_statement(text: str) -> Dict:
    """Parse bank statement - extract salary credits and interest"""
    data = {
        "document_type": "Bank Statement",
        "account_number": "",
        "bank_name": "",
        "salary_credits": [],
        "total_salary_credited": 0,
        "interest_earned": 0,
        "large_credits": [],
        "raw_text_preview": text[:500]
    }

    # Detect bank name
    for bank in ["SBI", "HDFC", "ICICI", "Axis", "Kotak", "PNB", "Bank of Baroda", "Canara"]:
        if bank.lower() in text.lower():
            data["bank_name"] = bank
            break

    # Extract account number
    acc_match = re.search(r'(?:account\s*(?:no|number)[.:\s]*)([\dX*]+)', text, re.IGNORECASE)
    if acc_match:
        data["account_number"] = acc_match.group(1)

    # Find salary credits (look for "SALARY", "SAL", "NEFT CR" with amounts)
    salary_pattern = re.findall(
        r'(?:salary|sal\b|neft.*?cr|credit.*?salary)[^\d]*([\d,]+(?:\.\d{2})?)',
        text, re.IGNORECASE
    )
    for amt in salary_pattern:
        try:
            amount = float(amt.replace(',', ''))
            if amount > 10000:  # Filter noise
                data["salary_credits"].append(amount)
        except ValueError:
            pass

    if data["salary_credits"]:
        data["total_salary_credited"] = sum(data["salary_credits"])

    # Find interest credits
    interest_pattern = re.findall(
        r'(?:interest\s*cr|int\s*cr|savings\s*int)[^\d]*([\d,]+(?:\.\d{2})?)',
        text, re.IGNORECASE
    )
    for amt in interest_pattern:
        try:
            data["interest_earned"] += float(amt.replace(',', ''))
        except ValueError:
            pass

    # Find all large credits (> 50K) - could be FD maturity, bonus etc.
    all_amounts = re.findall(r'CR\s*([\d,]+(?:\.\d{2})?)', text)
    for amt in all_amounts:
        try:
            amount = float(amt.replace(',', ''))
            if amount > 50000:
                data["large_credits"].append(amount)
        except ValueError:
            pass

    return data


def parse_salary_slip(text: str) -> Dict:
    """Parse salary slip - extract components"""
    data = {
        "document_type": "Salary Slip",
        "month": "",
        "employee_name": "",
        "basic": 0,
        "hra": 0,
        "da": 0,
        "special_allowance": 0,
        "pf_deduction": 0,
        "professional_tax": 0,
        "tds_this_month": 0,
        "net_salary": 0,
        "gross_salary": 0
    }

    # Salary components
    components = {
        "basic": r'basic(?:\s+pay|\s+salary)?[^\d]*([\d,]+(?:\.\d{2})?)',
        "hra": r'h\.?r\.?a\.?[^\d]*([\d,]+(?:\.\d{2})?)',
        "da": r'\bda\b|dearness\s+allowance[^\d]*([\d,]+(?:\.\d{2})?)',
        "special_allowance": r'special\s+allowance[^\d]*([\d,]+(?:\.\d{2})?)',
        "pf_deduction": r'(?:pf|provident\s+fund)\s*(?:deduction|contribution)?[^\d]*([\d,]+(?:\.\d{2})?)',
        "tds_this_month": r'tds[^\d]*([\d,]+(?:\.\d{2})?)',
        "net_salary": r'net\s+(?:salary|pay|take\s*home)[^\d]*([\d,]+(?:\.\d{2})?)',
        "gross_salary": r'gross\s+(?:salary|pay|earnings)[^\d]*([\d,]+(?:\.\d{2})?)',
    }

    for field, pattern in components.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            amt_str = groups[-1] if groups else None
            if amt_str:
                try:
                    data[field] = float(amt_str.replace(',', ''))
                except ValueError:
                    pass

    # Extract month/year
    month_match = re.search(
        r'(?:month|pay\s*period|for\s*the\s*month)[:\s]*((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\S*\s*\d{4})',
        text, re.IGNORECASE
    )
    if month_match:
        data["month"] = month_match.group(1)

    return data


def parse_investment_proof(text: str) -> Dict:
    """Parse investment proof - LIC, PPF, ELSS, etc."""
    data = {
        "document_type": "Investment Proof",
        "investment_type": "Unknown",
        "amount": 0,
        "section": ""
    }

    text_lower = text.lower()

    if "lic" in text_lower or "life insurance" in text_lower:
        data["investment_type"] = "LIC Premium"
        data["section"] = "80C"
    elif "ppf" in text_lower or "public provident" in text_lower:
        data["investment_type"] = "PPF"
        data["section"] = "80C"
    elif "elss" in text_lower or "equity linked" in text_lower:
        data["investment_type"] = "ELSS Mutual Fund"
        data["section"] = "80C"
    elif "nps" in text_lower or "national pension" in text_lower:
        data["investment_type"] = "NPS"
        data["section"] = "80CCD(1B)"
    elif "health" in text_lower or "mediclaim" in text_lower:
        data["investment_type"] = "Health Insurance"
        data["section"] = "80D"

    # Extract amount
    amount_patterns = [
        r'premium\s*(?:amount|paid)?[:\s]*([\d,]+)',
        r'amount\s*(?:paid|deposited)?[:\s]*([\d,]+)',
        r'total\s*(?:amount)?[:\s]*([\d,]+)',
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                data["amount"] = float(match.group(1).replace(',', ''))
                break
            except ValueError:
                pass

    return data


def parse_document(pdf_path: str) -> Dict:
    """
    Main entry point - auto detects and parses any document
    Returns structured dict with all extracted fields
    """
    text = extract_text_from_pdf(pdf_path)

    if text.startswith("ERROR"):
        return {"error": text, "document_type": "error"}

    doc_type = detect_document_type(text)

    if doc_type == "form16":
        result = parse_form16(text)
    elif doc_type == "bank_statement":
        result = parse_bank_statement(text)
    elif doc_type == "salary_slip":
        result = parse_salary_slip(text)
    elif doc_type == "investment_proof":
        result = parse_investment_proof(text)
    else:
        result = {
            "document_type": "Unknown",
            "raw_text_preview": text[:1000],
            "message": "Could not auto-detect document type. Please check the file."
        }

    result["raw_text"] = text
    result["file_path"] = str(pdf_path)
    return result
