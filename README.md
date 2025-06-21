<h1 align="center">📄 PDF Summarizer</h1>

<p align="center">
  Extract 📤, Transform 🔧, Load 💾 & Visualize 📊 tabular data from PDF invoices – using Python + MySQL + Streamlit.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/streamlit-dashboard-success?style=flat-square&logo=streamlit&color=ff4b4b" />
  <img src="https://img.shields.io/badge/mysql-database-blue?style=flat-square&logo=mysql" />
  <img src="https://img.shields.io/badge/python-etl-yellow?style=flat-square&logo=python" />
</p>

---

## 🚀 About the Project

`PDF Summarizer` is an end-to-end ETL + Dashboard pipeline that:

✅ **Extracts** tabular data from invoice-style PDFs  
✅ **Cleans & Transforms** it using `pandas`  
✅ **Loads** it into a `MySQL` (WAMP) database  
✅ **Displays** it beautifully using a `Streamlit` dashboard

Use it for:
- Invoice processing 💼  
- Tabular PDF summarization 📊  
- Automated invoice analytics 📄  

---

## 🧠 Tech Stack

| 💻 Tool        | 🔧 Purpose                |
|---------------|---------------------------|
| Python        | Core logic and scripting  |
| pdfplumber    | Extracting tables from PDF|
| pandas        | Data cleaning & analysis  |
| SQLAlchemy    | MySQL connectivity        |
| pymysql       | MySQL driver              |
| Streamlit     | Frontend dashboard UI     |
| MySQL (WAMP)  | Database server           |

---

## 📂 Project Structure
pdf_summarizer/
├── detailed_invoice.pdf ← sample invoice file
├── extract_invoice_etl.py ← ETL pipeline script
├── pdf_dashboard.py ← Streamlit dashboard
├── requirements.txt ← Python dependencies
└── README.md ← this file



---

## 🛠️ How to Run Locally

### 🔌 Prerequisites
* Python 3.x  
* WAMP Server running  
* A MySQL database named **`etl_pdf`**

---

### 1️⃣ Clone the Repo

```bash
git clone https://github.com/yourusername/pdf-summarizer.git
cd pdf-summarizer


