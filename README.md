# Inverted Index

This project contains programs to constuct, query and evaluate an inverted index.

An inverted list for a word is a sorted list of ids of records containing that word.
An inverted index is a map from all words to their inverted list.
We can use an inverted index to perform keyword search on a collection of text documents.
If you want to get more familar and more background information about the topic,
take a look at lectures 1 and 2 of the Information Retrieval lecture
[here](https://ad-wiki.informatik.uni-freiburg.de/teaching/InformationRetrievalWS1920 "Information Retrieval")

There are precomputed files available, since it might take a long time to compute some of them.
The data available is based on a movies dataset from the lecture mentioned above.
It contains 107,769 movies with title and description.

What follows are short descriptions of what the available programs do, what
files they require and output and which precomputed files are available to use.
For more details, call each program with the '-h'-flag to get usage information.


## Build an Inverted Index

[This program](inverted_index.py) will create an inverted index from a given input file and save it in an output file using pickle.
It computes the BM25 scores as explained in [lecture 2](https://daphne.informatik.uni-freiburg.de/ws1920/InformationRetrieval/svn/public/slides/lecture-02.pdf), that is
<img src="http://render.githubusercontent.com/render/math?math=tf^{*}\cdot\log_2\left(\frac{N}{df}\right)">,
where `N` is the total number of documents, `df` is the number of documents that contain a word and
<img src="http://render.githubusercontent.com/render/math?math=tf^{*}=\frac{tf\cdot\left(k+1\right)}{k\cdot\left(1-b+\frac{b\cdot DL}{AVDL}\right)+tf}">,
where tf is the term frequency, DL is the document length and AVDL is the average document length.
k and b are parameters that can be chosen in the program.
Usage:

```python3 inverted_index.py [-b B] [-k K] file_name```

The expected format of the file is one document per line, in the format <title>TAB<description>.
The program will automatically save the inverted index using pickle.
The output file will have the same base name, appended by "precomputed_ii.pkl"
Be careful, since the program will overwrite an existing file with the same name!

You can find a precomputed output file in the NFS folder (nfs/students/example-project)


## Query the Inverted Index

Run [this program](query_precomputed_ii.py) to query an inverted index. For
any amount of entered words, return movies whose description got the highest
BM25 scores.

To save time for building the inverted index, you can use the precomputed file
in the NFS folder as an input.


## Evaluate the Inverted Index

To evaluate an inverted index against a benchmark and compute the measures
precision at 3, precision at R and average precision, use
[this program](evaluate_inverted_index.py).


## Build a webapp

You can build a webapp that nicely outputs the evaluation using
[this program](www/webapp.py).
