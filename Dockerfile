FROM python:3.6
LABEL maintainer="Sam Sample <s.sample@ma.il>"
RUN apt-get update && apt-get install -y make vim && rm -rf /var/lib/apt/lists/*
COPY requirements.txt bashrc ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir example-project
WORKDIR /example-project
COPY *.py example.txt example-benchmark.tsv Makefile README.md ./
COPY webapp/ ./webapp/
CMD ["/bin/bash", "--rcfile", "/bashrc"]

# docker build -t sam-sample-project .
# docker run -it -p 5000:5000 -v /nfs/students/example-project/input:/example-project/input:ro -v /nfs/students/example-project/output:/example-project/output:rw sam-sample-project
