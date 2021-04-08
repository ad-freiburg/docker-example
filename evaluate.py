"""
Copyright 2017, University of Freiburg
Chair of Algorithms and Data Structures.
Claudius Korzen <korzen@cs.uni-freiburg.de>
Theresa Klumpp <klumppt@cs.uni-freiburg.de>
"""

import re
import argparse
import csv
import pickle
from inverted_index import InvertedIndex, DEFAULT_K, DEFAULT_B  # NOQA


def read_benchmark(file_name):
    """
    Read a benchmark from the given file and construct the ground truth.
    The expected format of the benchmark file is one query per line,
    with the ids of all documents relevant for that query, like:
    <query>TAB<id1>WHITESPACE<id2>WHITESPACE<id3> ...
    >>> benchmark = read_benchmark("example-benchmark.tsv")
    >>> sorted(benchmark.items())
    [('animated film', {1, 3, 4}), ('short film', {3, 4})]
    """
    benchmark = dict()

    with open(file_name, "r", encoding="utf-8") as f:
        for line in f:
            # Split the line into the query and the ground truth part.
            query, gt = line.strip().split('\t')
            # Split the ground truth part into ids and store them as a set.
            benchmark[query] = {int(x) for x in gt.split(" ")}

    return benchmark


def evaluate(ii, benchmark, k, b, verbose=True):
    """
    Run the given inverted index against the given benchmark. Compute the
    "raw" data (i.e. the result list it returns) with the given k and b.
    >>> ii = InvertedIndex()
    >>> ii.read_from_file("example.tsv", verbose=False)
    >>> benchmark = read_benchmark("example-benchmark.tsv")
    >>> evaluation = evaluate(ii, benchmark, k=1.75, b=0.75, verbose=False)
    >>> evaluation["animated film"]
    [2, 4, 1]
    """
    res = dict()

    for query in benchmark:
        if verbose:
            print("\tQuery: '%s'" % query)

        # Process query with the given k and b and fetch only the doc ids.
        words = [x.lower().strip() for x in re.split("[^A-Za-z]+", query)]
        result_ids = [x[0] for x in ii.process_query(words, k=k, b=b)]

        res[query] = result_ids
    return res


def main(precomputed_file, benchmark_file, k_list, b_list):
    """
    Evaluate a precomputed inverted index on a benchmark.
    Save the evaluation results in a pickle file in a dictionary (see
    "evaluate" for more information).
    """
    # Create the precomputed inverted index from the given file.
    print("Constructing inverted index from file '%s'..." % precomputed_file)
    ii = pickle.load(open(precomputed_file, "rb"))

    # Read the benchmark.
    print("Reading benchmark from file '%s'..." % benchmark_file)
    benchmark = read_benchmark(benchmark_file)
    print()

    # Evaluate the inverted index against the benchmark with the given
    # values for k and b.
    evaluation = []
    print("Starting the evaluation.")
    for k, b in zip(k_list, b_list):
        print(f"Running evaluation with k = {k} and b = {b}:")
        run = [k, b] + list(evaluate(ii, benchmark, k=k, b=b).values())
        evaluation.append(run)

    new_name = (benchmark_file.replace("input", "output")
                              .replace(".tsv", "_evaluation.tsv"))
    print(f"Saving evaluation data as {new_name}.")

    # Create header.
    header = ["k", "b"]
    for query in benchmark:
        header.append(query)

    # Get the ground truth.
    gt = ["ground_truth", ""]
    for query in benchmark:
        gt.append(list(benchmark[query]))

    with open(new_name, "wt") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        for mode in evaluation:
            writer.writerow(mode)
        writer.writerow(gt)


if __name__ == "__main__":
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(
        description="""
        Evaluate the given inverted index against the given benchmark.
        Run the evaluation for each given set of values for b and k.
        Make sure you enter the same amount of arguments for b and k.
        Save the ground truth and the evaluation data using pickle.
        """,
        epilog=f"""
        If no b and k are given, the evaluation is run with the following
        three modes:
        b={DEFAULT_B} and k={DEFAULT_K} (standard setting for BM25),
        b=0 and k=0 (binary),
        b=0 and k=inf (normal tf.idf).
        """)

    parser.add_argument("precomputed_file", type=str, help="""Pickle file
        containing a precomputed inverted index. To generate such a file,
        use 'inverted_index.py'.""")
    parser.add_argument("benchmark_file", type=str, help="""File containing the
        benchmark. The expected format of the file is one query per line,
        with the ids of all documents relevant for that query, like:
        <query>TAB<id1>WHITESPACE<id2>WHITESPACE<id3> ...""")
    parser.add_argument("-b", type=float, nargs="*",
                        default=[DEFAULT_B, 0.0, 0.0], help="""
        The b from the BM25 formula.
        Enter a list of floats to run the evaluation with different parameters.
        (default: %(default)s)""")
    parser.add_argument("-k", type=float, nargs="*",
                        default=[DEFAULT_K, 0.0, float("inf")], help="""
        The k from the BM25 formula.
        Enter a list of floats to run the evaluation with different parameters.
        (default: %(default)s)""")

    args = parser.parse_args()

    if len(args.k) != len(args.b):
        parser.exit(
            message="Need the same number of arguments for b and k, " +
                    f"but got {len(args.b)} for b and {len(args.k)} for k.\n")

    main(args.precomputed_file,
         args.benchmark_file,
         k_list=args.k,
         b_list=args.b)
