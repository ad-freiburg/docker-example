TEST_CMD = python3 -m doctest
CHECKSTYLE_CMD = flake8
DOCS = input/movies.tsv
BENCHMARK = input/movies-benchmark.tsv
PRECOMP_II = output/movies_precomputed_ii.pkl
PRECOMP_EVAL = output/movies-benchmark_evaluation.tsv

help: Makefile
	@echo "You are most likely to be interested in using 'make <target>', where <target> is one of the following:"
	@echo
	@grep "##" $< | grep -v 'grep' | sed 's/##//'
	@echo
	@echo "For more information about each target, use 'make help-<target>' for any of the targets above."
	@echo "To get a full list of targets, you can use the autocompletion, i.e. type 'make ' and enter TAB."

index:	##	Create the inverted index from the movies dataset.
##		Note: This has been done already and the corresponding output file is already available.
	python3 inverted_index.py -o $(PRECOMP_II) $(DOCS)

help-index:
	@echo "About 'make index':"
	@echo "	Uses:		inverted_index.py"
	@echo "	Files read:	$(DOCS)"
	@echo "	Files produced:	$(PRECOMP_II)"
	@echo "	~Time: 		< 1 min (for 44MB file)"
	@echo "For more usage information about 'inverted_index.py', call it with the '-h' flag."
	@echo "For more background information (in particular file formats), look at the section 'Creating an Inverted Index' in the README.md."

query:	##	Query the precomputed invertex index of the movies dataset.
	python3 query.py $(PRECOMP_II)

help-query:
	@echo "About 'make query':"
	@echo "	Uses:		query.py"
	@echo "	Files read: 	$(PRECOMP_II)"
	@echo "	Files produced:	None"
	@echo "	~Time: 		a few seconds to load the inverted index (~89MB)"
	@echo "For more usage information about 'query.py', call it with the '-h' flag."
	@echo "For more background information (in particular file formats), look at the section 'Keyword search on the Inverted Index' in the README.md."

evaluate:##	Run an evaluation on the precomputed inverted index of the movies dataset and show results
##		in the console.
##		Note: The produced file is already available and a better representation of the evaluation
##		is available through the webapp.
	python3 evaluate.py $(PRECOMP_II) $(BENCHMARK) -o $(PRECOMP_EVAL)

help-evaluate:
	@echo "About 'make evaluate':"
	@echo "	Uses:		evaluate.py"
	@echo "	Files read: 	$(PRECOMP_II), $(BENCHMARK)"
	@echo "	Files produced:	$(PRECOMP_EVAL)"
	@echo "	~Time: 		a few seconds to load the ii (~89MB) plus < 1 sec per query for most queries."
	@echo "For more usage information about 'evaluate.py', call it with the '-h' flag."
	@echo "For more background information (in particular file formats), look at the section 'Evaluating the Inverted Index' in the README.md."

webapp:	##	Build a webapp that contains an evaluation of the movies benchmark.
	@echo "Webapp is available at '<host>:<port>/www', where <host> is the local computer address and <port> is the port you mapped to the container port."
	python3 -m http.server 9999

help-webapp:
	@echo "About 'make webapp':"
	@echo "	Calls:		python3 -m http.server 9999"
	@echo "	Files needed: 	$(DOCS), $(PRECOMP_EVAL)"
	@echo "	Files produced:	None"
	@echo "	~Time: 		instant"
	@echo "Webapp will be available at '<host>:<port>/www', where <host> is the local computer address and <port> is the port you mapped to the container port."
	@echo "For more background information (in particular file formats), look at the section 'Building the webapp' in the README.md."

check:	#	Test and run checkstyle.
	$(TEST_CMD) *.py
	$(CHECKSTYLE_CMD) *.py

clean:	#	Remove auto-generated python files (pycache and .pyc files).
	rm -f *.pyc www/*.pyc
	rm -rf __pycache__ www/__pycache__
