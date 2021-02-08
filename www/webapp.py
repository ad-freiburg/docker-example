"""
Copyright 2020, University of Freiburg
Chair of Algorithms and Data Structures.
Theresa Klumpp <klumppt@cs.uni-freiburg.de>
"""

import pickle
import argparse
from flask import Flask, render_template, request, url_for  # NOQA


app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    user_input = request.args
    params = {}
    if "details" in user_input:

        query = user_input["details"]

        # Split the relevant documents into "in result" and "not in result".
        relevant = {"in results": [], "not in res": []}
        for i in evaluation[query]["relevant_ids"]:
            if i in evaluation[query]["result_ids"]:
                relevant["in results"].append(i)
            else:
                relevant["not in res"].append(i)

        # Remove the entry, if there are no relevant titles not in the result.
        if relevant["not in res"] == []:
            relevant.pop("not in res")

        params["query"] = query
        params["result_ids"] = evaluation[query]["result_ids"]
        params["relevant"] = relevant
        params["num_rel"] = len(evaluation[query]["relevant_ids"])
        params["docs"] = docs
    return render_template("index.html",
                           measures=measures,
                           **params)


if __name__ == "__main__":
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description="""Build a webapp that nicely
            presents the evaluation data.""")
    # Positional arguments
    parser.add_argument("doc_file", type=str, help="""File containing the
            documents. The expected format of the file is one document per
            line, in the format <title>TAB<description>.""")
    parser.add_argument("evaluation_file", type=str, help="""Pickle file
            containing an evaluation. To generate such a file, use
            'evaluate.py'""")
    # Optional arguments
    parser.add_argument("-p", "--port", type=int, default=5000, help="""Port
 for the webapp; should be the container port you published to the docker host
 (default: %(default)s)""")
    args = parser.parse_args()
    evaluation = pickle.load(open(args.evaluation_file, "rb"))

    # This should be removed soon!!
    measures = dict()
    for query in evaluation:
        measures[query] = evaluation[query]["precision"]

    docs = []
    with open(args.doc_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            docs.append(line.split("\t")[0])
    print("\nThe webapp is available at '<host>:<port>', where <host> is the "
          "local computer address and <port> is the port you mapped to the "
          "container port.\n")
    app.run(port=args.port, host="0.0.0.0", debug=True)
