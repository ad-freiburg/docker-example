FROM python:3.8
LABEL maintainer="Theresa Klumpp <klumppt@cs.uni-freiburg.de>"
RUN apt-get update && apt-get install -y make vim bash-completion && rm -rf /var/lib/apt/lists/*
COPY requirements.txt bashrc ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir docker-example
WORKDIR /docker-example
COPY *.py example.tsv example-benchmark.tsv Makefile README.md ./
COPY www/ ./www/
CMD ["/bin/bash", "--rcfile", "/bashrc"]

# docker build -t docker-example .
# docker run --rm -it -p 5000:5000 -v /nfs/students/example-project/input:/docker-example/input:ro -v /nfs/students/example-project/output:/docker-example/output:rw --name docker-example docker-example
