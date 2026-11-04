#!/usr/bin/env python

# https://www.youtube.com/watch?v=oZYlrooPgvs
# https://github.com/MariyaSha/rag_ollama

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

K=7

embeddings = OllamaEmbeddings(model="bge-m3")

vector_db = FAISS.load_local(
    "elrond_investigation",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vector_db.as_retriever(
    search_kwargs={"k": K}
)

llm = ChatOllama(model="qwen2.5:1.5b")

def ask(question, chat_history=""):
    """
    improved ask question function - tracking the conversation
    """
    retrieved_chunks = retriever.invoke(question)

    context = ""

    for chunk in retrieved_chunks:
        context += chunk.page_content + "\n\n"

    response = llm.invoke(
        f"""
        You are an AI detective investigating whether Elrond is Agent Smith.
        
        Answer ONLY using the provided context.
        
        If the answer cannot be found in the context, say:
        "I don't know based on the case files."
        
        Chat History:
        {chat_history}

        Context:
        {context}

        Question:
        {question}
        """
    )

    return response.content

chat_history = ""

while True:
    question = input("Question: ")

    if question.lower() == "exit":
        break

    answer = ask(question, chat_history)

    chat_history += f"""
    User: {question}

    Assistant: {answer}

    """

    print("=" * 80)
    print(answer)
    print("=" * 80)
