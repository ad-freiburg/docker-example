TEST_CMD = python3 -m doctest
CHECKSTYLE_CMD = flake8

help: Makefile
	@echo
	@echo "Please use 'make <target>', where <target> is one of the following:"
	@sed -n 's/^## //gp' $<
	@echo
	@echo "Take a look at the README file for more information."
	@echo

## all		Compile, test and run checkstyle.
all: compile test checkstyle

## compile		Compile files.
compile:
	@echo "Nothing to compile for Python"

## test		Run doctests.
test:
	$(TEST_CMD) *.py

## checkstyle	Run checkstyle using flake8.
checkstyle:
	$(CHECKSTYLE_CMD) *.py

## clean		Remove auto-generated files.
clean:
	rm -f *.pyc
	rm -rf __pycache__
