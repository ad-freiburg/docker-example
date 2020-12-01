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
    details = None
    if "details" in user_input:
        details = user_input["details"]
    return render_template("index.html",
                           measures=measures,
                           details=details)


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
    eva = pickle.load(open(args.eval_path, "rb"))
    benchmark = eva["benchmark"]
    measures = eva["measures"]
    # ii = pickle.load(open(args.ii_path, "rb"))
    # docs = [item[0] for item in ii.docs]  # For translating ids into doc titles
    docs = []
    with open(args.ii_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            docs.append(line.split("\t")[0])
    print("\nThe webapp is available at '<host>:<port>', where <host> is the "
          "local computer address and <port> is the port you mapped to the "
          "container port.\n")
    app.run(port=args.port, host="0.0.0.0", debug=True)
