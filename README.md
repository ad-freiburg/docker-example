# Inverted Index

Build an inverted index from a file containing movies and their descriptions.

[This program](inverted_index.py) will build an inverted index from an input
file and save it in a given output file using pickle.

Be careful, since the program will overwrite an existing file with the same
name!

Building this index takes a looong time, so you can find a precomputed output
file [here](path/to/output/precomputed_ii.pkl).


# Searching movies

Run [this program](search_movies.py) to query the inverted index. For any
amount of entered words, return movies whose description contains all of these
words.

To save the time for building the inverted index, you can use the
[precomputed file](path/to/output/precomputed_ii.pkl) as an input.
