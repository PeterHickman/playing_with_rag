# Playing with RAG

I wanted to understand how RAGs worked and for me that means coding my own. This is the result of me following YouTube tutorials and Googling as required

Runs on `Python 3.12.11` in it's own venv. The `data` directory contains some test documents and `requirements.txt` will install the necessary modules for you

```bash
$ ./rag --add_dir data
Reading file data/alice_in_wonderland.md
        Created 165 chunks in 8.6560 seconds
Reading file data/introduction_to_cyber_security__stay_safe_online.epub
        Created 255 chunks in 13.1685 seconds
Reading file data/learning_from_major_cyber_security_incidents.epub
        Created 56 chunks in 3.1101 seconds
Reading file data/llama_facts.txt
        Created 6 chunks in 0.1560 seconds
Reading file data/monopoly.pdf
        Created 17 chunks in 0.9265 seconds
Reading file data/ticket_to_ride.pdf
        Created 12 chunks in 0.7321 seconds
$ ./rag --list
Filename                                                    Chunks
----------------------------------------------------------  ------
data/alice_in_wonderland.md                                    165
data/introduction_to_cyber_security__stay_safe_online.epub     255
data/learning_from_major_cyber_security_incidents.epub          56
data/llama_facts.txt                                             6
data/monopoly.pdf                                               17
data/ticket_to_ride.pdf                                         12
$ ./rag --query "What animals are llamas related to?"
Query:    What animals are llamas related to?
RAG:      Usable data in ['data/llama_facts.txt:1', 'data/llama_facts.txt:5', 'data/llama_facts.txt:4', 'data/llama_facts.txt:2', 'data/llama_facts.txt:3']

Llamas are closely related to other members of the camelid family – such as vicuñas, alpacas, and guanacos – and are also related to the camel species (dromedaries and Bactrian camels).
```

## Questions no one asked

### Langchain?

So why didn't I just use Langchain? It's a wonderful framework to set up you own RAG if setting up a RAG is your priority. My priority was understanding how it worked. To that end I needed to get my hands into the guts and code it up myself. The urge to write my own vector database to replace ChromaDB was strong :)

### You wrote your own EPUB converter?

There is a perfectly good one available but it does result in much repeated text. I dumped the test documents to see and there was quite a lot of repetition, especially of page titles. Felt like it could be polluting the data and how hard was it to write my own?

