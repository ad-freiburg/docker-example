"""
Copyright 2020, University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
Theresa Klumpp <klumppt@cs.uni-freiburg.de>
"""

import re
import sys
import pickle


class InvertedIndex:
    """
    A simple inverted index.
    """

    def __init__(self, file_name):
        """
        Creates an empty inverted index.
        """
        self.inverted_lists = {}  # The inverted lists of record ids.
        self.records = []  # The records, each in form (title, description).
        self.read_from_file(file_name)

    def read_from_file(self, file_name):
        """
        Constructs the inverted index from given file in linear time (linear in
        the number of words in the file). The expected format of the file is
        one record per line, in the format <title>TAB<description>.

        Makes sure that each inverted list contains a particular record id at
        most once, even if the respective word occurs multiple time in the same
        record.

        >>> ii = InvertedIndex("example.txt")
        >>> sorted(ii.inverted_lists.items())
        [('a', [1, 2]), ('doc', [1, 2, 3]), ('film', [2]), ('movie', [1, 3])]
        >>> ii.records  # doctest: +NORMALIZE_WHITESPACE
        [('Doc 0', 'A movie movie.'),
         ('Doc 1', 'A film.'),
         ('Doc 2', 'Movie.')]
        """
        with open(file_name, "r") as file:
            record_id = 0
            for line in file:
                line = line.strip()

                record_id += 1

                # Store the record as a tuple (title, description).
                self.records.append(tuple(line.split("\t")))

                for word in re.split("[^A-Za-z]+", line):
                    word = word.lower().strip()

                    # Ignore the word if it is empty.
                    if len(word) == 0:
                        continue

                    if word not in self.inverted_lists:
                        # The word is seen for first time, create a new list.
                        self.inverted_lists[word] = [record_id]
                    elif self.inverted_lists[word][-1] != record_id:
                        # Make sure that the list contains the id at most once.
                        self.inverted_lists[word].append(record_id)


def main(input_file, output_file):
    # Create a new inverted index from the given file.
    print(f"Creating inverted index from file {input_file}.")
    ii = InvertedIndex(input_file)
    print(f"Saving the inverted intex as {output_file}.")
    pickle.dump(ii, open(output_file, "wb"))


if __name__ == "__main__":
    # Parse the command line arguments.
    if len(sys.argv) != 3:
        print(f"Usage: python3 {sys.argv[0]} <input_file> <output_file>")
        sys.exit()
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)
