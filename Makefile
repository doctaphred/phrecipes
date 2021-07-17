build: test lint

lint:
	flake8

test:
	python3 -m doctest -o ELLIPSIS *.py *.rst *.md xxx/*.*
