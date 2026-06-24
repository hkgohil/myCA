"""
Generate a professional Tax Summary PDF report
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from pathlib import Path


def generate_tax_report(tax_result: dict, income_summary: dict,
                         deductions_found: dict, missed_deductions: list,
                         explanation: str, recommendations: list,
                         output_path: str = "output/tax_report.pdf"):
    """Generate a complete tax analysis PDF report"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                             topMargin=0.5*inch, bottomMargin=0.5*inch,
                             leftMargin=0.6*inch, rightMargin=0.6*inch)

    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle('MainTitle', fontSize=20, textColor=colors.HexColor('#1a3a5c'),
                                  spaceAfter=4, fontName='Helvetica-Bold', alignment=TA_CENTER)
    subtitle_style = ParagraphStyle('Subtitle', fontSize=10, textColor=colors.grey,
                                     spaceAfter=2, alignment=TA_CENTER)
    section_style = ParagraphStyle('Section', fontSize=12, textColor=colors.HexColor('#1a3a5c'),
                                    spaceAfter=6, fontName='Helvetica-Bold')
    body_style = ParagraphStyle('Body', fontSize=9, textColor=colors.HexColor('#333333'),
                                 spaceAfter=4, leading=14)
    green_style = ParagraphStyle('Green', fontSize=10, textColor=colors.HexColor('#27ae60'),
                                  fontName='Helvetica-Bold')
    red_style = ParagraphStyle('Red', fontSize=10, textColor=colors.HexColor('#c0392b'),
                                fontName='Helvetica-Bold')

    # ── Header ──────────────────────────────────────────
    story.append(Paragraph("🇮🇳 AI Tax Assistant", title_style))
    story.append(Paragraph(f"Tax Analysis Report — FY 2023-24 | Generated: {datetime.now().strftime('%d %b %Y %I:%M %p')}",
                            subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a3a5c')))
    story.append(Spacer(1, 0.15 * inch))

    # ── Income Summary ───────────────────────────────────
    story.append(Paragraph("📊 Income Summary", section_style))

    income_data = [
        ["Income Component", "Annual Amount (₹)"],
        ["Basic Salary", f"₹{income_summary.get('basic_salary', 0):,.2f}"],
        ["HRA Received", f"₹{income_summary.get('hra_received', 0):,.2f}"],
        ["Dearness Allowance (DA)", f"₹{income_summary.get('da', 0):,.2f}"],
        ["Special Allowance", f"₹{income_summary.get('special_allowance', 0):,.2f}"],
        ["Interest Income", f"₹{income_summary.get('interest_income', 0):,.2f}"],
        ["Other Income", f"₹{income_summary.get('other_income', 0):,.2f}"],
        ["GROSS TOTAL INCOME", f"₹{income_summary.get('total_income', 0):,.2f}"],
    ]

    inc_table = Table(income_data, colWidths=[4*inch, 3*inch])
    inc_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a3a5c')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e8f4f8')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(inc_table)
    story.append(Spacer(1, 0.15 * inch))

    # ── Tax Comparison ───────────────────────────────────
    story.append(Paragraph("⚖️ Old Regime vs New Regime Comparison", section_style))

    new_r = tax_result.get("new_regime", {})
    old_r = tax_result.get("old_regime", {})
    rec = tax_result.get("recommendation", {})

    comparison_data = [
        ["", "Old Tax Regime", "New Tax Regime"],
        ["Standard Deduction", f"₹{old_r.get('standard_deduction', 50000):,.0f}", f"₹{new_r.get('standard_deduction', 75000):,.0f}"],
        ["HRA Exemption", f"₹{old_r.get('hra_exemption', 0):,.0f}", "Not Applicable"],
        ["80C Deductions", f"₹{old_r.get('80c_deduction', 0):,.0f}", "Not Applicable"],
        ["80D Deductions", f"₹{old_r.get('80d_deduction', 0):,.0f}", "Not Applicable"],
        ["Total Deductions", f"₹{old_r.get('total_deductions', 0):,.0f}", f"₹{new_r.get('standard_deduction', 75000):,.0f}"],
        ["Taxable Income", f"₹{old_r.get('taxable_income', 0):,.0f}", f"₹{new_r.get('taxable_income', 0):,.0f}"],
        ["Income Tax", f"₹{old_r.get('tax', 0):,.0f}", f"₹{new_r.get('tax', 0):,.0f}"],
        ["TDS Already Paid", f"₹{old_r.get('tds_paid', 0):,.0f}", f"₹{new_r.get('tds_paid', 0):,.0f}"],
        ["Refund (+) / Payable (-)",
         f"{'+ ₹' if old_r.get('refund_payable',0)>0 else '- ₹'}{abs(old_r.get('refund_payable',0)):,.0f}",
         f"{'+ ₹' if new_r.get('refund_payable',0)>0 else '- ₹'}{abs(new_r.get('refund_payable',0)):,.0f}"],
    ]

    # Highlight best regime column
    best_col = 2 if rec.get("best_regime") == "New Regime" else 1

    cmp_table = Table(comparison_data, colWidths=[2.8*inch, 2.1*inch, 2.1*inch])
    cmp_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a3a5c')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (best_col,0), (best_col,-1), colors.HexColor('#d5e8d4')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#fff3cd')),
        ('ROWBACKGROUNDS', (0,1), (0,-2), [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(cmp_table)
    story.append(Spacer(1, 0.1 * inch))

    # Best regime callout
    savings = rec.get('savings', 0)
    best_regime = rec.get('best_regime', '')
    story.append(Paragraph(
        f"🏆 RECOMMENDATION: Choose <b>{best_regime}</b> — Save ₹{savings:,.0f} in taxes!",
        ParagraphStyle('Rec', fontSize=11, textColor=colors.HexColor('#27ae60'),
                       fontName='Helvetica-Bold', borderColor=colors.HexColor('#27ae60'),
                       borderWidth=1, borderPadding=8, backColor=colors.HexColor('#f0fff4'))
    ))
    story.append(Spacer(1, 0.15 * inch))

    # ── Missed Deductions ────────────────────────────────
    if missed_deductions:
        story.append(Paragraph("🔔 Deductions You May Have Missed", section_style))
        missed_data = [["#", "Missed Deduction / Opportunity"]]
        for i, m in enumerate(missed_deductions, 1):
            missed_data.append([str(i), m])

        m_table = Table(missed_data, colWidths=[0.4*inch, 6.6*inch])
        m_table.setStyle(TableStyle([
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#c0392b')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#fff5f5'), colors.white]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(m_table)
        story.append(Spacer(1, 0.15 * inch))

    # ── AI Explanation ───────────────────────────────────
    story.append(Paragraph("🤖 AI Tax Advisor Says", section_style))
    story.append(Paragraph(explanation, body_style))
    story.append(Spacer(1, 0.15 * inch))

    # ── Action Items ─────────────────────────────────────
    if recommendations:
        story.append(Paragraph("✅ Your Action Plan", section_style))
        for rec_item in recommendations:
            story.append(Paragraph(f"• {rec_item}", body_style))
        story.append(Spacer(1, 0.1 * inch))

    # ── Disclaimer ───────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Spacer(1, 0.05 * inch))
    story.append(Paragraph(
        "⚠️ Disclaimer: This report is generated by AI for informational purposes only. "
        "Please consult a qualified Chartered Accountant (CA) before filing your ITR. "
        "Tax laws may change — always verify with official Income Tax India website (incometax.gov.in).",
        ParagraphStyle('Disclaimer', fontSize=7, textColor=colors.grey, leading=10)
    ))

    doc.build(story)
    print(f"✅ Tax report generated: {output_path}")
    return output_path
