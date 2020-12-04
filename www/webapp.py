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
        relevant_ids = evaluation[query]["relevant_ids"]
        num_relevant = len(relevant_ids)
        result_ids = evaluation[query]["result_ids"]
        relevant_in_res = []
        other_relevant = []
        for i in relevant_ids:
            if i in result_ids:
                # doc ids are 1-based
                relevant_in_res.append((docs[i - 1], result_ids.index(i) + 1))
            else:
                other_relevant.append(docs[i - 1])
        relevant_in_res.sort(key=lambda x: x[1])
        top_results = []
        counter = 0
        for i in result_ids[:100]:
            if i in relevant_ids:
                top_results.append([docs[i - 1], "black"])
                counter += 1
                if counter == num_relevant:
                    break
            else:
                top_results.append([docs[i - 1], "red"])
        params["query"] = query
        params["top_results"] = top_results
        params["relevant_in_res"] = relevant_in_res
        params["other_relevant"] = other_relevant
        params["num_relevant"] = num_relevant
    return render_template("index.html",
                           measures=measures,
                           **params)


if __name__ == "__main__":
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description="""Build a webapp that nicely
            presents the evaluation data.""")
    # Positional arguments
    parser.add_argument("doc_file", type=str)
    parser.add_argument("evaluation_file", type=str)
    # Optional arguments
    parser.add_argument("-p", "--port", type=int, default=5000, help="""Port
 for the webapp; should be the container port you published to the docker host
 (default: %(default)s)""")
    args = parser.parse_args()
    eva_file = pickle.load(open(args.evaluation_file, "rb"))
    evaluation = eva_file["evaluation"]
    measures = eva_file["measures"]
    docs = []
    with open(args.doc_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            docs.append(line.split("\t")[0])
    print("\nThe webapp is available at '<host>:<port>', where <host> is the "
          "local computer address and <port> is the port you mapped to the "
          "container port.\n")
    app.run(port=args.port, host="0.0.0.0", debug=True)
