install:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && pip install -e .

test:
	pytest -q

lint:
	ruff check . || true

typecheck:
	mypy src || true

run-example:
	ultradevice simulate --scenario examples/scenarios/day_walk.json --out outputs/day_walk.csv
	ultradevice plot --csv outputs/day_walk.csv --out outputs/day_walk.png
