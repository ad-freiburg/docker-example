"""
Copyright 2017, University of Freiburg
Chair of Algorithms and Data Structures.
Hannah Bast <bast@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
"""

import re
import readline  # NOQA
import argparse
import pickle
from inverted_index import InvertedIndex  # NOQA


def main(precomputed_file):
    # Create a new inverted index from the given file.
    print("Reading from file '%s'." % precomputed_file)
    ii = pickle.load(open(precomputed_file, "rb"))

    while True:
        try:
            # Ask the user for a keyword query.
            query = input("\nYour keyword query: ")
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        # Split the query into keywords.
        keywords = [x.lower().strip() for x in re.split("[^A-Za-z]+", query)]

        # Process the keywords.
        postings = ii.process_query(keywords)

        # Render the output (with ANSI codes to highlight the keywords).
        ii.render_output(postings, keywords)


if __name__ == "__main__":
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description="""Query a precomputed
        inverted index to find the most relavent hits.""")
    parser.add_argument("precomputed_file", type=str, help="""Pickle file
        containing a precomputed inverted index. To generate such a file,
        use 'inverted_index.py'.""")
    args = parser.parse_args()

    main(args.precomputed_file)
