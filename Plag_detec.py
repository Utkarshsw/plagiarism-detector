import streamlit as st
import pandas as pd
import nltk
# Ensure NLTK 'punkt' tokenizer is available
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/word_tokenize')
except LookupError:
    nltk.download('punkt')
    nltk.download('wordnet') # word_tokenize depends on wordnet

from nltk import tokenize
from bs4 import BeautifulSoup
import requests
import io
import docx2txt
from PyPDF2 import PdfReader
import plotly.express as px
from streamlit_extras.add_vertical_space import add_vertical_space
import re

# -------------------------------
# Utility Functions
# -------------------------------

def get_top_urls_api(query, api_key, cse_id, num_urls=7):
    """
    Searches Google using the official Custom Search JSON API.
    This is the new, robust function.
    """
    if not query:
        return []
    
    # Truncate query to be safe
    search_query = query[:300]
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': search_query,
        'num': num_urls
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise error for bad responses
        
        results = response.json()
        
        if 'items' not in results:
            st.warning("Google API returned 0 items for the search.")
            return []
            
        urls = []
        for item in results.get('items', []):
            url = item.get('link')
            if url and url.startswith('http') and "youtube.com" not in url:
                urls.append(url)
        return urls
        
    except requests.exceptions.RequestException as e:
        st.error(f"Network error while calling Google API: {e}")
        if response.text:
            st.error(f"API Response: {response.text}")
        return None # Signal failure
    except Exception as e:
        st.error(f"Error parsing API response: {e}")
        return None # Signal failure

def read_text_file(file):
    with io.open(file.name, 'r', encoding='utf-8') as f:
        return f.read()

def read_docx_file(file):
    return docx2txt.process(file)

def read_pdf_file(file):
    text = ""
    try:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
    return text

