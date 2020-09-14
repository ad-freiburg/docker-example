"""
Copyright 2020, University of Freiburg
Chair of Algorithms and Data Structures.
Theresa Klumpp <klumppt@cs.uni-freiburg.de>
"""

import pickle
import sys
from flask import Flask, render_template, request, url_for  # NOQA


app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", evaluation=evaluation)


@app.route("/test")
def test():
    return render_template("test.html")


if __name__ == "__main__":
    if len(sys.argv) > 3 or len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <evaluation_file> [port]")
        exit(1)
    evaluation_file = sys.argv[1]
    if len(sys.argv) == 3:
        port = int(sys.argv[2])
    else:
        port = 5000
    evaluation = pickle.load(open(evaluation_file, "rb"))
    app.run(port=port, host="0.0.0.0", debug=True)
