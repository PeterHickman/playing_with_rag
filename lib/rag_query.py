import ollama
import chromadb

import settings

class RAGQuery:
    def __init__(self, collection):
        self.collection = collection
        self.debug = False

    def query(self, prompt, debug):
        self.debug = debug

        response = ollama.embed(model=settings.EMDEDDING_MODEL, input=prompt)

        results = self.collection.query(
          query_embeddings=[response["embeddings"][0]],
          include=["metadatas","distances","documents"],
          n_results=settings.RESULTS
        )

        print(f"Query:    {prompt}")
        chunks, distances, texts = self.contents(results, settings.THRESHOLD) 

        if len(chunks) == 0:
            print(f"RAG:      No data available, passing it to {settings.MODEL}")
            text = prompt
        else:
            print(f"RAG:      Usable data in {chunks}")

            if self.debug:
                x = self.collection.get(ids=chunks)
                for i in range(len(x["ids"])):
                    print()
                    print(f"ID {x["ids"][i]} {distances[x["ids"][i]]}")
                    print(x["documents"][i])

            text = f"Using this data: {texts}. Respond in plain text to this prompt: {prompt}"
        print()

        output = ollama.generate(model=settings.MODEL, prompt=text)
        if self.debug:
            print(output.response.strip())
        else:
            print(self.remove_thinking(output.response.strip()))

    def contents(self, response, threshold):
        chunks = []
        distances = {}
        texts = []

        l = len(response["ids"][0])

        for i in range(l):
            if response["distances"][0][i] <= threshold:
                chunks.append(response["ids"][0][i])
                distances[response["ids"][0][i]] = response["distances"][0][i]
                texts.append(response["documents"][0][i])

        return chunks, distances, "\n\n--\n\n".join(texts)

    def remove_thinking(self, text):
        thinking = False
        r = []

        for line in text.splitlines():
            if thinking:
                if line.startswith("</think>"):
                    thinking = False
            else:
                if line.startswith("<think>"):
                    thinking = True
                else:
                    r.append(line)

        return " ".join(r).strip()
