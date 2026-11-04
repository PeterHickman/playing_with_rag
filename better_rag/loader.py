#!/usr/bin/env python

# https://www.youtube.com/watch?v=oZYlrooPgvs
# https://github.com/MariyaSha/rag_ollama

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

import os

CHUNK_SIZE=600
CHUNK_OVERLAP=50

file_names = sorted(os.listdir("data"))

all_pages = []

for file in file_names:
    print(f"==> {file}")
    loader = PyPDFLoader("data/" + file)
    pages = loader.load()
    print(f"    {len(pages)} pages")

    all_pages.extend(pages)

splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

chunks = splitter.split_documents(all_pages)
print(f"{len(all_pages)} pages in {len(chunks)} chunks")

embeddings = OllamaEmbeddings(model="bge-m3")

vector_db = FAISS.from_documents(chunks, embeddings)

vector_db.save_local("elrond_investigation")
