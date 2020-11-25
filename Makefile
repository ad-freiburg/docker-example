TEST_CMD = python3 -m doctest
CHECKSTYLE_CMD = flake8
BENCHMARK = input/movies-benchmark.tsv
PRECOMP_II = output/movies_precomputed_ii.pkl
PRECOMP_EVAL = output/movies-benchmark_evaluation.pkl

help: Makefile
	@echo
	@echo "The following programs are available:"
	@echo "	'inverted_index.py':		construct the inverted index with BM25 scores"
	@echo "	'query_precomputed_ii.py': 	query a precomputed index to find the most relavent hits"
	@echo "	'evaluate_inverted_index.py': 	evaluate an inverted index against a benchmark"
	@echo "	'www/webapp.py': 		build a webapp that nicely presents the evaluation data"
	@echo
	@echo "For more usage information call any of these programs with the -h flag."
	@echo "If you want to learn more and get background information, take a look at the README.md file."
	@echo "Type 'make options' to get some easy options for what to do next."
	@echo 

options: Makefile
	@echo
	@echo "Please use 'make <target>', where <target> is one of the following:"
	@echo
	@fgrep "##" $< | fgrep -v 'fgrep' | sed 's/##//'
	@echo

query:	##	Call "query_precomputed_ii.py" to query the precomputed invertex index of the movies dataset.
##			Files read: 	output/movies_precomputed_ii.pkl
##			Files produced:	None
##			~Time: 		a few seconds to load the ii (~140MB)
	python3 query_precomputed_ii.py $(PRECOMP_II)

webapp:	##	Call "www/webapp.py" to build the webapp that contains an evaluation of the movies benchmark.
## 			Files read: 	output/movies-benchmark_evaluation.pkl
##			Files produced:	None
## 			~Time: 		instant
	python3 www/webapp.py $(PRECOMP_EVAL)


index:	##	Call "inverted_index.py" to build the inverted index from the movies datasest.
##		Note: This has been done already and the corresponding output file is already available.
##			Files read:	input/movies.txt
##			Files produced: output/movies_precomputed_ii.pkl
##			~Time: 		< 1 min (for 44MB file)
	python3 inverted_index.py input/movies.txt -b 0.04 -k 0.7

evaluate:##	Call "evaluate_inverted_index.py" to run the evaluation on the precomputed inverted index
## 		of the movies dataset and show results in the console.
##		Note: The produced file is already available and a better representation of the evaluation
##		is available through the webapp.
##			Files read: 	output/movies_precomputed_ii.pkl, input/movies-benchmark.tsv
##			Files produced:	output/movies-benchmark_evaluation.pkl
##			~Time: 		a few seconds to load the ii (~140MB) plus < 1 sec per query for most queries.
	python3 evaluate_inverted_index.py $(PRECOMP_II) $(BENCHMARK)

check:	##	Test and run checkstyle.
	$(TEST_CMD) *.py
	$(TEST_CMD) www/*.py
	$(CHECKSTYLE_CMD) *.py
	$(CHECKSTYLE_CMD) www/*.py

clean:	##	Remove auto-generated python files (pycache and .pyc files).
	rm -f *.pyc www/*.pyc
	rm -rf __pycache__ www/__pycache__
