import shutil
import glob
import os.path
import time

import ollama
import chromadb
from pypdf import PdfReader
from markdown_it import MarkdownIt
from mdit_plain.renderer import RendererPlain

import settings
from lib.utils import *
from lib.epub_parser import EPUBParser

class RAGLoader:
    def __init__(self, debug):
        self.debug = debug

        self.collection = self.open_chromadb(False)
        self.existing_files = loaded_files(self.collection)

    def reset(self):
        self.collection = self.open_chromadb(True)
        self.existing_files = loaded_files(self.collection)

    def load_directory(self, directory):
        if not os.path.isdir(directory):
            print(f"Cannot find a directory called {directory}")
            return

        filenames = glob.glob(f"{directory}/*")
        filenames.sort()

        for filename in filenames:
            self.load_file(filename)

    def load_file(self, filename):
        if not os.path.isfile(filename):
            print(f"Cannot find a file called {filename}")
            return

        if filename in self.existing_files:
            print(f"Already loaded {filename}")
        else:
            if filename.endswith(".txt"):
                self.load_text(filename)
            elif filename.endswith(".pdf"):
                self.load_pdf(filename)
            elif filename.endswith(".md"):
                self.load_md(filename)
            elif filename.endswith(".epub"):
                self.load_epub(filename)
            else:
                print(f"Unknown type for {filename}")

    def load_md(self, filename):
        print(f"Reading file {filename}")

        parser = MarkdownIt(renderer_cls=RendererPlain)

        start_time = time.time()

        with open(filename, "r") as h:
            extracted_text = parser.render(h.read())
            c = self.split_into_chunks(filename, 0, extracted_text)

        end_time = time.time()
        print(f"        Created {c} chunks in {end_time - start_time:.4f} seconds")

    def load_epub(self, filename):
        print(f"Reading file {filename}")

        start_time = time.time()

        p = EPUBParser()
        d = p.parse(filename)
        c = self.process_text(filename, 0, d)

        end_time = time.time()
        print(f"        Created {c} chunks in {end_time - start_time:.4f} seconds")

    def load_text(self, filename):
        print(f"Reading file {filename}")

        start_time = time.time()
        c = 0

        with open(filename, "r") as h:
            d = h.read()
            c = self.process_text(filename, c, d)

        end_time = time.time()
        print(f"        Created {c} chunks in {end_time - start_time:.4f} seconds")

    def load_pdf(self, filename):
        print(f"Reading file {filename}")

        reader = PdfReader(filename)

        start_time = time.time()

        pages = []
        for i in range(reader.get_num_pages()):
            page = reader.pages[i]
            pages.append(page.extract_text())

        extracted_text = " ".join(pages)
        c = self.split_into_chunks(filename, 0, extracted_text)

        end_time = time.time()
        print(f"        Created {c} chunks in {end_time - start_time:.4f} seconds")

    def split_into_chunks(self, filename, c, extracted_text):
        texts = self.split_text(extracted_text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)

        for i in range(len(texts)):
            c += 1
            self.process(filename, f"{filename}:{c}", texts[i])

        return c

    def split_text(self, text, width, overlap):
        words = text.split()

        l = []

        while len(words):
            l.append(" ".join(words[:width]))
            words = words[(width - overlap):]

        return l

    def process(self, filename, tid, text):
        if len(text) == 0:
            return

        response = ollama.embed(model=settings.EMDEDDING_MODEL, input=text)

        if self.debug:
            print(f"        {tid}")
            print(text)
            print()

        self.collection.add(
            ids=[tid],
            embeddings=response["embeddings"],
            documents=[text],
            metadatas=[{"filename": filename}]
        )

    def process_text(self, filename, c, d):
        lines = d.splitlines()
        text = ""

        for line in lines:
            if line == "":
                if text != "":
                    c = self.split_into_chunks(filename, c, text)
                    text = ""
            else:
                text += line

        if text != "":
            c = self.split_into_chunks(filename, c, text)

        return c

    def open_chromadb(self, reset):
        if reset:
            shutil.rmtree(settings.CHROMADB)

        client = chromadb.PersistentClient(path=settings.CHROMADB)

        for c in client.list_collections():
            if c.name == settings.COLLECTION_NAME:
                return client.get_collection(name=settings.COLLECTION_NAME)

        return client.create_collection(name=settings.COLLECTION_NAME)
