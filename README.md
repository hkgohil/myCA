# 🧾 AI Tax Filing Assistant — India
### An Agentic AI System for Indian Taxpayers (FY 2023-24)

An intelligent multi-agent system that acts like a personal Chartered Accountant (CA). Powered by **LangGraph**, **Groq (Llama 3)**, and **Streamlit**.

---

## 🎯 Features

- 📄 **Automated Document Parsing**: Reads Form 16, Bank Statements, and Salary Slips (PDFs).
- 🤖 **Multi-Agent Pipeline**: 4 specialized AI Agents process financial data sequentially.
- 💰 **Smart Tax Calculation**: Computes tax under both Old and New Regimes to find the best savings.
- 🔍 **Deduction Discovery**: Proactively identifies missed deductions using LLMs.
- 🗣️ **Multilingual Explanations**: Explains tax breakdowns in plain English or Hindi.
- 📥 **Professional Reports**: Generates downloadable PDF tax reports.

---

## 🏗️ Architecture

```text
User Uploads PDFs
      ↓
Document Parser (PyMuPDF + Regex)
      ↓
┌─────────────────────────────────────────────┐
│             LangGraph Pipeline              │
│                                             │
│ 1. Income Aggregator: Sums all income       │
│                      ↓                      │
│ 2. Deduction Finder: LLM spots missing deds │
│                      ↓                      │
│ 3. Tax Calculator: Computes tax regimes     │
│                      ↓                      │
│ 4. Explainer: Translates logic to user      │
└─────────────────────────────────────────────┘
      ↓
Streamlit Dashboard + PDF Report
```

---

## 🔧 Tech Stack

| Component | Technology | Description |
|-----------|-----------|-------------|
| **Agent Framework** | LangGraph | Multi-agent orchestration with state management |
| **LLM** | Groq (Llama 3) | Fast, accurate, and cost-effective inference |
| **PDF Extraction** | PyMuPDF | Robust document text extraction |
| **Tax Logic** | Python | Standardized Indian tax slab calculations |
| **Frontend UI** | Streamlit | Responsive and interactive dashboard |
| **PDF Generation** | ReportLab | High-quality downloadable tax reports |

---

## 🚀 Quick Setup

1. **Clone & Install Dependencies:**
   ```bash
   git clone https://github.com/hkgohil/myCA.git
   cd myCA
   python -m venv venv
   venv\Scripts\activate  # Use source venv/bin/activate on Mac/Linux
   pip install -r requirements.txt
   ```

2. **Configure API Keys:**
   Create a `.env` file in the root directory and add your free Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

---

## 🔜 Future Roadmap

- [ ] OCR support for scanned/image PDFs using Tesseract.
- [ ] Vector Database (ChromaDB) to store and compare past returns.
- [ ] Auto-fill export for official ITR forms.
- [ ] Support for freelancer income (44ADA presumptive taxation).
- [ ] Capital gains calculation integration (Stocks, Mutual Funds).

---

<p align="center">
  <i>Disclaimer: This tool is for educational and portfolio purposes only. Always consult a qualified CA before filing your ITR.</i><br>
  <b>Built with ❤️ for India</b>
</p>
