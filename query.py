"""
Copyright 2017, University of Freiburg
Chair of Algorithms and Data Structures.
Hannah Bast <bast@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
Theresa Klumpp <klumppt@cs.uni-freiburg.de>
"""

import re
import readline  # NOQA
import argparse
import pickle
from inverted_index import InvertedIndex, DEFAULT_B, DEFAULT_K  # NOQA


BOLD = '\033[1m'
END = '\033[0m'


def main(precomputed_file):

    # Create a new inverted index from the given file.
    print("Reading from file '%s'..." % precomputed_file, end="\r")
    ii = pickle.load(open(precomputed_file, "rb"))
    print("Reading from file '%s'...Done!\n" % precomputed_file)

    b = DEFAULT_B
    k = DEFAULT_K
    num_res = 3  # number of results shown

    print("Query the inverted index to find the most relevant hits.")
    print("Enter any number of keywords.")
    print(f"Type {BOLD}'num_res=<n>'{END} to change the number of "
          f"results presented to you.")
    print(f"Type {BOLD}'k=<k>'{END} or {BOLD}'b=<b>'{END} to change the value "
          f"of k or b for the BM25 scores.")
    print(f"Default values: num_res={num_res}, k={k}, b={b}.")
    print("Use ctrl+d to leave the program.")

    while True:

        try:
            # Ask the user for a keyword query.
            query = input("\nYour keyword query: ")
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        # Check whether user wants to change number of results shown.
        m = re.match(r"num_res=([0-9]+)$", query)
        if m:
            num_res = int(m.group(1))
            print(f"Changed the number of results shown to {num_res}.")
            continue

        # Check whether user wants to change k.
        m = re.match(r"k=([0-9.]+|inf)$", query)
        if m:
            k = float(m.group(1))
            print(f"Changed k to {k}.")
            continue

        # Check whether user wants to change b.
        m = re.match(r"b=([0-9.]+)$", query)
        if m:
            b = float(m.group(1))
            print(f"Changed b to {b}.")
            continue

        # Split the query into keywords.
        keywords = [x.lower().strip() for x in re.split("[^A-Za-z]+", query)]

        # Process the keywords.
        postings = ii.process_query(keywords, k=k, b=b)

        # Render the output (with ANSI codes to highlight the keywords).
        ii.render_output(postings, keywords, num_res)


if __name__ == "__main__":

    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description="""Query a precomputed
        inverted index to find the most relavent hits.""")
    parser.add_argument("precomputed_file", type=str, help="""Pickle file
        containing a precomputed inverted index. To generate such a file,
        use 'inverted_index.py'.""")
    args = parser.parse_args()

    main(args.precomputed_file)
