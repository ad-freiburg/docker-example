"""
Copyright 2017, University of Freiburg
Chair of Algorithms and Data Structures.
Hannah Bast <bast@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
"""

import re
import readline  # NOQA
import sys
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
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <precomputed_ii_file>")
        sys.exit()

    precomputed_file = sys.argv[1]
    main(precomputed_file)
