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
    return render_template("home.html", evaluation=evaluation)


if __name__ == "__main__":
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description="""Build a webapp that nicely
            presents the evaluation data.""")
    # Positional arguments
    parser.add_argument("evaluation_file", type=str, help="""Pickle file
        containing the evaluation. To generate such a file, use
        'evaluate_inverted_index.py'""")
    # Optional arguments
    parser.add_argument("-p", "--port", type=int, default=5000, help="""Port
 for the webapp; should be the container port you published to the docker host
 (default: %(default)s)""")
    args = parser.parse_args()
    evaluation = pickle.load(open(args.evaluation_file, "rb"))
    print("\nThe webapp is available at '<host>:<port>', where <host> is the "
          "local computer address and <port> is the port you mapped to the "
          "container port.\n")
    app.run(port=args.port, host="0.0.0.0", debug=True)
