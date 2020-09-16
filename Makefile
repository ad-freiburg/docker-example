TEST_CMD = python3 -m doctest
CHECKSTYLE_CMD = flake8
BENCHMARK = input/movies-benchmark.tsv
PRECOMP_II = output/movies_precomputed_ii.pkl
PRECOMP_EVAL = output/movies-benchmark_evaluation.pkl

help: Makefile
	@echo
	@echo "Please use 'make <target>', where <target> is one of the following:"
	@sed -n 's/^## //gp' $<
	@echo
	@echo "For usage help call a program with the -h flag."
	@echo "Take a look at the README file for more detailed information."
	@echo

## all		Test and run checkstyle.
all:
	$(TEST_CMD) *.py
	$(TEST_CMD) www/*.py
	$(CHECKSTYLE_CMD) *.py
	$(CHECKSTYLE_CMD) www/*.py

## clean		Remove auto-generated files.
clean:
	rm -f *.pyc
	rm -rf __pycache__

## webapp		Build the webapp.
webapp:
	python3 www/webapp.py $(PRECOMP_EVAL)

## query		Query the precomputed inverted index.
query:
	python3 query_precomputed_ii.py $(PRECOMP_II)

## evaluate	Evaluate precomputed inverted index and show results in the console.
evaluate:
	python3 evaluate_inverted_index.py $(PRECOMP_II) $(BENCHMARK)
