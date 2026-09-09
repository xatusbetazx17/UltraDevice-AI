.PHONY: install test lint run-example demo build
PYTHON ?= python

install:
	$(PYTHON) -m pip install -e '.[dev,plot]'

test:
	$(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) -m ruff check src tests scripts firmware

run-example:
	ultradevice simulate-physics --scenario examples/scenarios/day_walk.json --out outputs/day_walk.csv
	ultradevice report --csv outputs/day_walk.csv --out outputs/day_walk.md
	ultradevice plot --csv outputs/day_walk.csv --out outputs/day_walk.png

demo:
	ultradevice demo --seconds 95

build:
	$(PYTHON) -m build
