import os
import re
import requests
from langchain_community.document_loaders import PyMuPDFLoader

class PaperUtils:

    def __init__(self):
        self.paper = None
        self.filename = None
        self.content = None
        self.cache_dir = "cache"

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)    
            
        self.document = {
            'title' : self.filename,
            'content' : self.content,
        }

    def sanitize_filename(self, filename):
        # This regex keeps alphanumeric, underscore, period, space, and hyphen
        # and replaces all other characters with an empty string.
        filename = re.sub(r'[^a-zA-Z0-9._ -]', ' ', filename)
        return filename.replace("  ", "")
        
    def process_paper(self, paper):
        self.paper = paper
        self.download_pdf()
        self.read_pdf()
        self.document = {
            'title' : self.filename,
            'content' : self.content,
        }
        return self.document
    
    def download_pdf(self):
        pdf_url = self.paper['link']
        try:
            pdf_response = requests.get(pdf_url.replace('/abs/', '/pdf/'))
            pdf_response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to download PDF from {pdf_url}") from e
        
        # filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + f"_{i:04d}"
        self.filename = self.paper['title']
        self.filename = self.sanitize_filename(self.filename)
        self.path_to_pdf = f"{self.cache_dir}/{self.filename}.pdf"
        print(f"Saving pdf to: {self.path_to_pdf}.")
        with open(self.path_to_pdf, "wb") as f:
            f.write(pdf_response.content)

    def read_pdf(self):
        pdf_loader = PyMuPDFLoader(self.path_to_pdf, mode='single')
        doc = pdf_loader.load()
        self.content = doc[0].page_content