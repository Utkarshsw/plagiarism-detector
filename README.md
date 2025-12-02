Plagiarism & Similarity Detector

📜 Project Description

The Plagiarism & Similarity Detector is a robust Python-based web application designed to detect syntactic (copy-paste) plagiarism. Unlike traditional tools that rely on static datasets, this application leverages the Google Custom Search JSON API to compare user input against the live internet in real-time.

The core logic utilizes Natural Language Processing (NLP) techniques—specifically k-shingling (k=7) and Jaccard Similarity—to calculate similarity scores based on word order and context. This method is superior to simple "Bag-of-Words" approaches for detecting direct plagiarism because it respects the structure of sentences. The application supports direct text input as well as .txt, .pdf, and .docx file uploads.

🚀 Setup and Installation

Follow these steps to set up and run the project locally.
1. Clone the Repository
Open your terminal and clone this repository to your local machine:
git clone [https://github.com/Utkarshsw/plagiarism-detector.git](https://github.com/Utkarshsw/plagiarism-detector.git)
cd plagiarism-detector

2. Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

Windows:

python -m venv venv
venv\Scripts\activate


macOS / Linux:

python3 -m venv venv
source venv/bin/activate


3. Install Dependencies

Install the required Python libraries using the requirements.txt file.

pip install -r requirements.txt


4. Download NLTK Data

The project uses NLTK for tokenization. You can run this command to ensure the necessary data is downloaded:

python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet')"


5. Get Google API Credentials

To use the "Enter Text" or "Single File" modes, you need API credentials to search the web.

API Key: Go to the Google Cloud Console, create a project, and enable the Custom Search JSON API.

CSE ID: Go to the Programmable Search Engine, create a search engine, and enable "Search the entire web" in the setup.

📂 Directory Structure

Here is a brief overview of the repository's structure:

plagiarism-detector/
│
├── Plagiarism_Detector_API.py   # The main application script
├── requirements.txt             # List of dependencies
├── README.md                    # Project documentation
└── .gitignore                   # Files to ignore (e.g., venv, __pycache__)


📊 Dataset Information

This project does not use a static offline dataset.

Source: The Live World Wide Web.

Access Method: Google Custom Search JSON API.

Preprocessing:

User Input: Tokenized using Regular Expressions (re) and converted to lowercase.

Web Content: Extracted using requests and BeautifulSoup. HTML tags (like <script>, <style>, <nav>) are filtered out to isolate human-readable text.

Stopwords: Intentionally retained to preserve the "fingerprint" of the sentence structure for strict plagiarism detection.

🖥️ Usage & Examples

How to Run

Execute the following command in your terminal:

streamlit run Plagiarism_Detector_API.py


The application will open in your default web browser (usually at http://localhost:8501).

Example Workflow

Input Data:

User Action: Paste the following text into the "Enter Text" box:

"Shahrukh Khan, popularly known by the initials SRK, is an Indian actor and film producer renowned for his work in Hindi cinema."

Settings: Enter your API Key and CSE ID in the sidebar.

Process:

The app queries Google, finds relevant URLs (e.g., Wikipedia, IMDb), scrapes the text, generates 7-word shingles, and calculates the Jaccard Similarity.

Expected Output:

A table displaying the top sources.

Potential Source URL

Similarity Score

Source Excerpt

https://en.wikipedia.org/wiki/Shahrukh_Khan

98.2%

"...Shahrukh Khan, popularly known by the initials SRK..."

https://www.imdb.com/name/nm0451321/

45.1%

"...is an Indian actor and film producer..."

Architecture

UI Layer: User inputs text via Streamlit.

Discovery Layer: App queries Google API to find sources.

Extraction Layer: BeautifulSoup cleans HTML from fetched URLs.

Logic Layer: k-Shingling (k=7) + Jaccard Similarity calculation.

Presentation Layer: Results are rendered in a Pandas DataFrame.

🛠️ Tech Stack

Language: Python 3.8+

Web Framework: Streamlit

Data Collection: Google Custom Search JSON API, Requests, BeautifulSoup (bs4)

NLP: NLTK, Regex (re)

Data Handling: Pandas

Visualization: Plotly Express

File Handling: PyPDF2 (PDFs), docx2txt (Word Docs)