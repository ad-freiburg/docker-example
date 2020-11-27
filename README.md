# Inverted Index

This project contains programs to constuct, query and evaluate an inverted index.

An inverted list for a word is a sorted list of ids of records containing that word.
An inverted index is a map from all words to their inverted list.
We can use an inverted index to perform keyword search on a collection of text documents.
If you want to get more familar and more background information about the topic,
take a look at lectures 1 and 2 of the Information Retrieval lecture
[here](https://ad-wiki.informatik.uni-freiburg.de/teaching/InformationRetrievalWS1920 "Information Retrieval")

## Getting started

This project is designed to be used with [docker](https://www.docker.com/) or [wharfer](https://github.com/ad-freiburg/wharfer).

Use the following commands (you can also find them at the end of the [Dockerfile](Dockerfile)) to build an image and run a container:

```
docker build -t docker-example .
docker run --rm -it -p 5000:5000 -v /nfs/students/example-project/input:/docker-example/input:ro -v /nfs/students/example-project/output:/docker-example/output:rw --name docker-example docker-example
```

What follows are short descriptions of what the available programs do, what files they require and output and which precomputed files are available to use.
For more details, call each program with the '-h'-flag to get usage information.

## Creating an Inverted Index

The program 'inverted_index.py' will create an inverted index from a given input file and save it in an output file using pickle.
It computes the BM25 scores for each word and document, that is 
	BM25 = tf * (k+1) / (k * (1 - b + b * DL/AVDL) + tf) * log2(N/df),
where tf is the term freqiemcy, DL is the document length, AVDL is the average document length, N is the total number of documents and df is the number of documents that contain the word.
Moreover, k and b are parameters to be chosen.
You can find more background information about the BM25 scores in [lecture 2](https://daphne.informatik.uni-freiburg.de/ws1920/InformationRetrieval/svn/public/slides/lecture-02.pdf) of the Information Retrieval lecture.

Usage: `python3 inverted_index.py [-b B] [-k K] file_name`

The expected format of the input file is one document per line, in the format \<title\>TAB\<description\>.
A file 'movies.txt' in the expected format is available in '/nfs/students/example-project/input'.
It contains 107.769 movies with title and description.
The input b and k are the parameters mentioned in the formula above (default: b=0.75, k=1.75).
The program will automatically save the inverted index using pickle.
The output file will have the same base name, appended by 'precomputed_ii.pkl'
Be careful, since the program will overwrite an existing file with the same name!

*Note: Since building an inverted index takes a long time, a file ('movies_precomputed_ii.pkl') with a precomputed inverted index is already available in the NFS output folder.
This means you do not have to run this piece of code on the movies dataset.*

## Keyword search on the Inverted Index

Run 'query_precomputed_ii.py' to perform keyword search on an inverted index.
For any amount of entered words, it returns movies whose description got the highest BM25 scores.

Usage: `python3 query_precomputed_ii.py precomputed_file`

Here, 'precomputed_file' is a pickle file containing the precomputed inverted index.
It expects a file as produced by 'inverted_index.py'.
For the movies dataset, this file has already been precomputed and is available in the NFS output folder.

## Evaluating the Inverted Index

We can evaluate an inverted index against a benchmark and compute the measures precision at 3, precision at R and average precision.
For a definition of these measures and more background information, feel free to take a look at [lecture 2](https://daphne.informatik.uni-freiburg.de/ws1920/InformationRetrieval/svn/public/slides/lecture-02.pdf) of the Information Retrieval lecture.
To evaluate an inverted index against a benchmark and compute these three measures, use 'evaluate_inverted_index.py.

Usage: `python3 evaluate_inverted_index.py precomputed_file benchmark_file`

Here, 'precomputed_file' is a pickle file containing the precomputed inverted index.
It expects a file as produced by 'inverted_index.py'.
For the movies dataset, this file has already been precomputed and is available in the NFS output folder.
The second input 'benchmark_file' is the file containing the benchmark.
The expected format of this file is one query per line, with the ids of all documents relevant for that query, like:
\<query\>TAB\<id1\>WHITESPACE\<id2\>WHITESPACE\<id3\> ...
A file 'movies-benchmark.tsv' in the expected format is available in '/nfs/students/example-project/input'.
It is suitable for the movies dataset and contains 12 queries.
The program automatically saves the data of the evaluation using pickle.
The output file will have the same base name as the benchmark file, appended by 'evaluation.pkl'.

*Note: Since evaluating an inverted index takes a long time, a file ('movies-benchmark_evaluation.pkl') with a precomouted evaluation is already available in the NFS output folder.
This means you do not have to run this piece of code on the movies dataset.*

## Building the webapp

You can build a webapp that nicely outputs an extensive evaluation using 'webapp.py' in the 'www' directory.

Usage: `python3 webapp.py [-p PORT] evaluation_file`

Here, 'evaluation_file' is a pickle file containing an evaluation.
It expects a file as produced by 'evaluate_inverted_index.py'.
For the movies dataset, this file has already been precomputed and is available in the NFS output folder.
Furthermore, PORT is the port for the webapp.
If you are using docker, this should be the container port you published to the docker host (default: 5000).
