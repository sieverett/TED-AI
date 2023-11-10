#ingest.py

import streamlit as st
import openai
from langchain.document_loaders import TextLoader 
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# Load OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# here 
loader = TextLoader(folder_name)
documents = loader.load()

# Split the Notion content into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    separators=["#","##", "###", "\\n\\n","\\n","."],
    chunk_size=1500,
    chunk_overlap=100)
docs = text_splitter.split_documents(documents)

# Initialize OpenAI embedding model
embeddings = OpenAIEmbeddings()

# Convert all chunks into vectors embeddings using OpenAI embedding model
# Store all vectors in FAISS index and save to local folder 'faiss_index'
db = FAISS.from_documents(docs, embeddings)
db.save_local("faiss_index")

print('Local FAISS index has been successfully saved.')