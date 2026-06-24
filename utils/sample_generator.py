"""
Generate realistic dummy documents for testing
Creates: Bank Statements, Form 16, Salary Slips as PDFs
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from pathlib import Path
import random


def generate_salary_slip(output_path: str, month: str = "March 2024",
                          employee_name: str = "Rahul Sharma",
                          basic: float = 45000):
    """Generate a realistic salary slip PDF"""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=18, textColor=colors.HexColor('#1a3a5c'),
                                  spaceAfter=6)
    header_style = ParagraphStyle('Header', parent=styles['Normal'],
                                   fontSize=10, textColor=colors.grey)

    story.append(Paragraph("TechCorp Solutions Pvt. Ltd.", title_style))
    story.append(Paragraph("123 MG Road, Bengaluru - 560001 | CIN: U72900KA2015PTC000001", header_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"<b>SALARY SLIP - {month.upper()}</b>",
                            ParagraphStyle('SlipTitle', fontSize=13, alignment=TA_CENTER,
                                           textColor=colors.HexColor('#c0392b'))))
    story.append(Spacer(1, 0.15 * inch))

    # Employee details table
    hra = basic * 0.40
    da = basic * 0.10
    special_allowance = basic * 0.20
    gross = basic + hra + da + special_allowance
    pf = basic * 0.12
    professional_tax = 200
    tds = round(gross * 0.08)
    net = gross - pf - professional_tax - tds

    emp_data = [
        ["Employee Name:", employee_name, "Employee ID:", "TC-2089"],
        ["PAN:", "ABCPS1234D", "Department:", "Engineering"],
        ["Designation:", "Software Engineer", "Bank A/C:", "XXXX XXXX 4521"],
        ["Pay Period:", month, "Working Days:", "26 / 26"],
    ]

    emp_table = Table(emp_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2*inch])
    emp_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (0,-1), colors.grey),
        ('TEXTCOLOR', (2,0), (2,-1), colors.grey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(emp_table)
    story.append(Spacer(1, 0.2 * inch))

    # Earnings and Deductions
    earnings_data = [
        ["EARNINGS", "Amount (₹)", "DEDUCTIONS", "Amount (₹)"],
        ["Basic Salary", f"{basic:,.2f}", "Provident Fund (12%)", f"{pf:,.2f}"],
        ["HRA (40% of Basic)", f"{hra:,.2f}", "Professional Tax", f"{professional_tax:,.2f}"],
        ["Dearness Allowance", f"{da:,.2f}", "TDS (Income Tax)", f"{tds:,.2f}"],
        ["Special Allowance", f"{special_allowance:,.2f}", "", ""],
        ["GROSS SALARY", f"{gross:,.2f}", "TOTAL DEDUCTIONS", f"{pf+professional_tax+tds:,.2f}"],
        ["", "", "NET SALARY", f"{net:,.2f}"],
    ]

    sal_table = Table(earnings_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch, 1.5*inch])
    sal_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a3a5c')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#e8f4f8')),
        ('BACKGROUND', (2,6), (-1,6), colors.HexColor('#d5e8d4')),
        ('FONTNAME', (0,5), (-1,6), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('ALIGN', (3,0), (3,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(sal_table)
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        f"<i>Net Salary in Words: {int(net):,} Rupees Only</i>",
        ParagraphStyle('Note', fontSize=9, textColor=colors.grey)
    ))

    doc.build(story)
    print(f"✅ Salary Slip generated: {output_path}")


def generate_form16(output_path: str, employee_name: str = "Rahul Sharma",
                     annual_salary: float = 720000):
    """Generate a realistic Form 16 PDF"""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=16, textColor=colors.HexColor('#1a3a5c'))

    story.append(Paragraph("FORM 16", title_style))
    story.append(Paragraph("Certificate of Tax Deducted at Source from Salary", styles['Normal']))
    story.append(Paragraph("[Under Section 203 of the Income-tax Act, 1961]", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    basic = annual_salary * 0.50
    hra = annual_salary * 0.20
    da = annual_salary * 0.05
    special = annual_salary * 0.10
    pf = basic * 0.12
    gross = annual_salary
    tds = round(annual_salary * 0.10)

    header_data = [
        ["Name of Employer:", "TechCorp Solutions Pvt. Ltd.", "TAN:", "BLRS12345A"],
        ["Address:", "123 MG Road, Bengaluru - 560001", "PAN of Employer:", "AABCT1234C"],
        ["Name of Employee:", employee_name, "PAN of Employee:", "ABCPS1234D"],
        ["Assessment Year:", "2024-25", "Financial Year:", "2023-24"],
    ]

    h_table = Table(header_data, colWidths=[1.8*inch, 2.8*inch, 1.5*inch, 1.9*inch])
    h_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (0,-1), colors.grey),
        ('TEXTCOLOR', (2,0), (2,-1), colors.grey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(h_table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("<b>PART A — Tax Deducted and Deposited</b>",
                            ParagraphStyle('Sec', fontSize=11, textColor=colors.HexColor('#c0392b'))))
    story.append(Spacer(1, 0.1 * inch))

    part_a = [
        ["Quarter", "Amount Credited (₹)", "TDS Deducted (₹)", "TDS Deposited (₹)"],
        ["Q1 (Apr-Jun)", f"{annual_salary/4:,.2f}", f"{tds/4:,.2f}", f"{tds/4:,.2f}"],
        ["Q2 (Jul-Sep)", f"{annual_salary/4:,.2f}", f"{tds/4:,.2f}", f"{tds/4:,.2f}"],
        ["Q3 (Oct-Dec)", f"{annual_salary/4:,.2f}", f"{tds/4:,.2f}", f"{tds/4:,.2f}"],
        ["Q4 (Jan-Mar)", f"{annual_salary/4:,.2f}", f"{tds/4:,.2f}", f"{tds/4:,.2f}"],
        ["TOTAL", f"{annual_salary:,.2f}", f"{tds:,.2f}", f"{tds:,.2f}"],
    ]

    a_table = Table(part_a, colWidths=[1.5*inch, 2*inch, 2*inch, 2*inch])
    a_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a3a5c')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e8f4f8')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(a_table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("<b>PART B — Salary Details</b>",
                            ParagraphStyle('Sec', fontSize=11, textColor=colors.HexColor('#c0392b'))))
    story.append(Spacer(1, 0.1 * inch))

    part_b = [
        ["Component", "Amount (₹)"],
        ["Basic Salary", f"{basic:,.2f}"],
        ["House Rent Allowance (HRA)", f"{hra:,.2f}"],
        ["Dearness Allowance (DA)", f"{da:,.2f}"],
        ["Special Allowance", f"{special:,.2f}"],
        ["Gross Salary", f"{gross:,.2f}"],
        ["Provident Fund Contribution (Employee)", f"{pf:,.2f}"],
        ["Tax Deducted at Source (TDS)", f"{tds:,.2f}"],
    ]

    b_table = Table(part_b, colWidths=[4*inch, 3*inch])
    b_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a3a5c')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(b_table)
    doc.build(story)
    print(f"✅ Form 16 generated: {output_path}")


def generate_bank_statement(output_path: str, account_holder: str = "Rahul Sharma",
                              monthly_salary: float = 62000):
    """Generate a realistic bank statement PDF"""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=16, textColor=colors.HexColor('#1a3a5c'))

    story.append(Paragraph("HDFC Bank", title_style))
    story.append(Paragraph("Account Statement — April 2023 to March 2024", styles['Normal']))
    story.append(Spacer(1, 0.15 * inch))

    acc_data = [
        ["Account Holder:", account_holder, "Account No.:", "XXXX XXXX 4521"],
        ["Branch:", "Koramangala, Bengaluru", "IFSC:", "HDFC0001234"],
        ["Account Type:", "Savings Account", "Period:", "01-Apr-2023 to 31-Mar-2024"],
    ]

    acc_table = Table(acc_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2*inch])
    acc_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (0,-1), colors.grey),
        ('TEXTCOLOR', (2,0), (2,-1), colors.grey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(acc_table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("<b>TRANSACTION DETAILS</b>",
                            ParagraphStyle('Sec', fontSize=11, textColor=colors.HexColor('#1a3a5c'))))
    story.append(Spacer(1, 0.1 * inch))

    months = ["Apr 2023", "May 2023", "Jun 2023", "Jul 2023", "Aug 2023", "Sep 2023",
              "Oct 2023", "Nov 2023", "Dec 2023", "Jan 2024", "Feb 2024", "Mar 2024"]

    txn_data = [["Date", "Description", "Type", "Amount (₹)", "Balance (₹)"]]
    balance = 50000

    for i, month in enumerate(months):
        # Salary credit
        balance += monthly_salary
        txn_data.append([
            f"01 {month}",
            "NEFT CR - TECHCORP SOLUTIONS SALARY",
            "CR",
            f"{monthly_salary:,.2f}",
            f"{balance:,.2f}"
        ])
        # Rent debit
        rent = 18000
        balance -= rent
        txn_data.append([
            f"03 {month}",
            "UPI - Rent Payment",
            "DR",
            f"{rent:,.2f}",
            f"{balance:,.2f}"
        ])
        # Misc expenses
        misc = random.randint(8000, 15000)
        balance -= misc
        txn_data.append([
            f"15 {month}",
            "UPI/DEBIT - Monthly Expenses",
            "DR",
            f"{misc:,.2f}",
            f"{balance:,.2f}"
        ])

    # Add savings interest at end
    interest = 3200
    balance += interest
    txn_data.append(["31 Mar 2024", "INT CR - Savings Interest Q4", "CR", f"{interest:,.2f}", f"{balance:,.2f}"])

    txn_table = Table(txn_data, colWidths=[1*inch, 2.8*inch, 0.6*inch, 1.2*inch, 1.4*inch])
    txn_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a3a5c')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('TEXTCOLOR', (2,1), (2,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.3, colors.lightgrey),
        ('ALIGN', (3,0), (4,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))

    # Color CR/DR cells
    for row_idx, row in enumerate(txn_data[1:], start=1):
        if len(row) > 2:
            if row[2] == "CR":
                txn_table.setStyle(TableStyle([
                    ('BACKGROUND', (2,row_idx), (2,row_idx), colors.HexColor('#27ae60')),
                ]))
            else:
                txn_table.setStyle(TableStyle([
                    ('BACKGROUND', (2,row_idx), (2,row_idx), colors.HexColor('#c0392b')),
                ]))

    story.append(txn_table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        f"<b>Total Salary Credited: ₹{monthly_salary*12:,.2f} | Interest Earned: ₹{interest:,.2f}</b>",
        ParagraphStyle('Summary', fontSize=10, textColor=colors.HexColor('#1a3a5c'))
    ))

    doc.build(story)
    print(f"✅ Bank Statement generated: {output_path}")


def generate_all_samples(output_dir: str = "data/samples"):
    """Generate all sample documents"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print("\n📄 Generating sample documents...")
    generate_salary_slip(f"{output_dir}/salary_slip_march_2024.pdf",
                          month="March 2024", employee_name="Rahul Sharma", basic=45000)
    generate_form16(f"{output_dir}/form16_2023_24.pdf",
                     employee_name="Rahul Sharma", annual_salary=720000)
    generate_bank_statement(f"{output_dir}/bank_statement_hdfc.pdf",
                             account_holder="Rahul Sharma", monthly_salary=62000)
    print("\n✅ All sample documents generated in:", output_dir)


if __name__ == "__main__":
    generate_all_samples()
