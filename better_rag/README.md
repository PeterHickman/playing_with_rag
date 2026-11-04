# RAG

Code stolen from the [Python Simplified](https://www.youtube.com/@PythonSimplified) Youtube channel. Specifically the [RAG](https://www.youtube.com/watch?v=oZYlrooPgvs) episode and the related code from [github](https://github.com/MariyaSha/rag_ollama)

## Steps

1. Set up a virtual environment for Python 3.12
2. Install the requirements
3. Activate the environment
4. Run `tuning.py` this will find the values for `CHUNK_SIZE` and `CHUNK_OVERLAP` that will be needed by `loader.py` and the `K` value that `app.py` will need. To be honest the values it returns for this dataset are just as usable as any other. Don't sweat the values for this example
5. Set the values for `CHUNK_SIZE` and `CHUNK_OVERLAP` in `loader.py` and run it. You will end up with a directory called `elrond_investigation` that holds the vector database
6. Finally set the `K` value from step 4 into `app.py` and run it
7. Profit!!!

Make sure to watch the video linked above and visit the github repo
