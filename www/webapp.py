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
        params["query"] = query
        relevant_ids = evaluation[query]["relevant_ids"]
        num_relevant = len(relevant_ids)
        result_ids = evaluation[query]["result_ids"]
        res = []
        other_relevant = []
        for i in relevant_ids:
            if i in result_ids:
                # doc ids are 1-based
                res.append([docs[i - 1], result_ids.index(i) + 1])
            else:
                other_relevant.append(docs[i - 1])
        res.sort(key = lambda x: x[1])
        params["relevant"] = relevant_ids
        top_results = []
        counter = 0
        for i in result_ids[:100]:
            if i in relevant_ids:
                top_results.append([docs[i - 1], "green"])
                counter += 1
                if counter == num_relevant:
                    break
            else:
                top_results.append([docs[i - 1], "red"])
        params["top_results"] = top_results
        params["res"] = res
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
    parser.add_argument("ii_path", type=str)
    parser.add_argument("eval_path", type=str)
    # Optional arguments
    parser.add_argument("-p", "--port", type=int, default=5000, help="""Port
 for the webapp; should be the container port you published to the docker host
 (default: %(default)s)""")
    args = parser.parse_args()
    eva_file = pickle.load(open(args.eval_path, "rb"))
    evaluation = eva_file["evaluation"]
    measures = eva_file["measures"]
    # ii = pickle.load(open(args.ii_path, "rb"))
    # # For translating ids into doc titles:
    # docs = [item[0] for item in ii.docs]
    docs = []
    with open(args.ii_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            docs.append(line.split("\t")[0])
    print("\nThe webapp is available at '<host>:<port>', where <host> is the "
          "local computer address and <port> is the port you mapped to the "
          "container port.\n")
    app.run(port=args.port, host="0.0.0.0", debug=True)
