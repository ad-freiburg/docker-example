"""
Copyright 2017, University of Freiburg
Chair of Algorithms and Data Structures.
Hannah Bast <bast@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
Theresa Klumpp <klumppt@cs.uni-freiburg.de>
"""

import math
import re
import argparse
import pickle


DEFAULT_B = 0.75
DEFAULT_K = 1.75


class InvertedIndex:
    """
    A simple inverted index that uses BM25 scores.
    """

    def __init__(self):
        """
        Creates an empty inverted index.
        """
        self.inverted_lists = {}  # The inverted lists with term frequencies.
        self.docs = []  # The docs, each in form (title, description).
        self.doc_lengths = []  # The document lengths (= number of words).
        self.n = 0  # The total number of documents.
        self.avdl = 0  # The average document length.

    def read_from_file(self, file_name, verbose=True):
        """
        Construct the inverted index from the given file. The expected format
        of the file is one document per line, in the format
        <title>TAB<description>. Each entry in the inverted list associated to
        a word should contain a document id and a term frequency score.

        Compute the inverted lists with tf scores (that is the number of
        occurrences of the word within the <title> and the <description> of a
        document). Further, compute the document length (DL) for each document
        (that is the number of words in the <title> and the <description> of a
        document). Afterwards, compute the average document length (AVDL).

        On reading the file, use UTF-8 as the standard encoding. To split the
        texts into words, use the method introduced in the IR lecture. Make
        sure that you ignore empty words.

        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example.tsv",
        ...                   verbose=False)
        >>> sorted(ii.inverted_lists.items())
        ... # doctest: +NORMALIZE_WHITESPACE
        [('animated', [(1, 1), (2, 1), (4, 1)]),
         ('animation', [(3, 1)]),
         ('film', [(2, 1), (4, 1)]),
         ('movie', [(1, 2), (2, 1), (3, 1), (4, 1)]),
         ('non', [(2, 1)]),
         ('short', [(3, 1), (4, 2)])]
        >>> ii.n
        4
        >>> ii.avdl
        3.75
        >>> ii.doc_lengths
        [3, 4, 3, 5]
        """

        # First pass: Compute (1) the inverted lists with tf scores and (2) the
        # document lengths.
        with open(file_name, "r", encoding="utf-8") as f:
            doc_id = 0
            for line in f:

                # Store the doc as a tuple (title, description).
                # Do this before line.strip, because some docs are missing the
                # description (but still have the TAB).
                self.docs.append(tuple(x.strip() for x in line.split("\t")))

                line = line.strip()

                dl = 0  # Compute the document length (number of words).
                doc_id += 1

                for word in re.split("[^A-Za-z]+", line):
                    word = word.lower().strip()

                    # Ignore the word if it is empty.
                    if len(word) == 0:
                        continue

                    dl += 1

                    if word not in self.inverted_lists:
                        # The word is seen for first time, create new list.
                        self.inverted_lists[word] = [(doc_id, 1)]
                        continue

                    # Get last posting to check if the doc was already seen.
                    last = self.inverted_lists[word][-1]
                    if last[0] == doc_id:
                        # The doc was already seen, increment tf by 1.
                        self.inverted_lists[word][-1] = (doc_id, last[1] + 1)
                    else:
                        # The doc was not already seen, set tf to 1.
                        self.inverted_lists[word].append((doc_id, 1))

                # Register the document length.
                self.doc_lengths.append(dl)

                if verbose:
                    if doc_id % 1000 == 0:
                        print(f"Progress: Read {doc_id:6} documents.",
                              end="\r")

        # Compute N (the total number of documents).
        self.n = len(self.docs)

        if verbose:
            print(f"Progress: Read {self.n:6} documents.")

        # Compute AVDL (the average document length).
        self.avdl = sum(self.doc_lengths) / self.n

    @staticmethod
    def merge(list1, list2):
        """
        Compute the union of the two given inverted lists in linear time
        (linear in the total number of entries in the two lists), where the
        entries in the inverted lists are postings of form (doc_id, bm25_score)
        and are expected to be sorted by doc_id, in ascending order.

        >>> ii = InvertedIndex()
        >>> l1 = ii.merge([(1, 2.1), (5, 3.2)], [(1, 1.7), (2, 1.3), (6, 3.3)])
        >>> [(id, "%.1f" % tf) for id, tf in l1]
        [(1, '3.8'), (2, '1.3'), (5, '3.2'), (6, '3.3')]

        >>> l2 = ii.merge([(3, 1.7), (5, 3.2), (7, 4.1)], [(1, 2.3), (5, 1.3)])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        [(1, '2.3'), (3, '1.7'), (5, '4.5'), (7, '4.1')]
        """
        i = 0  # The pointer in the first list.
        j = 0  # The pointer in the second list.
        result = []

        # Iterate the lists in an interleaving order and aggregate the scores.
        while i < len(list1) and j < len(list2):
            if i < list1[i][0] == list2[j][0]:
                result.append((list1[i][0], list1[i][1] + list2[j][1]))
                i += 1
                j += 1
            elif list1[i][0] < list2[j][0]:
                result.append(list1[i])
                i += 1
            else:
                result.append(list2[j])
                j += 1

        # Append the rest of the first list.
        while i < len(list1):
            result.append(list1[i])
            i += 1

        # Append the rest of the second list.
        while j < len(list2):
            result.append(list2[j])
            j += 1

        return result

    def process_query(self, keywords, k=None, b=None):
        """
        Process the given keyword query as follows: Fetch the inverted list
        with the term frequencies for each of the keywords in the query.
        Compute the BM25 scores with the given k and b. Then compute the union
        of all lists. Sort the resulting list by BM25 scores in descending
        order.

        >>> ii = InvertedIndex()
        >>> ii.inverted_lists = {
        ... "foo": [(1, 1), (3, 2)],
        ... "bar": [(1, 1), (2, 3), (3, 1)],
        ... "baz": [(2, 1)]}
        >>> ii.avdl = 3
        >>> ii.n = 3
        >>> ii.doc_lengths = [3, 4, 2]
        >>> result = ii.process_query(["foo", "bar"], k=0, b=0)
        >>> [(id, "%.2f" % tf) for id, tf in result]
        [(1, '0.58'), (3, '0.58')]
        >>> result = ii.process_query(["foo", "bar"], k=float("inf"), b=0)
        >>> [(id, "%.2f" % tf) for id, tf in result]
        [(3, '1.17'), (1, '0.58')]
        """

        b = DEFAULT_B if b is None else b
        k = DEFAULT_K if k is None else k

        if not keywords:
            return []

        # Fetch the inverted lists with the term frequencies for each of the
        # given keywords and compute the BM25 scores, defined as follows:
        # BM25 = tf * (k + 1) / (k * (1 - b + b * DL / AVDL) + tf) * log2(N/df)
        lists = []
        for keyword in keywords:

            if keyword not in self.inverted_lists:
                continue

            # Compute df (that is the length of the inverted list).
            df = len(self.inverted_lists[keyword])
            idf = math.log(self.n / df, 2)
            bm25_lists = []
            for doc_id, tf in self.inverted_lists[keyword]:
                # Obtain the document length (dl) of the document.
                dl = self.doc_lengths[doc_id - 1]  # doc_id is 1-based.
                # Compute alpha = (1 - b + b * DL / AVDL).
                alpha = 1 - b + (b * dl / self.avdl)
                # Compute tf2 = tf * (k + 1) / (k * alpha + tf).
                tf2 = tf * (1 + (1 / k)) / (alpha + (tf / k)) if k > 0 else 1
                # Compute the BM25 score = tf2 * log2(N/df).
                bm25_lists.append((doc_id, tf2 * idf))
            lists.append(bm25_lists)

        # Compute the union of all inverted lists.
        if len(lists) == 0:
            return []

        union = lists[0]
        for i in range(1, len(lists)):
            union = self.merge(union, lists[i])

        # Filter all postings with BM25 = 0.
        union = [x for x in union if x[1] != 0]

        # Sort the postings by BM25 scores, in descending order.
        return sorted(union, key=lambda x: x[1], reverse=True)

    def render_output(self, postings, keywords, num_res=3):
        """
        Render the output for the top-k of the given postings. Fetch the
        the titles and descriptions of the related docs and highlight the
        occurences of the given keywords in the output, using ANSI escape
        codes.
        """

        # Compile a pattern to identify the given keywords in a string.
        p = re.compile('\\b(' + '|'.join(keywords) + ')\\b', re.IGNORECASE)

        # Output at most k matching docs.
        for i in range(min(len(postings), num_res)):
            doc_id, tf = postings[i]
            title, desc = self.docs[doc_id - 1]  # doc_id is 1-based.

            # Highlight the keywords in the title in bold and red.
            title = re.sub(p, "\033[0m\033[1;31m\\1\033[0m\033[1m", title)

            # Print the rest of the title in bold.
            title = "\033[1m%s\033[0m" % title

            # Highlight the keywords in the description in red.
            desc = re.sub(p, "\033[31m\\1\033[0m", desc)

            print("\n%s\n%s" % (title, desc))

        print("\n# total hits: %s." % len(postings))


def main(file_name):
    # Create a new inverted index from the given file.
    print("Creating an inverted index from file '%s'." % file_name)
    ii = InvertedIndex()
    ii.read_from_file(file_name)

    # Save inverted index using pickle.
    new_name = (file_name.replace("input", "output")
                         .replace(".tsv", "_")) + "precomputed_ii.pkl"
    print("Saving index as '%s'." % new_name)
    pickle.dump(ii, open(new_name, "wb"))


if __name__ == "__main__":
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description="""Construct the inverted
        index with term frequency scores from the given file. Save the inverted
        index using pickle.""")
    # Positional arguments
    parser.add_argument("doc_file", type=str, help="""File to read from. The
            expected format of the file is one document per line, in the format
            <title>TAB<description>.""")
    args = parser.parse_args()
    main(args.doc_file)
