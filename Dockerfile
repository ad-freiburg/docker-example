FROM python:3.8
LABEL maintainer="Theresa Klumpp <klumppt@cs.uni-freiburg.de>"
RUN apt-get update && apt-get install -y make vim bash-completion && rm -rf /var/lib/apt/lists/*
COPY requirements.txt bashrc ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir repro-example
WORKDIR repro-example
COPY *.py example.tsv example-benchmark.tsv Makefile README.md ./
COPY www/*.html www/*.js www/*.css www/*.md ./www/
CMD ["/bin/bash", "--rcfile", "/bashrc"]

# docker build -t repro-example .
# docker run --rm -it -p 5000:5000 -v /nfs/students/repro-example/input:/repro-example/input:ro -v /nfs/students/repro-example/output:/repro-example/output:rw -v $(pwd)/.docker_bash_history:/root/.bash_history --name repro-example repro-example
