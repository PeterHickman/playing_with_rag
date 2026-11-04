#!/usr/bin/env python

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

import os

chunk_sizes = [500, 600, 700]
chunk_overlaps = [50, 150, 250]
ks = [3, 5, 7]

file_names = sorted(os.listdir("data"))

all_pages = []

for file in file_names:
    loader = PyPDFLoader("data/" + file)
    pages = loader.load()
    all_pages.extend(pages)

llm = ChatOllama(model="qwen2.5:1.5b")
embeddings = OllamaEmbeddings(model="bge-m3")

question = "Why is Elrond under investigation?"


def ask_with_retriever(question, retriever):
    retrieved_chunks = retriever.invoke(question)

    context = ""

    for chunk in retrieved_chunks:
        context += chunk.page_content + "\n\n"

    response = llm.invoke(f"""
        You are an AI detective investigating whether Elrond is Agent Smith.

        Answer ONLY using the provided context.

        If the answer cannot be found in the context, say:
        "I don't know based on the case files."

        Context:
        {context}

        Question:
        {question}
        """)

    return response.content, retrieved_chunks


results = []

for chunk_size in chunk_sizes:
    for chunk_overlap in chunk_overlaps:
        print(f"==> chunk_size={chunk_size} chunk_overlap={chunk_overlap}")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        chunks = splitter.split_documents(all_pages)
        vector_db = FAISS.from_documents(chunks, embeddings)

        for k in ks:
            retriever = vector_db.as_retriever(search_kwargs={"k": k})

            answer, retrieved_chunks = ask_with_retriever(question, retriever)

            result = {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "k": k,
                "num_chunks": len(chunks),
                "answer": answer,
            }

            results.append(result)

            print(f"    k={k}")

reference_answer = """
Elrond is under investigation because witness statements reported irregular behavior,
leading to allegations that he may have possible affiliation with, impersonation by,
or identity overlap with an extradimensional entity known as Agent Smith.
"""


def evaluate_answer(reference, answer):
    texts = [reference, answer]

    vectorizer = TfidfVectorizer(
        lowercase=True, stop_words="english", ngram_range=(1, 2)
    )

    tfidf = vectorizer.fit_transform(texts)

    similarity = cosine_similarity(tfidf[0], tfidf[1])[0][0]

    ref_words = reference.split()
    answer_words = answer.split()

    length_ratio = min(len(answer_words), len(ref_words)) / max(
        len(answer_words), len(ref_words)
    )

    return {
        "similarity": similarity,
        "length_ratio": length_ratio,
        "final_score": (similarity * 0.8) + (length_ratio * 0.2),
    }


scored_results = []

for result in results:
    scores = evaluate_answer(reference_answer, result["answer"])

    scored_results.append({**result, **scores})

df = pd.DataFrame(scored_results)

df = df.sort_values("final_score", ascending=False)

df[
    [
        "chunk_size",
        "chunk_overlap",
        "k",
        "similarity",
        "length_ratio",
        "final_score",
        "answer",
    ]
]

best = df.iloc[0]

print()
print("BEST CONFIG")
print(f"chunk_size: {best['chunk_size']}")
print(f"chunk_overlap: {best['chunk_overlap']}")
print(f"k: {best['k']}")
print(f"similarity: {best['similarity']:.3f}")
print(f"length_ratio: {best['length_ratio']:.3f}")
print(f"final_score: {best['final_score']:.3f}")
print()
print(best["answer"])