def get_text_from_file(uploaded_file):
    if uploaded_file is not None:
        try:
            if uploaded_file.type == "text/plain":
                return read_text_file(uploaded_file)
            elif uploaded_file.type == "application/pdf":
                return read_pdf_file(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return read_docx_file(uploaded_file)
        except Exception as e:
            st.error(f"Failed to process file {uploaded_file.name}: {e}")
            return ""
    return ""

def get_text(url):
    """Scrapes paragraph text from a given URL."""
    try:
        response = requests.get(url, 
                                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'},
                                timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        text_chunks = soup.find_all(string=True)
        blacklist = [
            '[document]', 'noscript', 'header', 'html', 'meta', 'head', 
            'input', 'script', 'style', 'footer', 'nav'
        ]
        
        output = ''
        for t in text_chunks:
            if t.parent.name not in blacklist:
                output += '{} '.format(t)

        return ' '.join(output.split())
        
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch text from URL {url}: {e}")
        return ""

# -------------------------------
# Similarity Logic Functions
# -------------------------------

def get_shingles(text, k=7):
    if not text:
        return set()
    
    words = [word for word in re.findall(r"[\w']+", text.lower()) if word.isalnum()]
    
    shingles = set()
    if len(words) < k:
        if words:
             shingles.add(tuple(words))
        return shingles

    for i in range(len(words) - k + 1):
        shingle = tuple(words[i:i+k])
        shingles.add(shingle)
    
    return shingles

def get_jaccard_similarity(text1, text2, k=7):
    if not text1 or not text2:
        return 0.0

    shingles1 = get_shingles(text1, k)
    shingles2 = get_shingles(text2, k)
    
    intersection = len(shingles1.intersection(shingles2))
    union = len(shingles1.union(shingles2))
    
    if union == 0:
        return 0.0
    else:
        return intersection / union

def get_similarity_list(texts, filenames=None, k=7):
    if filenames is None:
        filenames = [f"File {i+1}" for i in range(len(texts))]
    
    sims = []
    for i in range(len(texts)):
        for j in range(i+1, len(texts)):
            similarity = get_jaccard_similarity(texts[i], texts[j], k)
            sims.append((filenames[i], filenames[j], similarity))
    return sims

# -------------------------------
# Visualization Function
# -------------------------------

def plot_chart(df, chart_type):
    try:
        if chart_type == "Scatter":
            fig = px.scatter(df, x='File 1', y='File 2', color='Similarity', 
                             title='Similarity Scatter Plot', size='Similarity',
                             hover_data=['File 1', 'File 2', 'Similarity'])
        elif chart_type == "Line":
            df_melted = df.melt(id_vars=['File 1', 'Similarity'], value_vars=['File 2'], value_name='File 2')
            fig = px.line(df_melted, x='File 1', y='Similarity', color='File 2', 
                          title='Similarity Line Plot', markers=True)
        elif chart_type == "Bar":
            fig = px.bar(df, x='File 1', y='Similarity', color='File 2', 
                         title='Similarity Bar Chart', barmode='group')
        elif chart_type == "3D Scatter":
            fig = px.scatter_3d(df, x='File 1', y='File 2', z='Similarity', color='Similarity',
                                title='3D Similarity Visualization')
        elif chart_type == "Violin":
            df_melted = pd.melt(df, id_vars=['Similarity'], value_vars=['File 1', 'File 2'], 
                                var_name='File_Group', value_name='File_Name')
            fig = px.violin(df_melted, y='Similarity', x='File_Name', 
                            title='Similarity Distribution per File', box=True, points="all")
        else:
            st.warning("Invalid chart type selected.")
            return

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error plotting chart: {e}")

# -------------------------------
# Streamlit UI
# -------------------------------

st.set_page_config(page_title="AI-Powered Plagiarism Detector", page_icon="🧠", layout="wide")

st.markdown("<h1 style='text-align:center; color:#4B9CD3;'> Plagiarism & Similarity Detector (API)</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Options Panel")
    
    st.subheader("Google API Credentials")
    st.markdown("Get your keys from [Google Cloud Console](https://developers.google.com/custom-search/v1/introduction).")
    api_key = st.text_input("Enter your Google API Key", type="password")
    cse_id = st.text_input("Enter your CSE ID")
    
    st.divider()
    
    st.subheader("App Settings")
    mode = st.radio("Select Mode:", ['Enter Text', 'Upload File', 'Compare Multiple Files'])
    chart_choice = st.selectbox("📊 Choose Chart Type (for Multi-File)", ["Scatter", "Bar", "3D Scatter", "Violin", "Line"])
    
    add_vertical_space(1)
    st.info("💡 This tool uses the official Google Search API for reliable results.")
    st.info("💡 You can upload .txt, .pdf, or .docx files.")


# --- Main Page ---
add_vertical_space(2)

# Input Section
user_text = ""
texts = []
filenames = []

if mode == 'Enter Text':
    user_text = st.text_area("✏️ Enter or paste your text here:", height=250, placeholder="Paste your essay, article, or any text here...")
elif mode == 'Upload File':
    uploaded_file = st.file_uploader("📂 Upload a single file", type=["docx", "pdf", "txt"])
    if uploaded_file:
        with st.spinner(f"Reading {uploaded_file.name}..."):
            user_text = get_text_from_file(uploaded_file)
        if user_text:
            st.success(f"Successfully loaded {uploaded_file.name}.")
            with st.expander("Show File Content (First 500 characters)"):
                st.write(user_text[:500] + "...")
        else:
            st.warning("Could not extract text from the file.")
else: # 'Compare Multiple Files'
    uploaded_files = st.file_uploader("📁 Upload 2 or more files", type=["docx", "pdf", "txt"], accept_multiple_files=True)
    if uploaded_files and len(uploaded_files) >= 2:
        with st.spinner("Reading all files..."):
            for file in uploaded_files:
                text = get_text_from_file(file)
                if text:
                    texts.append(text)
                    filenames.append(file.name)
                else:
                    st.warning(f"Could not extract text from {file.name}. It will be skipped.")
        if len(texts) < 2:
            st.warning("Please upload at least two valid files to compare.")
    elif uploaded_files:
        st.info("Please upload at least 2 files for comparison.")

# Processing Section
if st.button("🚀 Run Detection", type="primary"):
    
    # --- Compare Multiple Files Logic ---
    if mode == 'Compare Multiple Files':
        if len(texts) >= 2:
            st.info("🔍 Comparing files... This may take a moment.")
            with st.spinner("Calculating similarities..."):
                sims = get_similarity_list(texts, filenames, k=7)
            
            if not sims:
                st.warning("Could not calculate any similarities.")
                st.stop()
                
            df = pd.DataFrame(sims, columns=['File 1', 'File 2', 'Similarity']).sort_values(by='Similarity', ascending=False)
            st.success("✅ Similarity analysis completed!")
            
            st.subheader("📊 Similarity Visualization")
            plot_chart(df, chart_choice)
            
            st.subheader("📈 Similarity Scores")
            st.dataframe(df.style.format({'Similarity': '{:.2%}'}))
        else:
            st.warning("⚠️ Please upload at least two valid files to compare.")
    
    # --- Single Text/File Logic (API-based) ---
    else:
        if not user_text:
            st.warning("⚠️ No input text provided. Please enter text or upload a file.")
            st.stop()
            
        # Check for API keys
        if not api_key or not cse_id:
            st.error("🚨 Please enter your Google API Key and CSE ID in the sidebar to run the detection.")
            st.stop()
            
        st.info("🔍 Searching for potential online sources via Google API...")
        
        with st.spinner("Searching Google for top matches..."):
            urls = get_top_urls_api(user_text, api_key, cse_id, num_urls=7)

        if urls is None:
            st.error("Search failed. Check your API credentials or Google Cloud project settings.")
            st.stop()
        
        if not urls:
            st.success("🎉 No potential online sources found! The content appears to be original.")
            st.stop()
        
        st.info(f"Found {len(urls)} potential source(s). Comparing content...")
        
        results = []
        with st.spinner("Fetching and comparing text from sources..."):
            for url in urls:
                scraped_text = get_text(url)
                if scraped_text:
                    similarity = get_jaccard_similarity(user_text, scraped_text, k=7)
                    if similarity > 0.02: # 2% similarity threshold
                        results.append((url, similarity, scraped_text[:200] + "..."))

        if not results:
            st.success("✅ Search complete. No significant plagiarism detected!")
            st.write("While some online pages were found, their content does not significantly match the submitted text.")
            st.stop()

        # Display results
        st.success("✅ Plagiarism check completed!")
        st.subheader("🚨 Potential Matches Found")
        
        df = pd.DataFrame(results, columns=['Potential Source URL', 'Similarity Score', 'Source Excerpt'])
        df = df.sort_values(by='Similarity Score', ascending=False)

        st.dataframe(df.style.format({'Similarity Score': '{:.2%}'}))

st.markdown("---")
