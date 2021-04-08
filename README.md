# Reproducibility Example

This is a project to help you get to know [docker](https://www.docker.com/) better and get familiar with our [reproducibility guidelines](https://ad-wiki.informatik.uni-freiburg.de/teaching/Reproducibility).

## Getting started

This project is designed to be used with [docker](https://www.docker.com/) or [wharfer](https://github.com/ad-freiburg/wharfer).

Use the following commands (you can also find them at the end of the [Dockerfile](Dockerfile)) to build an image and run a container:

```
docker build -t repro-example .
docker run --rm -it -p 5000:9999 -v /nfs/students/repro-example/input:/repro-example/input:ro -v /nfs/students/repro-example/output:/repro-example/output:rw -v $(pwd)/.docker_bash_history:/root/.bash_history --name repro-example repro-example
```

## Features

Here is a list of tips and features you can learn in this example on top of the basics provided in our [simple Docker example](https://ad-wiki.informatik.uni-freiburg.de/teaching/DockerExample):
+ Docker
  + The compulsory `FROM` instruction at the beginning of your Dockerfile specifies the parent image.
    By using `FROM python` instead of `FROM ubuntu`, installing python is not neccessary anymore.
    However, with the python parent image, many features like `bash-completion` have to be installed manually, if we desire to use them.
    Even though ubuntu or python are probably well suited for your project at our chair, [here](https://hub.docker.com/search?q=&type=image&image_filter=official) is a list of official images you can use.
  + To make a port available to services outside of Docker, use the `-p` flag.
    The command `-p <host_port>:<container_port>` publishes `<container_port>` to the outside world and maps it to `<host_port>` on your machine.
    In a nutshell: Anything you now run on `<container_port>` inside the docker container is available on `<host_port>` outside of Docker.
  + The fact that Docker forgets your history of commands every time you start/stop a container, can be quite annoying.
    With a simple trick that you can see in this example, you can make docker remember your bash history.
    Create an empty file `.docker_bash_history` and mount it to `/root/.bash_history` with the -v flag.
    This means that your bash history is mounted to a file outside the container and is therefore saved after leaving the container.
    Make sure the file already exists when starting the container, since Docker will otherwise create a directory (instead of a file).
+ Python
  + Note that when running keyword search with 'query.py', you can get your last query by entering the Up key.
    A simple `import readline` enables this history-feature.
    This is very useful in many applications.
  + In cases like the `import readline`, use `# NOQA` after the import to prevent flake8 to return an 'imported but unused' message.
+ Other
  + Use `##` with `grep` and `sed` in the [Makefile](Makefile) to print the help message.
    This means the help message for a target can be located with the target itself, which makes it easier to keep track of the help messages when targets are added, changed or deleted.

If you have any questions about docker, use our [Docker Forum](https://daphne.informatik.uni-freiburg.de/forum/viewforum.php?f=1083).

# Inverted Index

The project contains programs to constuct, query and evaluate an inverted index.

An inverted list for a word is a sorted list of ids of records containing that word.
An inverted index is a map from all words to their inverted list.
We can use an inverted index to perform keyword search on a collection of text documents.
If you want to get more familiar with the topic and get more background information,
take a look at lectures 1 and 2 of the Information Retrieval lecture
[here](https://ad-wiki.informatik.uni-freiburg.de/teaching/InformationRetrievalWS1920 "Information Retrieval").

What follows are short descriptions of what the available programs do, what files they require and output and which precomputed files are available to use.
For more details, call each program with the '-h'-flag to get usage information.

## Creating an Inverted Index

The program 'inverted_index.py' will create an inverted index from a given input file and serialize it using [Pickle](https://docs.python.org/3/library/pickle.html).

Usage: `python3 inverted_index.py doc_file`

The expected format of the input file is one document per line, in the format \<title\>TAB\<description\>.
A file 'movies.tsv' in the expected format is available in '/nfs/students/repro-example/input'.
It contains 107,769 movies with title and description.
The program will automatically save the inverted index using [Pickle](https://docs.python.org/3/library/pickle.html).
The output file will have the same base name, appended by 'precomputed_ii.pkl'

*Note: Since building an inverted index takes a long time, a file ('movies_precomputed_ii.pkl') with a precomputed inverted index is already available in '/nfs/students/repro-example/output'.
This means you do not have to run this program on the movies dataset.*

## Keyword search on the Inverted Index

Run 'query.py' to perform your own keyword search on an inverted index.
For any amount of entered words, it returns movies whose description got the highest BM25 scores, that is
BM25 = tf * (k+1) / (k * (1 - b + b * DL/AVDL) + tf) * log2(N/df),
where tf is the term frequency, DL is the document length, AVDL is the average document length, N is the total number of documents and df is the number of documents that contain the word.
Moreover, k and b are parameters to be chosen.
You can find more background information about the BM25 scores in [lecture 2](https://daphne.informatik.uni-freiburg.de/ws1920/InformationRetrieval/svn/public/slides/lecture-02.pdf) of the Information Retrieval lecture.

Usage: `python3 query.py precomputed_file`

Here, 'precomputed_file' is a [Pickle](https://docs.python.org/3/library/pickle.html) file containing the precomputed inverted index.
It expects a file as produced by 'inverted_index.py'.
For the movies dataset, this file has already been precomputed and is available in '/nfs/students/repro-example/output'.
The parameters k and b from the BM25 formula above can be changed for each query (default: b=0.75, k=1.75).
This is explained in more detail upon starting the program.

## Evaluating the Inverted Index

To evaluate an inverted index against a benchmark and compute the ranking of the result list, use 'evaluate.py'.

Usage: `python3 evaluate.py precomputed_file benchmark_file [-b B [B ...]] [-k K [K ...]]`

Here, 'precomputed_file' is a [Pickle](https://docs.python.org/3/library/pickle.html) file containing the precomputed inverted index.
It expects a file as produced by 'inverted_index.py'.
For the movies dataset, this file has already been precomputed and is available in '/nfs/students/repro-example/output'.
The second input 'benchmark_file' is the file containing the benchmark.
The expected format of this file is one query per line, with the ids of all documents relevant for that query, like:
\<query\>TAB\<id1\>WHITESPACE\<id2\>WHITESPACE\<id3\> ...
A file 'movies-benchmark.tsv' in the expected format is available in '/nfs/students/docker-example/input'.
It is suitable for the movies dataset and contains 12 queries.
You can choose any number of pairs b and k you want to run the evaluation on.
Make sure you pass the same number of arguments for b and k.
For example, if you want to run the evaluation in two modes; first, with k=0.4 and b=0.7 and second, with k=inf and b=0, use:

`python3 evaluate.py output/movies_precomputed_ii.pkl input/movies-benchmark.tsv -k 0.4 inf -b 0.7 0`

The default uses three modes: binary (k=0, b=0), standard setting for BM25 (k=1.75, b=0.75) and normal tf.idf (k=inf, b=0).
The program automatically saves the data of the evaluation as a tsv-file.
The output file will have the same base name as the benchmark file, appended by 'evaluation.tsv'.

*Note: Since evaluating an inverted index takes a long time, a file ('movies-benchmark_evaluation.tsv') with a precomouted evaluation on the three default modes is already available in '/nfs/students/repro-example/output'.
This means you do not have to run this program on the movies dataset unless you would like to evaluate a different mode.*

## Building the webapp

You can build a webapp that nicely outputs an extensive evaluation using the python http.server.

You need the following files available in order to run the webapp properly:

+ ./input/movies.tsv (the tsv file we provided for you)
+ ./output/movies-benchmark_evaluation.tsv (a tsv file as produced by 'evaluate.py')

Both files are available in the NFS folder.
If you are using docker/wharfer (and you should!), they are mounted to the expected directory, if you used the commands above.
You can then build the webapp:

Usage: `python3 -m http.server <port>`

where <port> is the port for the webapp.
If you are using docker/wharfer, this should be the container port you published to the docker host (default: 9999).
The webapp is then avaiable at '<host>:<host_port>/www',
where <host> is the local computer address ('<machine>.informatik.privat' on our machines)
and <host_port> is the port you maped to the docker container port (default: 5000).
