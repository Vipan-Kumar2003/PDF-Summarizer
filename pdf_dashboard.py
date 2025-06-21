import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# -----------------------
# DB Configuration
# -----------------------
DB_USER = "root"
DB_PASSWORD = ""  # Add password if any
DB_HOST = "localhost"
DB_NAME = "etl_pdf"
TABLE_NAME = "invoice_data"

# -----------------------
# Load data from MySQL
# -----------------------
@st.cache_data
def load_data():
    try:
        engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
        df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", con=engine)
        return df
    except Exception as e:
        st.error(f"Error loading data from Database: {e}")
        return pd.DataFrame()

# -----------------------
# Streamlit App UI
# -----------------------
def main():
    st.set_page_config(page_title="📄 Invoice Dashboard", layout="wide")
    st.title("📄 Extracted Invoice Dashboard")

    df = load_data()
    if df.empty:
        st.warning("No data available. Please run the ETL script first.")
        return

    # Show raw data
    st.subheader("🧾 Full Invoice Table")
    st.dataframe(df, use_container_width=True)

    # Filter by item or price
    with st.expander("🔍 Filter"):
        search = st.text_input("Search by Item Name").lower()
        if search:
            df = df[df['item_description'].str.lower().str.contains(search)]

    # Show summary
  # Show summary
    st.subheader("📊 Summary Statistics")
    df['total'] = pd.to_numeric(df['total'], errors='coerce')  # Convert to float
    total_invoice = df['total'].sum()
    st.metric("💰 Total Invoice Amount", f"₹ {total_invoice:,.2f}")
    st.metric("🛍️ Items Listed", len(df))

if __name__ == "__main__":
    main()
