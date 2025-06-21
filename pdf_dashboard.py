import streamlit as st
import pandas as pd
import pdfplumber
import io
import tempfile
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# -----------------------
# Database Configuration
# -----------------------
DB_USER = "root"
DB_PASSWORD = ""  # Add password if any
DB_HOST = "localhost"
DB_NAME = "etl_pdf"
TABLE_NAME = "invoice_data"

# -----------------------
# PDF Processing Functions
# -----------------------
def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def extract_tables_from_pdf(pdf_file):
    """Extract tables from uploaded PDF file (ETL style)"""
    try:
        dataframes = []
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                table = page.extract_table()
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df['page'] = page_num + 1
                    dataframes.append(df)
        
        if dataframes:
            return pd.concat(dataframes, ignore_index=True)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error extracting tables from PDF: {e}")
        return pd.DataFrame()

def transform_data(df):
    """Transform extracted data (from notebook)"""
    if df.empty:
        return df
    
    # Clean column names
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    df.fillna("N/A", inplace=True)
    return df

def load_to_mysql(df):
    """Load data to MySQL database"""
    try:
        engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
        df.to_sql(TABLE_NAME, con=engine, if_exists='replace', index=False)
        return True
    except Exception as e:
        st.error(f"Error loading to MySQL: {e}")
        return False

def load_data_from_mysql():
    """Load existing data from MySQL"""
    try:
        engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
        df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", con=engine)
        return df
    except Exception as e:
        st.warning(f"Could not load from database: {e}")
        return pd.DataFrame()

