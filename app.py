"""
🇮🇳 AI Tax Filing Assistant — India
Streamlit UI with Multi-Agent LangGraph Pipeline
"""

import streamlit as st
import os
import sys
import tempfile
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

from utils.document_parser import parse_document
from utils.report_generator import generate_tax_report
from agents.tax_pipeline import run_tax_analysis

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Tax Assistant 🇮🇳",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main-header {
        background: #000000;
        padding: 2.5rem;
        border-radius: 0;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
        border: 4px solid #000000;
        box-shadow: 8px 8px 0px #000000;
    }
    .metric-card {
        background: white;
        border: 3px solid #000000;
        border-radius: 0;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 6px 6px 0px #000000;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translate(-2px, -2px);
        box-shadow: 8px 8px 0px #000000;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 900;
        color: #000000;
    }
    .metric-label {
        font-size: 0.9rem;
        font-weight: 800;
        color: #000000;
        text-transform: uppercase;
        margin-top: 8px;
        letter-spacing: 0.5px;
    }
    .refund-box {
        background: #000000;
        color: white;
        padding: 1.5rem;
        border-radius: 0;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 900;
        border: 4px solid #000000;
        box-shadow: 6px 6px 0px #000000;
        text-transform: uppercase;
    }
    .payable-box {
        background: white;
        color: #000000;
        padding: 1.5rem;
        border-radius: 0;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 900;
        border: 4px solid #000000;
        box-shadow: 6px 6px 0px #000000;
        text-transform: uppercase;
    }
    .missed-deduction {
        background: white;
        border: 3px solid #000000;
        padding: 1rem;
        border-radius: 0;
        margin: 0.5rem 0;
        font-weight: 800;
        color: #000000;
        font-size: 1rem;
        box-shadow: 4px 4px 0px #000000;
    }
    .recommendation {
        background: #000000;
        color: white;
        border: 3px solid #000000;
        padding: 1rem;
        border-radius: 0;
        margin: 0.5rem 0;
        font-weight: 800;
        font-size: 1rem;
        box-shadow: 4px 4px 0px white, 6px 6px 0px #000000;
    }
    .agent-step {
        background: white;
        color: #000000;
        border-radius: 0;
        padding: 0.8rem 1rem;
        margin: 0.3rem 0;
        font-weight: 900;
        font-size: 0.95rem;
        border: 3px solid #000000;
        box-shadow: 4px 4px 0px #000000;
        text-transform: uppercase;
        text-align: center;
    }
    .best-regime-badge {
        background: #000000;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 0;
        font-weight: 900;
        font-size: 0.9rem;
        text-transform: uppercase;
        border: 2px solid #000000;
    }
    div[data-testid="stFileUploader"] {
        border: 4px solid #000000;
        border-radius: 0;
        padding: 1.5rem;
        background: #ffffff;
    }
    div[data-testid="stFileUploader"] * {
        color: #000000 !important;
    }
    div[data-testid="stFileUploadDropzone"] {
        border: 4px dashed #000000 !important;
        background: #ffffff !important;
        border-radius: 0 !important;
        padding: 2rem !important;
    }
    div[data-testid="stUploadedFile"] {
        border: 2px solid #000000;
        background: #ffffff;
        border-radius: 0;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>🧾 AI Tax Filing Assistant</h1>
    <p style="opacity:0.9; margin:0">Upload your documents → Get instant tax analysis powered by AI agents</p>
    <p style="opacity:0.7; font-size:0.85rem; margin-top:8px">FY 2023-24 | Supports: Form 16, Bank Statement, Salary Slips, Investment Proofs</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("⚙️ Settings 🇮🇳")



    language = st.radio(
        "🌐 Explanation Language",
        ["English", "Hindi (हिंदी)"],
        index=0
    )
    lang_code = "hindi" if "Hindi" in language else "english"

    st.divider()

    st.subheader("🏙️ City Type (for HRA)")
    city_type = st.radio(
        "Your city",
        ["Non-Metro", "Metro (Mumbai/Delhi/Chennai/Kolkata)"],
        index=0,
        help="Metro cities get 50% HRA exemption vs 40% for non-metro"
    )

    st.divider()


    st.markdown("""
    **📌 How it works:**
    1. Upload your documents
    2. AI agents extract data
    3. Tax is calculated automatically
    4. Get Old vs New Regime comparison
    5. Download PDF report

    **🤖 Agents:**
    - 📊 Income Aggregator
    - 🔍 Deduction Finder
    - 🧮 Tax Calculator
    - 💬 Explainer
    """)

# ─── Main Area ────────────────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs(["📤 Upload & Analyze", "🧮 Manual Entry", "ℹ️ Tax Guide"])

# ══════════════════════════════════════════════════════════════════════
# TAB 1: Document Upload
# ══════════════════════════════════════════════════════════════════════

with tab1:
    st.subheader("📂 Upload Your Documents")
    st.info("Supported: Form 16, Bank Statement, Salary Slips, Investment Proofs (PDF format)")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_files = st.file_uploader(
            "Drop your PDF documents here",
            type=["pdf"],
            accept_multiple_files=True,
            help="You can upload multiple documents at once"
        )

    with col2:
        st.markdown("**📋 Document Checklist:**")
        st.markdown("✅ Form 16 (from employer)")
        st.markdown("✅ Bank Statement (Apr-Mar)")
        st.markdown("⬜ Salary Slips (optional)")
        st.markdown("⬜ LIC/PPF/ELSS receipts")
        st.markdown("⬜ Health Insurance proof")

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} document(s) uploaded")

        # Show uploaded files
        for f in uploaded_files:
            st.markdown(f"📄 **{f.name}** — `{f.size / 1024:.1f} KB`")

        st.divider()

        if st.button("🚀 Analyze My Taxes", type="primary", use_container_width=True):
            parsed_docs = []

            # Progress
            progress = st.progress(0)
            status = st.empty()

            # Step 1: Parse documents
            status.markdown("**Step 1/5:** 📄 Parsing documents...")
            progress.progress(10)

            with tempfile.TemporaryDirectory() as tmp_dir:
                for i, uploaded_file in enumerate(uploaded_files):
                    tmp_path = Path(tmp_dir) / uploaded_file.name
                    tmp_path.write_bytes(uploaded_file.read())
                    parsed = parse_document(str(tmp_path))
                    # Inject city type
                    if "deductions_found" not in parsed:
                        parsed["city_type_override"] = "metro" if "Metro" in city_type else "non-metro"
                    parsed_docs.append(parsed)

            progress.progress(25)
            status.markdown("**Step 2/5:** 🤖 Running AI agents...")

            # Show agent pipeline
            agent_container = st.container()
            with agent_container:
                a1, a2, a3, a4 = st.columns(4)
                with a1:
                    st.markdown('<div class="agent-step">📊 Income<br>Aggregator</div>', unsafe_allow_html=True)
                with a2:
                    st.markdown('<div class="agent-step">🔍 Deduction<br>Finder</div>', unsafe_allow_html=True)
                with a3:
                    st.markdown('<div class="agent-step">🧮 Tax<br>Calculator</div>', unsafe_allow_html=True)
                with a4:
                    st.markdown('<div class="agent-step">💬 Explainer<br>Agent</div>', unsafe_allow_html=True)

            # Run pipeline
            try:
                result = run_tax_analysis(parsed_docs, language=lang_code)
                progress.progress(80)
                status.markdown("**Step 5/5:** 📄 Generating report...")

                # Store in session state
                st.session_state["result"] = result
                st.session_state["parsed_docs"] = parsed_docs

                # Generate PDF
                report_path = "output/tax_report.pdf"
                try:
                    generate_tax_report(
                        tax_result=result["tax_result"],
                        income_summary=result["income_summary"],
                        deductions_found=result["deductions_found"],
                        missed_deductions=result["missed_deductions"],
                        explanation=result["explanation"],
                        recommendations=result["recommendations"],
                        output_path=report_path
                    )
                    st.session_state["report_path"] = report_path
                except Exception as e:
                    st.session_state["report_path"] = None

                progress.progress(100)
                status.markdown("✅ **Analysis Complete!**")

            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.info("Tip: Make sure your Groq API key is set correctly in the sidebar.")

    # ── Display Results ──────────────────────────────────────────────
    if "result" in st.session_state:
        result = st.session_state["result"]
        tax = result.get("tax_result", {})
        income = result.get("income_summary", {})
        new_r = tax.get("new_regime", {})
        old_r = tax.get("old_regime", {})
        rec = tax.get("recommendation", {})

        st.divider()
        st.subheader("📊 Your Tax Analysis Results")

        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">₹{income.get('total_income',0)/100000:.1f}L</div>
                <div class="metric-label">Gross Annual Income</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            best = rec.get("best_regime", "New Regime")
            best_data = new_r if best == "New Regime" else old_r
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">₹{best_data.get('tax',0)/1000:.1f}K</div>
                <div class="metric-label">Tax Payable ({best})</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            savings = rec.get("savings", 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:#000000">₹{savings/1000:.1f}K</div>
                <div class="metric-label">Savings by Best Regime</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            refund = best_data.get("refund_payable", 0)
            label = "Refund" if refund > 0 else "Tax Payable"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:#000000">₹{abs(refund)/1000:.1f}K</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Refund / Payable callout
        if refund > 0:
            st.markdown(f'<div class="refund-box">🎉 Great News! You are eligible for a TAX REFUND of ₹{abs(refund):,.0f}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="payable-box">⚠️ Additional Tax Payable: ₹{abs(refund):,.0f} — Pay before ITR deadline</div>',
                        unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Old vs New Regime comparison
        col_old, col_new = st.columns(2)
        best_regime = rec.get("best_regime", "")

        with col_old:
            badge = " 🏆 BEST" if best_regime == "Old Regime" else ""
            st.markdown(f"### 📋 Old Tax Regime{badge}")
            old_metrics = {
                "Standard Deduction": f"₹{old_r.get('standard_deduction', 50000):,.0f}",
                "HRA Exemption": f"₹{old_r.get('hra_exemption', 0):,.0f}",
                "80C Deductions": f"₹{old_r.get('80c_deduction', 0):,.0f}",
                "80D Deductions": f"₹{old_r.get('80d_deduction', 0):,.0f}",
                "Total Deductions": f"₹{old_r.get('total_deductions', 0):,.0f}",
                "Taxable Income": f"₹{old_r.get('taxable_income', 0):,.0f}",
                "Income Tax (incl. cess)": f"₹{old_r.get('tax', 0):,.0f}",
            }
            for k, v in old_metrics.items():
                st.markdown(f"**{k}:** {v}")

        with col_new:
            badge = " 🏆 BEST" if best_regime == "New Regime" else ""
            st.markdown(f"### 🆕 New Tax Regime{badge}")
            new_metrics = {
                "Standard Deduction": f"₹{new_r.get('standard_deduction', 75000):,.0f}",
                "HRA Exemption": "Not Applicable",
                "80C Deductions": "Not Applicable",
                "80D Deductions": "Not Applicable",
                "Total Deductions": f"₹{new_r.get('standard_deduction', 75000):,.0f}",
                "Taxable Income": f"₹{new_r.get('taxable_income', 0):,.0f}",
                "Income Tax (incl. cess)": f"₹{new_r.get('tax', 0):,.0f}",
            }
            for k, v in new_metrics.items():
                st.markdown(f"**{k}:** {v}")

        st.divider()

        # Missed deductions
        missed = result.get("missed_deductions", [])
        if missed:
            st.subheader("🔔 Deductions You May Have Missed")
            for m in missed:
                st.markdown(f'<div class="missed-deduction">⚠️ {m}</div>', unsafe_allow_html=True)

        st.divider()

        # AI Explanation
        st.subheader(f"🤖 AI Explanation ({language})")
        explanation = result.get("explanation", "")
        if explanation:
            st.info(explanation)
        else:
            st.warning("Add Groq API key to get AI explanations in Hindi/English.")

        # Recommendations
        st.subheader("✅ Your Action Plan")
        for rec_item in result.get("recommendations", []):
            st.markdown(f'<div class="recommendation">{rec_item}</div>', unsafe_allow_html=True)

        # Download Report
        st.divider()
        report_path = st.session_state.get("report_path")
        if report_path and Path(report_path).exists():
            with open(report_path, "rb") as f:
                st.download_button(
                    label="📥 Download Full Tax Report (PDF)",
                    data=f.read(),
                    file_name="tax_analysis_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )

# ══════════════════════════════════════════════════════════════════════
# TAB 2: Manual Entry
# ══════════════════════════════════════════════════════════════════════

with tab2:
    st.subheader("🧮 Enter Your Details Manually")
    st.info("Don't have PDFs? Enter your income and deduction details here directly.")

    with st.form("manual_tax_form"):
        st.markdown("#### 💰 Income Details")
        col1, col2 = st.columns(2)
        with col1:
            m_basic = st.number_input("Basic Salary (Annual ₹)", min_value=0, value=540000, step=10000)
            m_hra = st.number_input("HRA Received (Annual ₹)", min_value=0, value=216000, step=5000)
            m_da = st.number_input("Dearness Allowance (Annual ₹)", min_value=0, value=54000, step=5000)
        with col2:
            m_special = st.number_input("Special Allowance (Annual ₹)", min_value=0, value=108000, step=5000)
            m_interest = st.number_input("Savings Interest Income (₹)", min_value=0, value=3200, step=500)
            m_tds = st.number_input("TDS Already Deducted (₹)", min_value=0, value=72000, step=1000)

        st.markdown("#### 🏠 HRA Details")
        col3, col4 = st.columns(2)
        with col3:
            m_rent = st.number_input("Monthly Rent Paid (₹)", min_value=0, value=15000, step=500)
        with col4:
            m_city = st.selectbox("City Type", ["non-metro", "metro"])

        st.markdown("#### 📑 Deductions (80C, 80D, etc.)")
        col5, col6 = st.columns(2)
        with col5:
            m_pf = st.number_input("PF Contribution (Annual ₹)", min_value=0, value=64800, step=1000)
            m_lic = st.number_input("LIC Premium (₹)", min_value=0, value=25000, step=1000)
            m_ppf = st.number_input("PPF Deposit (₹)", min_value=0, value=0, step=5000)
            m_elss = st.number_input("ELSS Investment (₹)", min_value=0, value=0, step=5000)
        with col6:
            m_health_self = st.number_input("Health Insurance - Self (₹)", min_value=0, value=15000, step=1000)
            m_health_parents = st.number_input("Health Insurance - Parents (₹)", min_value=0, value=0, step=1000)
            m_nps = st.number_input("NPS Contribution 80CCD(1B) (₹)", min_value=0, value=0, step=5000)
            m_edu_loan = st.number_input("Education Loan Interest 80E (₹)", min_value=0, value=0, step=1000)

        submitted = st.form_submit_button("🧮 Calculate My Tax", type="primary", use_container_width=True)

    if submitted:
        from utils.tax_calculator import TaxableIncome, Deductions, compute_full_tax

        income_obj = TaxableIncome(
            basic_salary=m_basic, hra_received=m_hra, da=m_da,
            special_allowance=m_special, interest_income=m_interest, tds_deducted=m_tds
        )
        ded_obj = Deductions(
            pf_contribution=m_pf, lic_premium=m_lic, ppf=m_ppf,
            elss_mutual_fund=m_elss, health_insurance_self=m_health_self,
            health_insurance_parents=m_health_parents, nps_contribution=m_nps,
            education_loan_interest=m_edu_loan, rent_paid_monthly=m_rent, city_type=m_city
        )
        result = compute_full_tax(income_obj, ded_obj)
        new_r = result["new_regime"]
        old_r = result["old_regime"]
        rec = result["recommendation"]

        st.success(f"✅ Calculation complete! **{rec['best_regime']}** saves you ₹{rec['savings']:,.0f}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("New Regime Tax", f"₹{new_r['tax']:,.0f}",
                      delta=f"Refund ₹{new_r['refund_payable']:,.0f}" if new_r['refund_payable'] > 0
                      else f"Pay ₹{abs(new_r['refund_payable']):,.0f}")
        with col2:
            st.metric("Old Regime Tax", f"₹{old_r['tax']:,.0f}",
                      delta=f"Refund ₹{old_r['refund_payable']:,.0f}" if old_r['refund_payable'] > 0
                      else f"Pay ₹{abs(old_r['refund_payable']):,.0f}")
        with col3:
            st.metric("Best Choice", rec["best_regime"], delta=f"Saves ₹{rec['savings']:,.0f}")

        with st.expander("📊 Detailed Breakdown"):
            st.json(result)

# ══════════════════════════════════════════════════════════════════════
# TAB 3: Tax Guide
# ══════════════════════════════════════════════════════════════════════

with tab3:
    st.subheader("📚 Quick Tax Guide — FY 2023-24")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🆕 New Tax Regime Slabs
        | Income | Tax Rate |
        |--------|----------|
        | Up to ₹3L | 0% |
        | ₹3L – ₹7L | 5% |
        | ₹7L – ₹10L | 10% |
        | ₹10L – ₹12L | 15% |
        | ₹12L – ₹15L | 20% |
        | Above ₹15L | 30% |

        **Rebate u/s 87A:** No tax if income ≤ ₹7L
        **Standard Deduction:** ₹75,000
        """)

    with col2:
        st.markdown("""
        ### 📋 Old Tax Regime Slabs
        | Income | Tax Rate |
        |--------|----------|
        | Up to ₹2.5L | 0% |
        | ₹2.5L – ₹5L | 5% |
        | ₹5L – ₹10L | 20% |
        | Above ₹10L | 30% |

        **Rebate u/s 87A:** No tax if income ≤ ₹5L
        **Standard Deduction:** ₹50,000
        """)

    st.divider()
    st.markdown("""
    ### 💡 Key Deductions (Old Regime only)

    | Section | What Qualifies | Max Limit |
    |---------|---------------|-----------|
    | **80C** | PF, LIC, PPF, ELSS, Home Loan Principal | ₹1,50,000 |
    | **80D** | Health Insurance Premium | ₹25,000 (self) + ₹25,000 (parents) |
    | **HRA** | House Rent Allowance exemption | As per formula |
    | **80TTA** | Savings Bank Interest | ₹10,000 |
    | **80E** | Education Loan Interest | No limit |
    | **80CCD(1B)** | NPS Additional Contribution | ₹50,000 |
    | **80G** | Donations to recognized charities | 50%/100% of donation |

    ### 📅 Important Deadlines
    - **July 31, 2024** — ITR filing deadline (no audit cases)
    - **March 15, 2024** — Final advance tax installment
    - **June 15, July 15, Sept 15, Dec 15, March 15** — Advance tax due dates

    ### 🔗 Useful Links
    - [Income Tax Portal](https://www.incometax.gov.in)
    - [Tax Calculator (Official)](https://www.incometax.gov.in/iec/foportal/help/individual/return-applicable-1)
    - [Form 26AS (TDS view)](https://www.incometax.gov.in)
    """)

# ─── Footer ──────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("""
<div style='text-align:center; color:grey; font-size:0.8rem'>
    🧾 AI Tax Assistant | Built with LangGraph + Groq + Streamlit<br>
    ⚠️ For educational purposes only. Consult a CA before filing ITR.
</div>
""", unsafe_allow_html=True)
