"""
Copyright 2017, University of Freiburg
Chair of Algorithms and Data Structures.
Claudius Korzen <korzen@cs.uni-freiburg.de>
Theresa Klumpp <klumppt@cs.uni-freiburg.de>
"""

import re
import argparse
import pickle

from inverted_index import InvertedIndex  # NOQA


def read_benchmark(file_name):
    """
    Read a benchmark from the given file. The expected format of the file
    is one query per line, with the ids of all documents relevant for that
    query, like: <query>TAB<id1>WHITESPACE<id2>WHITESPACE<id3> ...

    >>> benchmark = read_benchmark("example-benchmark.tsv")
    >>> sorted(benchmark.items())
    [('animated film', {1, 3, 4}), ('short film', {3, 4})]
    """
    benchmark = {}

    with open(file_name, "r", encoding="utf-8") as f:
        for line in f:
            # Split the line into the query and the groundtruth part.
            query, gt = line.strip().split('\t')
            # Split the groundtruth part into ids and store them as a set.
            benchmark[query] = {int(x) for x in gt.split(" ")}

    return benchmark


def evaluate(ii, benchmark, verbose=True):
    """
    Evaluate the given inverted index against the given benchmark as
    follows. Process each query in the benchmark with the given inverted
    index and compare the result list with the groundtruth in the
    benchmark. For each query, compute and print (if verbose=True) the
    measure P@3, P@R and AP as well as mean P@3, mean P@R and mean AP.
    Return a dictionary with one entry for each query and one entry for the
    mean. The keys are the keywords of the query (or "mean" for the mean) and
    values are dictionaries with an entry "precision", which contains lists of
    the measures. The dictionaries for the queries also contain the keys
    "result_ids" (where the value is a list of document ids with the results
    returned by the inverted index) and "relevant_ids" (where the value is a
    set of the relevant ids for this query).
    >>> ii = InvertedIndex()
    >>> ii.read_from_file("example.tsv", b=0.75, k=1.75, verbose=False)
    >>> benchmark = read_benchmark("example-benchmark.tsv")
    >>> evaluation = evaluate(ii, benchmark, verbose=False)
    >>> [round(x, 3) for x in evaluation["mean"]["precision"]]
    [0.667, 0.833, 0.694]
    >>> evaluation["animated film"]["result_ids"]
    [2, 4, 1]
    >>> sorted(list(evaluation["animated film"]["relevant_ids"]))
    [1, 3, 4]
    >>> [round(x, 3) for x in evaluation["animated film"]["precision"]]
    [0.667, 0.667, 0.389]
    """
    evaluation = {}
    sum_p_at_3 = 0
    sum_p_at_r = 0
    sum_ap = 0

    num_queries = len(benchmark)

    for query, relevant_ids in benchmark.items():
        if verbose:
            print("Processing query '%s' ..." % query)

        # Process the query by the index and fetch only the document ids.
        words = [x.lower().strip() for x in re.split("[^A-Za-z]+", query)]
        result_ids = [x[0] for x in ii.process_query(words)]

        # Compute P@3.
        p_at_3 = precision_at_k(result_ids, relevant_ids, 3)
        sum_p_at_3 += p_at_3
        if verbose:
            print("  P@3: %.2f" % p_at_3)

        # Compute P@R.
        r = len(relevant_ids)
        p_at_r = precision_at_k(result_ids, relevant_ids, r)
        sum_p_at_r += p_at_r
        if verbose:
            print("  P@R: %.2f" % p_at_r)

        # Compute AP.
        ap = average_precision(result_ids, relevant_ids)
        sum_ap += ap
        if verbose:
            print("  AP: %.2f" % ap)

        evaluation[query] = {"precision": [p_at_3, p_at_r, ap],
                             "result_ids": result_ids,
                             "relevant_ids": relevant_ids}

    # Compute MP@3.
    mp_at_3 = sum_p_at_3 / num_queries
    # Compute MP@R.
    mp_at_r = sum_p_at_r / num_queries
    # Compute MAP.
    map_value = sum_ap / num_queries
    evaluation["mean"] = {"precision": [mp_at_3, mp_at_r, map_value]}
    if verbose:
        print("Mean results:")
        print("  MP@3: %s" % round(mp_at_3, 3))
        print("  MP@R: %s" % round(mp_at_r, 3))
        print("  MAP:  %s" % round(map_value, 3))

    return evaluation


def precision_at_k(result_ids, relevant_ids, k):
    """
    Compute the measure P@k for the given list of result ids as it was
    returned by the inverted index for a single query, and the given set of
    relevant document ids.

    Note that the relevant document ids are 1-based (as they reflect the
    line number in the dataset file).

    >>> precision_at_k([5, 3, 6, 1, 2], {1, 2, 5, 6, 7, 8}, k=0)
    0
    >>> precision_at_k([5, 3, 6, 1, 2], {1, 2, 5, 6, 7, 8}, k=4)
    0.75
    >>> precision_at_k([5, 3, 6, 1, 2], {1, 2, 5, 6, 7, 8}, k=8)
    0.5
    """
    if k == 0:
        return 0

    num_relevant_result_ids = 0
    for i in range(0, min(len(result_ids), k)):
        if result_ids[i] in relevant_ids:
            num_relevant_result_ids += 1
    return num_relevant_result_ids / k


def average_precision(result_ids, relevant_ids):
    """
    Compute the average precision (AP) for the given list of result ids as
    it was returned by the inverted index for a single query, and the given
    set of relevant document ids.

    Note that the relevant document ids are 1-based (as they reflect the
    line number in the dataset file).

    >>> average_precision([7, 17, 9, 42, 5], {5, 7, 12, 42})
    0.525
    """

    sum_ap = 0
    for i in range(0, len(result_ids)):
        if result_ids[i] in relevant_ids:
            sum_ap += precision_at_k(result_ids, relevant_ids, i + 1)
    return sum_ap / len(relevant_ids)


def main(precomputed_file, benchmark_file):
    """
    Evaluate a precomputed inverted index on a benchmark.
    Save the evaluation results in a pickle file in a dictionary (see
    "evaluate" for more information).
    """
    # Create the precomputed inverted index from the given file.
    print("Reading from file '%s'..." % precomputed_file)
    index = pickle.load(open(precomputed_file, "rb"))

    # Read the benchmark.
    print("Reading benchmark from file '%s'..." % benchmark_file)
    benchmark = read_benchmark(benchmark_file)

    # Evaluate the the inverted index against the benchmark.
    evaluation = evaluate(index, benchmark)

    new_name = (benchmark_file.replace("input", "output")
                              .replace(".tsv", "_")) + "evaluation.pkl"
    print(f"Saving evaluation data as {new_name}.")
    pickle.dump(evaluation,
                open(new_name, "wb"))


if __name__ == "__main__":
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description="""Evaluate an inverted index
            against a benchmark. Compute the measures precision at 3, precision
            at R and average precision. Save the data from the evaluation using
            pickle.""")
    parser.add_argument("precomputed_file", type=str, help="""Pickle file
            containing a precomputed inverted index. To generate such a file,
            use 'inverted_index.py'.""")
    parser.add_argument("benchmark_file", type=str, help="""File containing the
            benchmark. The expected format of the file is one query per line,
            with the ids of all documents relevant for that query, like:
            <query>TAB<id1>WHITESPACE<id2>WHITESPACE<id3> ...""")
    args = parser.parse_args()
    precomputed_file = args.precomputed_file
    benchmark_file = args.benchmark_file
    main(precomputed_file, benchmark_file)
