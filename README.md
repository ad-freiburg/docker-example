# Inverted Index

Build, query and evaluate an inverted index.
The following are short descriptions of what the important programs do. For
more details, call each program with the '-h'-flag to get usage information.


## Build an Inverted Index

[This program](inverted_index.py) will build an inverted index from a given
input file and save it in an output file using pickle.

Be careful, since the program will overwrite an existing file with the same
name!

You can find a precomputed output file in the nfs folder
(nfs/studentes/example-project)


## Query the Inverted Index

Run [this program](query_precomputed_ii.py) to query an inverted index. For
any amount of entered words, return movies whose description got the highest
BM25 scores.

To save time for building the inverted index, you can use the precomputed file
in the nfs folder as an input.


## Evaluate the Inverted Index

To evaluate an inverted index against a benchmark and compute the measures
precision at 3, precision at R and average precision, use
[this program](evaluate_inverted_index.py).


## Build a webapp

You can build a webapp that nicly outputs the evaluation, use
[this program](www/webapp.py).
