"""
Copyright 2020, University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
Theresa Klumpp <klumppt@cs.uni-freiburg.de>
"""

import re
import sys
import pickle
import readline  # NOQA
from inverted_index import InvertedIndex  # NOQA


def intersect(list1, list2):
    """
    Computes the intersection of two given (sorted) inverted lists in linear
    time (linear in the total number of elements in the two lists).

    >>> intersect([1, 5, 7], [2, 4])
    []
    >>> intersect([1, 2, 5, 7], [1, 3, 5, 6, 7, 9])
    [1, 5, 7]
    """
    i = 0  # The pointer in the first list.
    j = 0  # The pointer in the second list.
    result = []

    while i < len(list1) and j < len(list2):
        if list1[i] == list2[j]:
            result.append(list1[i])
            i += 1
            j += 1
        elif list1[i] < list2[j]:
            i += 1
        else:
            j += 1

    return result


def process_query(ii, keywords):
    """
    Processes the given keyword query as follows: Fetches the inverted list for
    each of the keywords in the given query and computes the intersection of
    all inverted lists (which is empty, if there is a keyword in the query
    which has no inverted list in the index).

    >>> from inverted_index import InvertedIndex
    >>> ii = InvertedIndex("example.txt")
    >>> process_query(ii, [])
    []
    >>> process_query(ii, ["doc", "movie"])
    [1, 3]
    >>> process_query(ii, ["doc", "movie", "comedy"])
    []
    """
    if not keywords:
        return []

    # Fetch the inverted lists for each of the given keywords.
    lists = []
    for keyword in keywords:
        if keyword in ii.inverted_lists:
            lists.append(ii.inverted_lists[keyword])
        else:
            # We can abort, because the intersection is empty
            # (there is no inverted list for the word).
            return []

    # Compute the intersection of all inverted lists.
    if len(lists) == 0:
        return []

    intersected = lists[0]
    for i in range(1, len(lists)):
        intersected = intersect(intersected, lists[i])

    return intersected


def render_output(ii, record_ids, keywords, k=3):
    """
    Renders the output for the top-k of the given record_ids. Fetches the
    the titles and descriptions of the related records and highlights
    the occurences of the given keywords in the output, using ANSI escape
    codes.
    """

    # Compile a pattern to identify the given keywords in a string.
    p = re.compile('\\b(' + '|'.join(keywords) + ')\\b', re.IGNORECASE)

    # Output at most k matching records.
    for i in range(min(len(record_ids), k)):
        title, desc = ii.records[record_ids[i] - 1]  # ids are 1-based.

        # Highlight the keywords in the title in bold and red.
        title = re.sub(p, "\033[0m\033[1;31m\\1\033[0m\033[1m", title)

        # Print the rest of the title in bold.
        title = "\033[1m%s\033[0m" % title

        # Highlight the keywords in the description in red.
        desc = re.sub(p, "\033[31m\\1\033[0m", desc)

        print("\n%s\n%s" % (title, desc))

    print("\n# total hits: %s." % len(record_ids))


def main(precomputed_file):
    # Load inverted index from the precomputed file.
    print(f"Loading file {precomputed_file}.")
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
        record_ids = process_query(ii, keywords)

        # Render the output (with ANSI codes to highlight the keywords).
        render_output(ii, record_ids, keywords)


if __name__ == "__main__":
    # Parse the command line arguments.
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <precomputed_file>")
        sys.exit()
    precomputed_file = sys.argv[1]
    main(precomputed_file)
