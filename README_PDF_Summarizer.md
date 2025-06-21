# 📄 PDF Invoice Summarizer Dashboard

A powerful Streamlit-based web application that combines PDF text extraction, summarization, and ETL (Extract, Transform, Load) capabilities for invoice processing and document analysis.

## ✨ Features

- **📤 PDF Upload**: Drag and drop or browse to upload PDF files
- **📄 Text Extraction**: Extract all text content from PDF documents
- **📝 Automatic Summarization**: Generate intelligent summaries using extractive summarization
- **🔍 Keyword Analysis**: Extract and visualize the most important keywords
- **📊 Document Statistics**: Analyze document metrics (word count, sentence count, etc.)
- **📋 Table Extraction**: Extract and display tables found in PDFs (ETL-style)
- **🗄️ Database Integration**: Save extracted data to MySQL database
- **📥 Download Results**: Download extracted text, summaries, and tables
- **🎨 Modern UI**: Beautiful, responsive interface with interactive visualizations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- MySQL database (optional, for data persistence)

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL database (optional)**:
   ```sql
   CREATE DATABASE etl_pdf;
   USE etl_pdf;
   ```

4. **Run the application**:
   ```bash
   streamlit run pdf_dashboard.py
   ```

5. **Open your browser** and navigate to `http://localhost:8501`

## 📖 How to Use

### 1. Upload PDF
- Click on the file uploader or drag and drop a PDF file
- Supported format: PDF files only
- Maximum file size: 200MB (Streamlit default)

### 2. Configure Settings (Optional)
Use the sidebar to customize:
- **Summary Settings**: Adjust the number of sentences in the summary
- **Keyword Analysis**: Set the number of keywords to extract
- **Analysis Options**: Toggle different analysis features
- **Database Options**: Enable/disable saving to database

### 3. View Results
The dashboard provides results in organized tabs:

#### 📄 Extracted Text
- View the complete extracted text from the PDF
- Download the text as a .txt file

#### 📝 Summary
- Read the automatically generated summary
- Download the summary as a .txt file

#### 🔍 Keywords
- Interactive bar chart showing keyword frequencies
- Detailed keyword table with frequency counts

#### 📊 Statistics
- Document metrics (characters, words, sentences, paragraphs)
- Average sentence and word lengths
- Word length distribution histogram

#### 📋 Tables
- Extracted tables from the PDF (if any)
- Invoice data analysis with metrics
- Download tables as CSV files

#### 🗄️ Database
- Load existing data from MySQL database
- View database records and statistics
- Database connection status monitoring

## 🔧 Technical Details

### ETL Pipeline Integration
The application integrates with your existing ETL workflow:

1. **Extract**: Uses `pdfplumber` for robust text and table extraction
2. **Transform**: Cleans column names and handles missing data
3. **Load**: Saves processed data to MySQL database

### Text Processing Pipeline
1. **Text Extraction**: Uses `pdfplumber` for robust text extraction
2. **Text Cleaning**: Removes extra whitespace and normalizes text
3. **Tokenization**: Splits text into words and sentences using NLTK
4. **Keyword Extraction**: 
   - Removes stopwords and short words
   - Applies lemmatization
   - Counts word frequencies
5. **Summarization**: 
   - Uses extractive summarization based on sentence scoring
   - Scores sentences based on word frequency
   - Selects top-scoring sentences

### Database Configuration
- **Database**: MySQL
- **Host**: localhost
- **Database Name**: etl_pdf
- **Table Name**: invoice_data
- **User**: root (configurable)

### Libraries Used
- **Streamlit**: Web application framework
- **pdfplumber**: PDF text and table extraction
- **NLTK**: Natural language processing
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation and analysis
- **SQLAlchemy**: Database connectivity
- **PyMySQL**: MySQL database driver

## 🎯 Use Cases

- **Invoice Processing**: Extract and analyze invoice data
- **Document Analysis**: Quickly understand the content of long PDF documents
- **Research**: Extract key information from research papers and reports
- **Business Intelligence**: Analyze business documents and reports
- **Content Summarization**: Create summaries of articles and documents
- **Data Extraction**: Extract structured data from PDF tables
- **ETL Workflows**: Integrate with existing data processing pipelines

## 🔍 Advanced Features

### Customizable Analysis
- Adjust summary length based on your needs
- Control the number of keywords extracted
- Toggle different analysis features on/off
- Enable/disable database operations

### Interactive Visualizations
- Dynamic keyword frequency charts
- Word length distribution histograms
- Invoice data analysis metrics
- Responsive design that works on all devices

### Export Capabilities
- Download extracted text as plain text files
- Export summaries as separate files
- Save extracted tables as CSV files
- All downloads maintain original file naming

### Database Integration
- Real-time database connection status
- Load existing data from database
- Save processed data to database
- Database statistics and analysis

## 🛠️ Troubleshooting

### Common Issues

1. **PDF not loading**: Ensure the PDF is not password-protected or corrupted
2. **No text extracted**: Some PDFs may contain only images - try a different PDF
3. **Slow processing**: Large PDFs may take longer to process
4. **Missing dependencies**: Run `pip install -r requirements.txt` to install all required packages
5. **Database connection failed**: Check MySQL service and credentials

### Performance Tips
- For large PDFs, consider splitting them into smaller files
- Close other applications to free up memory
- Use the sidebar options to disable features you don't need
- Ensure MySQL is running for database operations

## 📝 Example Output

After uploading a PDF, you'll see:
- File information (name, size, upload time)
- Extracted text in a scrollable area
- Generated summary highlighting key points
- Keyword analysis with interactive charts
- Document statistics with metrics
- Extracted tables with invoice analysis
- Database operations and existing data

## 🔄 Integration with Existing Workflow

This dashboard seamlessly integrates with your existing ETL notebook:
- Uses the same database configuration
- Implements the same data transformation logic
- Maintains compatibility with existing data structures
- Provides web interface for the same functionality

## 🤝 Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Improving the documentation
- Submitting pull requests

## 📄 License

This project is open source and available under the MIT License.

---

**Happy PDF Processing and Summarizing! 📄✨** 