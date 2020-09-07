FROM python:3.6
LABEL maintainer="Sam Sample <s.sample@ma.il>"
RUN apt-get update && apt-get install -y make vim && rm -rf /var/lib/apt/lists/*
COPY *.py *.txt Makefile README.md bashrc ./
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["/bin/bash", "--rcfile", "bashrc"]

# docker build -t sam-sample-project .
# docker run -it -v $(pwd)/path/to/input:/path/to/input:ro -v $(pwd)/path/to/output:/path/to/output:rw sam-sample-project
