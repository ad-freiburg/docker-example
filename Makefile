TEST_CMD = python3 -m doctest
CHECKSTYLE_CMD = flake8
BENCHMARK = input/movies-benchmark.tsv
PRECOMP_II = output/movies_precomputed_ii.pkl
PRECOMP_EVAL = output/movies-benchmark_evaluation.pkl

help: Makefile
	@echo
	@echo "Please use 'make <target>', where <target> is one of the following:"
	@echo
	@fgrep "##" $< | fgrep -v 'fgrep' | sed 's/##//'
	@echo
	@echo "For usage help call a program with the -h flag."
	@echo "Take a look at the README file for more detailed information."
	@echo

all:	##	Test and run checkstyle.
	$(TEST_CMD) *.py
	$(TEST_CMD) www/*.py
	$(CHECKSTYLE_CMD) *.py
	$(CHECKSTYLE_CMD) www/*.py

clean:	##	Remove auto-generated files.
	rm -f *.pyc
	rm -rf __pycache__

index:	##	Build the inverted index.
##			Files read:	input/movies.txt
##			Files produced: output/movies_precomputed_ii.pkl
##			~Time: 		< 1 min
	python3 inverted_index.py input/movies.txt -b 0.04 -k 0.7

query:	##	Query the precomputed inverted index.
##			Files read: 	output/movies_precomputed_ii.pkl 
##			Files produced:	None
##			~Time: 		a few seconds
	python3 query_precomputed_ii.py $(PRECOMP_II)

evaluate:##	Evaluate precomputed inverted index and show results in the console.
##			Files read: 	output/movies_precomputed_ii.pkl, input/movies-benchmark.tsv
##			Files produced:	output/movies-benchmark_evaluation.pkl
##			~Time: 		< 20 sec
	python3 evaluate_inverted_index.py $(PRECOMP_II) $(BENCHMARK)

webapp:	##	Build the webapp.
## 			Files read: 	output/movies-benchmark_evaluation.pkl
##			Files produced:	None
## 			~Time: 		instant
	python3 www/webapp.py $(PRECOMP_EVAL)
