TEST_CMD = python3 -m doctest
CHECKSTYLE_CMD = flake8
BENCHMARK = input/movies-benchmark.tsv
PRECOMP_II = output/movies_precomputed_ii.pkl
PRECOMP_EVAL = output/movies-benchmark_evaluation.pkl

help: Makefile
	@echo "You are most likely to be interested in using 'make <target>', where <target> is one of the following:"
	@echo
	@grep "##" $< | grep -v 'grep' | sed 's/##//'
	@echo
	@echo "For more information about each target, use 'make help-<target>' for any of the targets above."
	@echo "To get a full list of targets, you can use the autocompletion, i.e. type 'make ' and enter TAB."

index:	##	Create the inverted index from the movies dataset.
##		Note: This has been done already and the corresponding output file is already available.
	python3 inverted_index.py input/movies.tsv -b 0.04 -k 0.7

help-index:
	@echo "About 'make index':"
	@echo "	Calls:		inverted_index.py"
	@echo "	Files read:	input/movies.tsv"
	@echo "	Files produced:	output/movies_precomputed_ii.pkl"
	@echo "	~Time: 		< 1 min (for 44MB file)"
	@echo "For more usage information about 'inverted_index.py', call it with the '-h' flag."
	@echo "For more background information, look at the 'Creating an Inverted Index' section in the README.md."

query:	##	Query the precomputed invertex index of the movies dataset.
	python3 query.py $(PRECOMP_II)

help-query:
	@echo "About 'make query':"
	@echo "	Calls:		query.py"
	@echo "	Files read: 	output/movies_precomputed_ii.pkl"
	@echo "	Files produced:	None"
	@echo "	~Time: 		a few seconds to load the inverted index (~140MB)"
	@echo "For more usage information about 'query_precomputed_ii.py', call it with the '-h' flag."
	@echo "For more background information, look at the 'Keyword search on the Inverted Index' section in the README.md."

evaluate:##	Run an evaluation on the precomputed inverted index of the movies dataset and show results
##		in the console.
##		Note: The produced file is already available and a better representation of the evaluation
##		is available through the webapp.
	python3 evaluate.py $(PRECOMP_II) $(BENCHMARK)

help-evaluate:
	@echo "About 'make evaluate':"
	@echo "	Calls:		evaluate_inverted_index.py"
	@echo "	Files read: 	output/movies_precomputed_ii.pkl, input/movies-benchmark.tsv"
	@echo "	Files produced:	output/movies-benchmark_evaluation.pkl"
	@echo "	~Time: 		a few seconds to load the ii (~140MB) plus < 1 sec per query for most queries."
	@echo "For more usage information about 'evaluate_inverted_index.py', call it with the '-h' flag."
	@echo "For more background information, look at the 'Evaluating the Inverted Index' section in the README.md."

webapp:	##	Build a webapp that contains an evaluation of the movies benchmark.
	python3 www/webapp.py input/movies.tsv $(PRECOMP_EVAL)

help-webapp:
	@echo "About 'make webapp':"
	@echo "	Calls:		www/webapp.py"
	@echo "	Files read: 	output/movies-benchmark_evaluation.pkl"
	@echo "	Files produced:	None"
	@echo "	~Time: 		instant"
	@echo "For more usage information about 'webapp.py', call it with the '-h' flag."
	@echo "For more background information, look at the 'Building the webapp' section in the README.md."

check:	#	Test and run checkstyle.
	$(TEST_CMD) *.py
	$(TEST_CMD) www/*.py
	$(CHECKSTYLE_CMD) *.py
	$(CHECKSTYLE_CMD) www/*.py

clean:	#	Remove auto-generated python files (pycache and .pyc files).
	rm -f *.pyc www/*.pyc
	rm -rf __pycache__ www/__pycache__
