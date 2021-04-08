# Inverted Index Evaluation

This is the README.md file explaining the results of the evaluation.
There is also a README.md file that explains [how to run the evaluation and how to use the programs involved](https://github.com/ad-freiburg/reproducibility-example).

## Datasets

We used [this dataset](https://ad-teaching.informatik.uni-freiburg.de/InformationRetrievalWS1920/movies2.txt) with 107,769 movies to build the inverted index.
The dataset contains one entry for each movie with the title and a description for each movie.

We then evaluated the inverted index against a benchmark that contains 12 keyword queries.
For our benchmark, we combined
[this training benchmark](http://ad-teaching.informatik.uni-freiburg.de/InformationRetrievalWS1920/movies.training-benchmark.tsv)
and [this testing benchmark](http://ad-teaching.informatik.uni-freiburg.de/InformationRetrievalWS1920/movies.testing-benchmark.tsv)
with 6 queries each.

## Evaluation

For the evaluation, the [BM25 scores](https://en.wikipedia.org/wiki/Okapi_BM25) are computed.
Each mode uses a different set of values for k and b in the BM25 formula.
The inverted index then returns a list of results, ranked according to the BM25 scores.
The measures Precision at 3, Precision at k and Average Precision are computed for each mode and each query.
To read more about these evaluation measures, see [here](https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)) or [here](https://daphne.informatik.uni-freiburg.de/ws1920/InformationRetrieval/svn/public/slides/lecture-02.pdf).
