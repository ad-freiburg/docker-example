FROM python:3.6
LABEL maintainer="Sam Sample <s.sample@ma.il>"
RUN apt-get update && apt-get install -y make vim && rm -rf /var/lib/apt/lists/*
COPY requirements.txt bashrc ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir docker-example
WORKDIR /docker-example
COPY *.py example.txt example-benchmark.tsv Makefile README.md ./
COPY www/ ./www/
CMD ["/bin/bash", "--rcfile", "/bashrc"]

# docker build -t docker-example .
# docker run --rm -it -p 5000:5000 -v /nfs/students/example-project/input:/docker-example/input:ro -v /nfs/students/example-project/output:/docker-example/output:rw --name docker-example docker-example
# wharfer build -t docker-example . && wharfer run --rm -it -p 5000:5000 -v /nfs/students/example-project/input:/docker-example/input:ro -v /nfs/students/example-project/output:/docker-example/output:rw --name docker-example docker-example
