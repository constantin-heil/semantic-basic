# Basic semantic search

This repo demonstrates basic functionality of semantic search.

The process basically consists of the following steps:
 - Chop up a text and obtain embeddings for each block
 - Save the texts and embeddings in a database with vector lookup capability (vector store)
 - Get a user question, again get its embeddings
 - Find the top text blocks that are most similar to the query
 - Integrate that result into a query and send that query to OpenAI completion API

 **Since you are here using both the OpenAI Embeddings as well as Completion API, make sure not to send private or sensitive information.**

 You will need to save your OpenAI API key in a file secretkey.txt in the repos root path.

The enclosed example datafile come from:
https://www.gutenberg.org/ebooks/15877

 ## Usage

  1. Activate the vector store

  The vector store is a normal postgresql database with the pgvector extension activated.

  To activate:
  ```
  cd database
  docker build -t pgimg .
  bash startup.sh
  ```

  Verify activation by pointing a client (psql, DBeaver) to port 5432 with username **root** and password **password**.

  2. Load embeddings into DB

  There is an example datafile under _datafile/meditations.txt_.

  Run:
  ```
  python writedb.py -t datafile/meditations.txt
  ```

  3. Interrogate database and model

  Run:
  ```
  python sendprompts.py -u 'My question to the emperor'
  ```
