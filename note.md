Component 1: tiktoken — Token-Based Chunking
What it is: OpenAI's tokenizer library. Counts and splits text by tokens (subword units), not characters. Other way is Recursive character - splitLangChainGood - but adds LangChain dependency.

Component 2: CHUNK_OVERLAP = 40 — Sliding Window
What it is: Each new chunk starts 40 tokens before the previous chunk ended.Why it matters: Without overlap, a key sentence sitting exactly at a chunk boundary gets split. The reranker in Stage 2 would never see the complete thought.

Component 3: hashlib.md5 — Deduplication
What it is: MD5 fingerprint of every chunk text. If the same text appears twice (from overlap or duplicate documents), it's skipped. Why it matters: Without this, re-ingesting the same email twice doubles your vectors. The retrieval results would return duplicate chunks at the top.

pipeline
1.The Document is Chunked: Your script reads the text file and uses tiktoken purely as a measuring tape. tiktoken counts the tokens to figure out where to cut the text so that no chunk exceeds your max_tokens limit.

2.Chunks are kept as Text Strings: Once the boundaries are decided, the chunks are stored in a Python list as regular plain-text strings (not numbers or token IDs).

3.SentenceTransformer takes the Plain Text: When you run encoder.encode(chunk), you pass the raw text string directly into the model.2. What "happens inside the SentenceTransformer?"
The SentenceTransformer has its own internal pipeline. When you pass a text string to it, it performs two steps automatically under the hood:
    >Internal Tokenization: The model uses its own built-in tokenizer (which is different from tiktoken) to split your text chunk into its own specialized token IDs.

    >Vector Generation: It passes those internal tokens through its neural network layers to output a single, consolidated 384-dimensional vector embedding that represents the semantic meaning of the entire text string.

    JSON = metada where provide extra information to the retriver like file path, formar etc eg this chunks belongs to file1.txt not in file2.txt

main.py
python librarires
1.import os - It acts as a bridge between your Python code and your computer's file system.

2.import shutil - If os is the manager that creates folders, shutil is the heavy-machinery mover that moves big files around. When a user uploads a large document through their web browser, shutil takes that incoming stream of digital data and streams it directly onto your hard drive to save a permanent copy.

3.import json - It translates Python dictionaries (which use curly braces {}) into a universal internet text format called JSON (JavaScript Object Notation), and vice versa. It allows different systems (like your UI and your backend) to talk to each other.

4.import datetime - It tracks time-stamps. It allows your system to log exactly when a file was uploaded or when a chat message was sent.

5.from fastapi import FastAPI, UploadFile, File, HTTPException
    a.FastAPI: The master server controller.
    b.UploadFile & File: Specialized tools designed to catch files safely as they fly across the internet from a browser upload button.
    c.HTTPException: A clean way to send back red error messages (like a 404 Not Found or 500 Server Error) if something breaks.

6.from fastapi.responses import HTMLResponse - Normally, a backend server only sends back raw data numbers. HTMLResponse tells the user's web browser: "Hey, treat this text like a visual website with colors and buttons, not just plain words." It's used to load and render your ui.html file.

7.from fastapi.middleware.cors import CORSMiddleware - CORS stands for Cross-Origin Resource Sharing. Modern web browsers have a built-in safety rule: they block web interfaces on one port from talking to backends on a different port. 
    Why you need it: Your backend runs on port 8000. If your frontend UI runs somewhere else, the browser will block them from talking. Adding this middleware flips that safety switch to "Allow" so your UI can communicate with your backend smoothly.

8.from pydantic import BaseModel - If a user sends a chat message, BaseModel verifies that the incoming request contains exactly what you expect (e.g., a text string) before letting it proceed into your pipeline. It prevents broken or corrupted data from crashing your server.

9.import uvicorn - FastAPI is just a blueprint of your routes; it cannot actually open network ports on its own. Uvicorn is an asynchronous server engine that takes your FastAPI app configuration and turns it into a live, high-speed running process on your computer (host='0.0.0.0', port=8000). It is what physically makes your application accessible at http://localhost:8000.