def clean_text(text):
    """Clean and preprocess text"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
    return text.strip()

def extract_keywords(text, top_n=10):
    """Extract keywords from text"""
    if not text:
        return []
    
    # Tokenize and clean
    tokens = word_tokenize(text.lower())
    
    # Remove stopwords and short words
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.isalnum() and word not in stop_words and len(word) > 2]
    
    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    
    # Count frequencies
    word_freq = Counter(tokens)
    return word_freq.most_common(top_n)

def generate_summary(text, max_sentences=5):
    """Generate a simple extractive summary"""
    if not text:
        return ""
    
    # Split into sentences
    sentences = sent_tokenize(text)
    
    # Calculate sentence scores based on word frequency
    word_freq = Counter(word_tokenize(text.lower()))
    
    sentence_scores = {}
    for sentence in sentences:
        words = word_tokenize(sentence.lower())
        score = sum(word_freq[word] for word in words if word.isalnum())
        sentence_scores[sentence] = score
    
    # Get top sentences
    top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:max_sentences]
    summary_sentences = [sentence for sentence, score in sorted(top_sentences, key=lambda x: sentences.index(x[0]))]
    
    return ' '.join(summary_sentences)

def analyze_document_stats(text):
    """Analyze document statistics"""
    if not text:
        return {}
    
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    paragraphs = text.split('\n\n')
    
    return {
        'characters': len(text),
        'words': len(words),
        'sentences': len(sentences),
        'paragraphs': len(paragraphs),
        'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
        'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0
    }

def analyze_invoice_data(df):
    """Analyze invoice-specific data"""
    if df.empty:
        return {}
    
    analysis = {}
    
    # Try to find numeric columns for analysis
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if numeric_cols:
        analysis['numeric_columns'] = numeric_cols
        for col in numeric_cols:
            analysis[f'{col}_sum'] = df[col].sum()
            analysis[f'{col}_avg'] = df[col].mean()
            analysis[f'{col}_min'] = df[col].min()
            analysis[f'{col}_max'] = df[col].max()
    
    # Count unique values in categorical columns
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    for col in categorical_cols:
        analysis[f'{col}_unique_count'] = df[col].nunique()
    
    analysis['total_rows'] = len(df)
    analysis['total_columns'] = len(df.columns)
    
    return analysis

# -----------------------
# Streamlit App UI
# -----------------------
def main():
    st.set_page_config(
        page_title="📄 PDF Invoice Summarizer Dashboard",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">📄 PDF Invoice Summarizer Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Summary settings
        st.subheader("📝 Summary Settings")
        max_sentences = st.slider("Maximum sentences in summary", 3, 10, 5)
        top_keywords = st.slider("Number of keywords to extract", 5, 20, 10)
        
        # Analysis options
        st.subheader("📊 Analysis Options")
        show_keywords = st.checkbox("Show keyword analysis", value=True)
        show_stats = st.checkbox("Show document statistics", value=True)
        show_tables = st.checkbox("Extract and show tables", value=True)
        save_to_db = st.checkbox("Save extracted data to database", value=False)
        
        # Database connection test
        st.subheader("🗄️ Database Status")
        try:
            engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
            with engine.connect() as conn:
                st.success("✅ Database connected")
        except Exception as e:
            st.error(f"❌ Database connection failed: {e}")
        
        st.markdown("---")
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. Upload a PDF file (invoice or document)
        2. Wait for processing to complete
        3. View extracted text, summary, and analysis
        4. Optionally save to database
        5. Download results if needed
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📤 Upload PDF")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a PDF file to extract text and generate summary"
        )
        
        if uploaded_file is not None:
            # Show file info
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.2f} KB",
                "Upload time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            st.success("✅ File uploaded successfully!")
            
            # Process the PDF
            with st.spinner("🔄 Processing PDF..."):
                # Extract text
                text = extract_text_from_pdf(uploaded_file)
                
                if text:
                    # Clean text
                    cleaned_text = clean_text(text)
                    
                    # Generate summary
                    summary = generate_summary(cleaned_text, max_sentences)
                    
                    # Extract keywords
                    keywords = extract_keywords(cleaned_text, top_keywords)
                    
                    # Analyze document stats
                    stats = analyze_document_stats(cleaned_text)
                    
                    # Extract tables if requested
                    tables_df = pd.DataFrame()
                    if show_tables:
                        tables_df = extract_tables_from_pdf(uploaded_file)
                    
                    # Transform data if tables found
                    if not tables_df.empty:
                        tables_df = transform_data(tables_df)
                        
                        # Save to database if requested
                        if save_to_db:
                            if load_to_mysql(tables_df):
                                st.success("✅ Data saved to database!")
                    
                    # Store results in session state
                    st.session_state['pdf_text'] = cleaned_text
                    st.session_state['summary'] = summary
                    st.session_state['keywords'] = keywords
                    st.session_state['stats'] = stats
                    st.session_state['tables_df'] = tables_df
                    st.session_state['file_details'] = file_details
                    
                    st.success("✅ PDF processed successfully!")
                else:
                    st.error("❌ Could not extract text from PDF. Please try another file.")
    
    with col2:
        st.subheader("📋 File Information")
        if 'file_details' in st.session_state:
            for key, value in st.session_state['file_details'].items():
                st.metric(key, value)
    
    # Display results
    if 'pdf_text' in st.session_state:
        st.markdown("---")
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📄 Extracted Text", 
            "📝 Summary", 
            "🔍 Keywords", 
            "📊 Statistics", 
            "📋 Tables", 
            "🗄️ Database"
        ])
        
        with tab1:
            st.subheader("📄 Extracted Text")
            st.text_area(
                "Full extracted text:",
                value=st.session_state['pdf_text'],
                height=400,
                help="Complete text extracted from the PDF"
            )
            
            # Download button for text
            text_download = st.session_state['pdf_text'].encode('utf-8')
            st.download_button(
                label="📥 Download Text",
                data=text_download,
                file_name=f"{uploaded_file.name.replace('.pdf', '')}_extracted_text.txt",
                mime="text/plain"
            )
        
        with tab2:
            st.subheader("📝 Generated Summary")
            st.write(st.session_state['summary'])
            
            # Download button for summary
            summary_download = st.session_state['summary'].encode('utf-8')
            st.download_button(
                label="📥 Download Summary",
                data=summary_download,
                file_name=f"{uploaded_file.name.replace('.pdf', '')}_summary.txt",
                mime="text/plain"
            )
        
        with tab3:
            if show_keywords and st.session_state['keywords']:
                st.subheader("🔍 Keyword Analysis")
                
                # Create keyword visualization
                keywords_df = pd.DataFrame(st.session_state['keywords'], columns=['Keyword', 'Frequency'])
                
                # Bar chart
                fig = px.bar(
                    keywords_df, 
                    x='Frequency', 
                    y='Keyword',
                    orientation='h',
                    title="Top Keywords by Frequency",
                    color='Frequency',
                    color_continuous_scale='viridis'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Keyword table
                st.subheader("📋 Keyword Details")
                st.dataframe(keywords_df, use_container_width=True)
        
        with tab4:
            if show_stats and st.session_state['stats']:
                st.subheader("📊 Document Statistics")
                
                stats = st.session_state['stats']
                
                # Create metrics display
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📝 Characters", f"{stats['characters']:,}")
                    st.metric("📊 Sentences", f"{stats['sentences']:,}")
                
                with col2:
                    st.metric("📖 Words", f"{stats['words']:,}")
                    st.metric("📄 Paragraphs", f"{stats['paragraphs']:,}")
                
                with col3:
                    st.metric("📏 Avg Sentence Length", f"{stats['avg_sentence_length']:.1f} words")
                    st.metric("📏 Avg Word Length", f"{stats['avg_word_length']:.1f} characters")
                
                # Create word length distribution
                if st.session_state['pdf_text']:
                    words = word_tokenize(st.session_state['pdf_text'])
                    word_lengths = [len(word) for word in words if word.isalnum()]
                    
                    if word_lengths:
                        fig = px.histogram(
                            x=word_lengths,
                            nbins=20,
                            title="Word Length Distribution",
                            labels={'x': 'Word Length', 'y': 'Frequency'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        with tab5:
            if show_tables and not st.session_state['tables_df'].empty:
                st.subheader("📋 Extracted Tables")
                
                tables_df = st.session_state['tables_df']
                st.dataframe(tables_df, use_container_width=True)
                
                # Analyze invoice data
                invoice_analysis = analyze_invoice_data(tables_df)
                if invoice_analysis:
                    st.subheader("📊 Invoice Data Analysis")
                    
                    # Display key metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Rows", invoice_analysis.get('total_rows', 0))
                    with col2:
                        st.metric("Total Columns", invoice_analysis.get('total_columns', 0))
                    with col3:
                        if 'numeric_columns' in invoice_analysis:
                            st.metric("Numeric Columns", len(invoice_analysis['numeric_columns']))
                
                # Download button for tables
                csv = tables_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Table Data",
                    data=csv,
                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_extracted_data.csv",
                    mime="text/csv"
                )
            else:
                st.info("No tables found in the PDF or table extraction is disabled.")
        
        with tab6:
            st.subheader("🗄️ Database Operations")
            
            # Load existing data
            if st.button("🔄 Load Data from Database"):
                with st.spinner("Loading data from database..."):
                    db_data = load_data_from_mysql()
                    if not db_data.empty:
                        st.session_state['db_data'] = db_data
                        st.success(f"✅ Loaded {len(db_data)} records from database")
                    else:
                        st.warning("No data found in database")
            
            # Display database data
            if 'db_data' in st.session_state and not st.session_state['db_data'].empty:
                st.subheader("📋 Database Records")
                st.dataframe(st.session_state['db_data'], use_container_width=True)
                
                # Database statistics
                db_stats = analyze_invoice_data(st.session_state['db_data'])
                if db_stats:
                    st.subheader("📊 Database Statistics")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Records", db_stats.get('total_rows', 0))
                    with col2:
                        st.metric("Total Fields", db_stats.get('total_columns', 0))
                    with col3:
                        if 'numeric_columns' in db_stats:
                            st.metric("Numeric Fields", len(db_stats['numeric_columns']))
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <p>📄 PDF Invoice Summarizer Dashboard | Built with Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
